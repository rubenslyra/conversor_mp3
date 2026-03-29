
from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

import yt_dlp

from .models import DownloadOptions, VideoInfo


ProgressCallback = Optional[Callable[[str], None]]


class VideoDownloader:
    def __init__(self, logger: ProgressCallback = None) -> None:
        self._logger = logger

    def _log(self, message: str) -> None:
        if self._logger:
            self._logger(message)

    def get_info(self, url: str) -> VideoInfo:
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }
        self._log("Consultando metadados...")
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
        return VideoInfo(
            title=info.get("title", "Sem título"),
            duration=info.get("duration"),
            uploader=info.get("uploader"),
            thumbnail=info.get("thumbnail"),
            webpage_url=info.get("webpage_url"),
            extractor=info.get("extractor"),
        )

    def download(self, request: DownloadOptions) -> Path:
        request.output_dir.mkdir(parents=True, exist_ok=True)

        def progress_hook(data: dict) -> None:
            status = data.get("status")
            if status == "downloading":
                downloaded = data.get("_downloaded_bytes_str", "?")
                total = data.get("_total_bytes_str") or data.get("_total_bytes_estimate_str") or "?"
                speed = data.get("_speed_str", "?")
                eta = data.get("_eta_str", "?")
                self._log(f"Baixando: {downloaded}/{total} | velocidade {speed} | ETA {eta}")
            elif status == "finished":
                self._log("Download concluído. Processando arquivo final...")

        base_options = {
            "outtmpl": str(request.output_dir / "%(title).180s.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [progress_hook],
        }

        if request.audio_only:
            options = {
                **base_options,
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": request.audio_format,
                        "preferredquality": "192",
                    }
                ],
            }
        else:
            options = {
                **base_options,
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
            }

        self._log("Iniciando download...")
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(request.url, download=True)
            prepared = Path(ydl.prepare_filename(info))

        if request.audio_only:
            final_path = prepared.with_suffix(f".{request.audio_format}")
        else:
            if prepared.suffix.lower() != ".mp4":
                candidate = prepared.with_suffix(".mp4")
                final_path = candidate if candidate.exists() else prepared
            else:
                final_path = prepared

        self._log(f"Arquivo salvo em: {final_path}")
        return final_path
