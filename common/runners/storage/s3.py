"""S3-compatible sink. Supports AWS S3, MinIO, DigitalOcean Spaces, Cloudflare R2.

Pattern ported (and trimmed) from /Users/mikefluff/Documents/figma/workers/python/object_storage_adapter.py.
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
