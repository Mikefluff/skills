"""Storage sinks — local FS always, optional S3-compatible."""

from .local import write_local
from .s3 import s3_configured, write_s3

__all__ = ["s3_configured", "write_local", "write_s3"]
