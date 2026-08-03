"""S3-compatible sink. Supports AWS S3, MinIO, DigitalOcean Spaces, Cloudflare R2.

Pattern ported (and trimmed) from the author's earlier object-storage adapter.
"""

from __future__ import annotations

import os
import re
from typing import Any

_REQUIRED_ENV = ("S3_BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY")
_SAFE_KEY_RE = re.compile(r"[^A-Za-z0-9._/-]+")


def s3_configured() -> bool:
    return all(os.environ.get(k) for k in _REQUIRED_ENV)


def _safe_key(raw: str) -> str:
    return _SAFE_KEY_RE.sub("-", raw).strip("-/") or "asset"


def _client() -> Any:
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError(
            "S3 upload requested but boto3 is not installed. "
            "Run: pip install -r common/runners/requirements.txt"
        ) from exc
    kwargs: dict[str, Any] = {
        "aws_access_key_id": os.environ["S3_ACCESS_KEY"],
        "aws_secret_access_key": os.environ["S3_SECRET_KEY"],
    }
    endpoint = os.environ.get("S3_ENDPOINT")
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    region = os.environ.get("S3_REGION")
    if region:
        kwargs["region_name"] = region
    return boto3.client("s3", **kwargs)


def presigned_url(key: str, *, ttl: int = 3600) -> str:
    """Time-limited GET URL for an object already in the bucket.

    Used by the publishing layer: Instagram and Threads will not accept raw
    bytes — they fetch the media themselves from a URL you hand them. A
    presigned link is the right shape for that and a public-read ACL is not:
    the bucket stays private, the link dies on its own, and nothing generated
    here is left permanently readable by whoever finds the URL.
    """
    if not s3_configured():
        raise RuntimeError("S3 not configured (S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY missing)")
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ.get("S3_PATH_PREFIX", "").strip("/")
    full_key = f"{prefix}/{_safe_key(key)}" if prefix else _safe_key(key)
    return _client().generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": full_key}, ExpiresIn=ttl
    )


def stage_for_fetch(path, key: str, content_type: str, *, ttl: int = 3600) -> str:
    """Upload a local file and return a URL a platform can fetch it from.

    One call because the two halves are never useful apart, and because
    forgetting the presign step would silently hand Meta a URL that 403s.
    """
    from pathlib import Path

    data = Path(path).read_bytes()
    write_s3(data, key, content_type)
    return presigned_url(key, ttl=ttl)


def write_s3(content: bytes, key: str, content_type: str) -> str:
    """Upload to the configured bucket. Returns a URL.

    URL format depends on endpoint:
    - MinIO: <endpoint>/<bucket>/<key>
    - DO Spaces: <endpoint>/<bucket>/<key>
    - AWS S3: https://<bucket>.s3.<region>.amazonaws.com/<key>
    - R2: <endpoint>/<bucket>/<key>
    """
    if not s3_configured():
        raise RuntimeError("S3 not configured (S3_BUCKET / S3_ACCESS_KEY / S3_SECRET_KEY missing)")
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ.get("S3_PATH_PREFIX", "").strip("/")
    full_key = f"{prefix}/{_safe_key(key)}" if prefix else _safe_key(key)

    client = _client()
    client.put_object(Bucket=bucket, Key=full_key, Body=content, ContentType=content_type)

    endpoint = os.environ.get("S3_ENDPOINT", "").rstrip("/")
    region = os.environ.get("S3_REGION", "us-east-1")
    if endpoint:
        return f"{endpoint}/{bucket}/{full_key}"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{full_key}"
