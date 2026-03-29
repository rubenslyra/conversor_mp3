
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class VideoInfo:
    title: str
    duration: Optional[int]
    uploader: Optional[str]
    thumbnail: Optional[str]
    webpage_url: Optional[str]
    extractor: Optional[str]


@dataclass(slots=True)
class DownloadOptions:
    url: str
    output_dir: Path
    audio_only: bool = False
    audio_format: str = "mp3"
