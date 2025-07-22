from dataclasses import dataclass


@dataclass
class Config:
    # Server
    host: str = "127.0.0.1"
    port: int = 8080

    # Upload
    enable_upload: bool = False
    max_upload_size: int = 10_000_000  # 10 MB

    # Storage
    enable_storage: bool = False
