from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Optional

from .models import ConversionOptions, MediaMetadata, TrimOptions
from .validators import ensure_media_file, ensure_parent_dir


ProgressCallback = Optional[Callable[[float, str], None]]


class FFmpegService:
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe") -> None:
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def check_binaries(self) -> None:
        if shutil.which(self.ffmpeg_path) is None:
            raise FileNotFoundError("FFmpeg não encontrado no PATH.")
        if shutil.which(self.ffprobe_path) is None:
            raise FileNotFoundError("FFprobe não encontrado no PATH.")

    def read_metadata(self, input_file: str | Path) -> MediaMetadata:
        self.check_binaries()
        source = ensure_media_file(input_file)

        cmd = [
            self.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=format_name,duration,size,bit_rate:stream=codec_name,sample_rate,channels",
            "-of", "json",
            str(source),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout or "{}")

        fmt = data.get("format", {})
        streams = data.get("streams", [])
        audio_stream = next((s for s in streams if s.get("channels") is not None), streams[0] if streams else {})

        return MediaMetadata(
            path=source,
            format_name=fmt.get("format_name", ""),
            duration_seconds=float(fmt.get("duration", 0) or 0),
            size_bytes=int(fmt.get("size", 0) or 0),
            bit_rate=int(fmt["bit_rate"]) if fmt.get("bit_rate") else None,
            sample_rate_hz=int(audio_stream["sample_rate"]) if audio_stream.get("sample_rate") else None,
            channels=int(audio_stream["channels"]) if audio_stream.get("channels") else None,
            codec_name=audio_stream.get("codec_name", ""),
        )

    def convert_to_audio(
        self,
        input_file: str | Path,
        output_file: str | Path,
        options: ConversionOptions,
        progress_callback: ProgressCallback = None,
    ) -> Path:
        self.check_binaries()
        options.validate()
        source = ensure_media_file(input_file)
        target = ensure_parent_dir(output_file)

        metadata = self.read_metadata(source)
        total_duration = metadata.duration_seconds or 0.0

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(source),
            "-vn",
            "-acodec", self._codec_for(options.output_format),
            "-ar", str(options.sample_rate_hz),
            "-ac", str(options.channels),
        ]

        if options.output_format != "wav":
            cmd.extend(["-b:a", f"{options.bitrate_kbps}k"])

        cmd.extend([
            "-progress", "pipe:1",
            "-nostats",
            str(target),
        ])

        self._run_ffmpeg_with_progress(cmd, total_duration, progress_callback)
        return target

    def trim_audio(
        self,
        input_file: str | Path,
        output_file: str | Path,
        options: TrimOptions,
        progress_callback: ProgressCallback = None,
    ) -> Path:
        self.check_binaries()
        options.validate()
        source = ensure_media_file(input_file)
        target = ensure_parent_dir(output_file)

        clip_duration = max(options.end_seconds - options.start_seconds, 0.001)

        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", str(source),
            "-ss", f"{options.start_seconds:.3f}",
            "-to", f"{options.end_seconds:.3f}",
            "-c:a", "copy",
            "-progress", "pipe:1",
            "-nostats",
            str(target),
        ]

        try:
            self._run_ffmpeg_with_progress(cmd, clip_duration, progress_callback)
        except subprocess.CalledProcessError:
            # Fallback para re-encode quando copy não for compatível.
            fallback = [
                self.ffmpeg_path,
                "-y",
                "-i", str(source),
                "-ss", f"{options.start_seconds:.3f}",
                "-to", f"{options.end_seconds:.3f}",
                "-c:a", "libmp3lame" if target.suffix.lower() == ".mp3" else "aac",
                "-progress", "pipe:1",
                "-nostats",
                str(target),
            ]
            self._run_ffmpeg_with_progress(fallback, clip_duration, progress_callback)

        return target

    def _run_ffmpeg_with_progress(
        self,
        cmd: list[str],
        total_duration: float,
        progress_callback: ProgressCallback,
    ) -> None:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True,
        )

        stderr_lines: list[str] = []
        current_out_time = 0.0

        assert process.stdout is not None
        assert process.stderr is not None

        for line in process.stdout:
            text = line.strip()
            if not text:
                continue

            if "=" in text:
                key, value = text.split("=", 1)

                if key == "out_time_ms":
                    try:
                        current_out_time = int(value) / 1_000_000.0
                    except ValueError:
                        current_out_time = 0.0
                elif key == "progress" and progress_callback:
                    if value == "continue":
                        percent = 0.0
                        if total_duration > 0:
                            percent = min((current_out_time / total_duration) * 100.0, 99.0)
                        progress_callback(percent, f"{percent:.0f}%")
                    elif value == "end":
                        progress_callback(100.0, "100%")

        for err_line in process.stderr:
            stderr_lines.append(err_line)

        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code=return_code,
                cmd=cmd,
                output="".join(stderr_lines[-20:]),
            )

    @staticmethod
    def _codec_for(output_format: str) -> str:
        mapping = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "aac": "aac",
            "flac": "flac",
            "ogg": "libvorbis",
            "m4a": "aac",
        }
        try:
            return mapping[output_format]
        except KeyError as exc:
            raise ValueError(f"Formato não suportado: {output_format}") from exc
