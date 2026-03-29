from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


SUPPORTED_OUTPUT_FORMATS = ("mp3", "wav", "aac", "flac", "ogg", "m4a")


@dataclass(slots=True)
class ConversionOptions:
    output_format: str = "mp3"
    bitrate_kbps: int = 256
    sample_rate_hz: int = 44100
    channels: int = 2

    def validate(self) -> None:
        if self.output_format not in SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(f"Formato não suportado: {self.output_format}")
        if self.bitrate_kbps <= 0:
            raise ValueError("Bitrate deve ser maior que zero.")
        if self.sample_rate_hz <= 0:
            raise ValueError("Sample rate deve ser maior que zero.")
        if self.channels not in (1, 2):
            raise ValueError("Channels deve ser 1 ou 2.")


@dataclass(slots=True)
class TrimOptions:
    start_seconds: float
    end_seconds: float

    def validate(self) -> None:
        if self.start_seconds < 0:
            raise ValueError("O início não pode ser negativo.")
        if self.end_seconds <= self.start_seconds:
            raise ValueError("O tempo final deve ser maior que o inicial.")


@dataclass(slots=True)
class MediaMetadata:
    path: Path
    format_name: str = ""
    duration_seconds: float = 0.0
    size_bytes: int = 0
    bit_rate: Optional[int] = None
    sample_rate_hz: Optional[int] = None
    channels: Optional[int] = None
    codec_name: str = ""

    @property
    def file_name(self) -> str:
        return self.path.name
