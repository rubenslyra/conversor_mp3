from __future__ import annotations

from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".opus"}
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS


def ensure_file_exists(file_path: str | Path) -> Path:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if not path.is_file():
        raise ValueError(f"Caminho inválido, esperado arquivo: {path}")
    return path


def ensure_media_file(file_path: str | Path) -> Path:
    path = ensure_file_exists(file_path)
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        raise ValueError(
            f"Extensão não suportada: {path.suffix}. "
            f"Use um arquivo de mídia compatível."
        )
    return path


def ensure_parent_dir(file_path: str | Path) -> Path:
    path = Path(file_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
