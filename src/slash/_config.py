from dataclasses import dataclass


@dataclass
class Config:
    # Server
    host: str = "127.0.0.1"
    """Hostname on which to serve the web server."""
    port: int = 8080
    """Port on which to serve the web server."""

    # Upload
    enable_upload: bool = False
    """Flag to enable file upload."""
    max_upload_size: int = 10_000_000  # 10 MB
    """Maximum file size for uploaded files in bytes."""
