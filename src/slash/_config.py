from dataclasses import dataclass


@dataclass
class Config:
    # Upload
    enable_upload: bool = False
    max_upload_size: int = 10_000_000  # 10 MB

    # Storage
    enable_storage: bool = False
