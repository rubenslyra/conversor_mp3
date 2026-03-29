from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from ..core.ffmpeg_service import FFmpegService
from ..core.models import ConversionOptions, SUPPORTED_OUTPUT_FORMATS, TrimOptions
from ..core.time_parser import format_seconds, parse_time_input


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RLAudioApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("RL Audio Refactored")
        self.geometry("980x700")
        self.minsize(900, 640)

        self.service = FFmpegService()
        self.selected_file: Path | None = None
        self.logo_image = self._load_logo_image()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()
        self._build_status_bar()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_columnconfigure(1, weight=1)

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")

        if self.logo_image is not None:
            logo_label = ctk.CTkLabel(title_row, text="", image=self.logo_image)
            logo_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

        title = ctk.CTkLabel(
            title_row,
            text="RL Audio — Conversor e Editor",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title.grid(row=0, column=1, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Conversão com FFmpeg, leitura com FFprobe e corte por mm:ss ou mm:ss:ms",
            font=ctk.CTkFont(size=13),
            text_color="gray75",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 18), sticky="w")

    def _load_logo_image(self) -> ctk.CTkImage | None:
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if not logo_path.exists():
            return None
        return ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(30, 30))

    def _build_tabs(self) -> None:
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.tabs.add("Converter")
        self.tabs.add("Cortar")

        self._build_convert_tab(self.tabs.tab("Converter"))
        self._build_trim_tab(self.tabs.tab("Cortar"))

    def _build_status_bar(self) -> None:
        wrapper = ctk.CTkFrame(self)
        wrapper.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        wrapper.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(wrapper, text="Pronto.", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))

        self.progress_bar = ctk.CTkProgressBar(wrapper)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        self.progress_bar.set(0)

    def _build_convert_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        file_frame = ctk.CTkFrame(parent)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=12)
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(file_frame, text="Arquivo de entrada").grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.input_entry = ctk.CTkEntry(file_frame, placeholder_text="Selecione um vídeo ou áudio")
        self.input_entry.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        browse_btn = ctk.CTkButton(file_frame, text="Escolher arquivo", command=self._select_input_file)
        browse_btn.grid(row=0, column=2, padx=12, pady=12)

        settings_frame = ctk.CTkFrame(parent)
        settings_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=12)
        settings_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(settings_frame, text="Formato").grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.format_var = tk.StringVar(value="mp3")
        self.format_menu = ctk.CTkOptionMenu(settings_frame, variable=self.format_var, values=list(SUPPORTED_OUTPUT_FORMATS))
        self.format_menu.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Bitrate (kbps)").grid(row=1, column=0, padx=12, pady=12, sticky="w")
        self.bitrate_entry = ctk.CTkEntry(settings_frame)
        self.bitrate_entry.insert(0, "256")
        self.bitrate_entry.grid(row=1, column=1, padx=12, pady=12, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Sample rate (Hz)").grid(row=2, column=0, padx=12, pady=12, sticky="w")
        self.sample_rate_entry = ctk.CTkEntry(settings_frame)
        self.sample_rate_entry.insert(0, "44100")
        self.sample_rate_entry.grid(row=2, column=1, padx=12, pady=12, sticky="ew")

        ctk.CTkLabel(settings_frame, text="Canais").grid(row=3, column=0, padx=12, pady=12, sticky="w")
        self.channels_var = tk.StringVar(value="2")
        self.channels_menu = ctk.CTkOptionMenu(settings_frame, variable=self.channels_var, values=["1", "2"])
        self.channels_menu.grid(row=3, column=1, padx=12, pady=12, sticky="ew")

        convert_btn = ctk.CTkButton(settings_frame, text="Converter", command=self._start_conversion)
        convert_btn.grid(row=4, column=0, columnspan=2, padx=12, pady=(12, 16), sticky="ew")

        meta_frame = ctk.CTkFrame(parent)
        meta_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)
        meta_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(meta_frame, text="Metadados", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, padx=12, pady=(12, 8), sticky="w"
        )

        self.metadata_box = ctk.CTkTextbox(meta_frame, height=280)
        self.metadata_box.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")
        self.metadata_box.insert("1.0", "Selecione um arquivo para visualizar os metadados.")
        self.metadata_box.configure(state="disabled")

    def _build_trim_tab(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Arquivo de entrada").grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.trim_input_entry = ctk.CTkEntry(frame, placeholder_text="Use o mesmo arquivo ou escolha outro")
        self.trim_input_entry.grid(row=0, column=1, padx=12, pady=12, sticky="ew")
        ctk.CTkButton(frame, text="Escolher arquivo", command=self._select_trim_file).grid(row=0, column=2, padx=12, pady=12)

        ctk.CTkLabel(frame, text="Início (mm:ss ou mm:ss:ms)").grid(row=1, column=0, padx=12, pady=12, sticky="w")
        self.trim_start_entry = ctk.CTkEntry(frame, placeholder_text="00:30")
        self.trim_start_entry.grid(row=1, column=1, padx=12, pady=12, sticky="ew")

        ctk.CTkLabel(frame, text="Fim (mm:ss ou mm:ss:ms)").grid(row=2, column=0, padx=12, pady=12, sticky="w")
        self.trim_end_entry = ctk.CTkEntry(frame, placeholder_text="01:45:250")
        self.trim_end_entry.grid(row=2, column=1, padx=12, pady=12, sticky="ew")

        self.trim_preview_label = ctk.CTkLabel(
            frame,
            text="Exemplo: 01:45:250 = 105.250 segundos",
            text_color="gray75",
        )
        self.trim_preview_label.grid(row=3, column=0, columnspan=3, padx=12, pady=(0, 8), sticky="w")

        ctk.CTkButton(frame, text="Validar tempos", command=self._preview_trim_times).grid(
            row=4, column=0, padx=12, pady=(6, 16), sticky="ew"
        )
        ctk.CTkButton(frame, text="Cortar áudio", command=self._start_trim).grid(
            row=4, column=1, columnspan=2, padx=12, pady=(6, 16), sticky="ew"
        )

    def _select_input_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de mídia",
            filetypes=[("Mídia", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.mp3 *.wav *.flac *.aac *.ogg *.m4a *.opus"), ("Todos", "*.*")],
        )
        if not path:
            return
        self.selected_file = Path(path)
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, path)
        self.trim_input_entry.delete(0, "end")
        self.trim_input_entry.insert(0, path)
        self._load_metadata(path)

    def _select_trim_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecionar arquivo de mídia",
            filetypes=[("Mídia", "*.mp4 *.mkv *.avi *.mov *.webm *.m4v *.mp3 *.wav *.flac *.aac *.ogg *.m4a *.opus"), ("Todos", "*.*")],
        )
        if not path:
            return
        self.trim_input_entry.delete(0, "end")
        self.trim_input_entry.insert(0, path)

    def _load_metadata(self, path: str) -> None:
        try:
            metadata = self.service.read_metadata(path)
            lines = [
                f"Arquivo: {metadata.file_name}",
                f"Formato: {metadata.format_name or '-'}",
                f"Duração: {format_seconds(metadata.duration_seconds)}",
                f"Tamanho: {metadata.size_bytes} bytes",
                f"Codec: {metadata.codec_name or '-'}",
                f"Bitrate: {metadata.bit_rate or '-'}",
                f"Sample rate: {metadata.sample_rate_hz or '-'}",
                f"Canais: {metadata.channels or '-'}",
            ]
            self._set_metadata_text("\\n".join(lines))
            self._set_status("Metadados carregados.")
        except Exception as exc:
            self._set_metadata_text(f"Não foi possível ler os metadados.\\n\\n{exc}")
            self._set_status("Falha ao carregar metadados.")

    def _set_metadata_text(self, text: str) -> None:
        self.metadata_box.configure(state="normal")
        self.metadata_box.delete("1.0", "end")
        self.metadata_box.insert("1.0", text)
        self.metadata_box.configure(state="disabled")

    def _preview_trim_times(self) -> None:
        try:
            start_seconds = parse_time_input(self.trim_start_entry.get())
            end_seconds = parse_time_input(self.trim_end_entry.get())
            if end_seconds <= start_seconds:
                raise ValueError("O tempo final deve ser maior que o inicial.")

            self.trim_preview_label.configure(
                text=(
                    f"Início: {start_seconds:.3f}s | "
                    f"Fim: {end_seconds:.3f}s | "
                    f"Duração: {end_seconds - start_seconds:.3f}s"
                )
            )
            self._set_status("Tempos validados com sucesso.")
        except Exception as exc:
            messagebox.showerror("Tempos inválidos", str(exc))
            self._set_status("Falha na validação dos tempos.")

    def _start_conversion(self) -> None:
        try:
            source_path = self.input_entry.get().strip()
            if not source_path:
                raise ValueError("Selecione um arquivo de entrada.")

            output_format = self.format_var.get()
            output_path = filedialog.asksaveasfilename(
                title="Salvar áudio convertido",
                defaultextension=f".{output_format}",
                filetypes=[(output_format.upper(), f"*.{output_format}")],
                initialfile=f"{Path(source_path).stem}.{output_format}",
            )
            if not output_path:
                return

            options = ConversionOptions(
                output_format=output_format,
                bitrate_kbps=int(self.bitrate_entry.get().strip()),
                sample_rate_hz=int(self.sample_rate_entry.get().strip()),
                channels=int(self.channels_var.get()),
            )
            options.validate()
        except Exception as exc:
            messagebox.showerror("Configuração inválida", str(exc))
            return

        self._run_background_task(
            target=lambda: self.service.convert_to_audio(
                source_path,
                output_path,
                options,
                progress_callback=self._threadsafe_progress_update,
            ),
            success_message=f"Conversão concluída:\\n{output_path}",
            busy_message="Convertendo arquivo...",
        )

    def _start_trim(self) -> None:
        try:
            source_path = self.trim_input_entry.get().strip()
            if not source_path:
                raise ValueError("Selecione um arquivo de entrada para corte.")

            start_seconds = parse_time_input(self.trim_start_entry.get())
            end_seconds = parse_time_input(self.trim_end_entry.get())

            if end_seconds <= start_seconds:
                raise ValueError("O tempo final deve ser maior que o inicial.")

            suffix = Path(source_path).suffix or ".mp3"
            output_path = filedialog.asksaveasfilename(
                title="Salvar trecho cortado",
                defaultextension=suffix,
                filetypes=[("Arquivo de áudio", f"*{suffix}")],
                initialfile=f"{Path(source_path).stem}_trim{suffix}",
            )
            if not output_path:
                return

            options = TrimOptions(start_seconds=start_seconds, end_seconds=end_seconds)
            options.validate()
        except Exception as exc:
            messagebox.showerror("Configuração inválida", str(exc))
            return

        self._run_background_task(
            target=lambda: self.service.trim_audio(
                source_path,
                output_path,
                options,
                progress_callback=self._threadsafe_progress_update,
            ),
            success_message=f"Corte concluído:\\n{output_path}",
            busy_message="Cortando áudio...",
        )

    def _run_background_task(self, target, success_message: str, busy_message: str) -> None:
        self.progress_bar.set(0)
        self._set_status(busy_message)

        def runner() -> None:
            try:
                target()
                self.after(0, lambda: self._on_task_success(success_message))
            except Exception as exc:
                self.after(0, lambda: self._on_task_error(exc))

        threading.Thread(target=runner, daemon=True).start()

    def _threadsafe_progress_update(self, percent: float, text: str) -> None:
        self.after(0, lambda: self._update_progress(percent, text))

    def _update_progress(self, percent: float, text: str) -> None:
        self.progress_bar.set(max(0.0, min(percent / 100.0, 1.0)))
        self._set_status(text)

    def _on_task_success(self, message: str) -> None:
        self.progress_bar.set(1.0)
        self._set_status("Concluído.")
        messagebox.showinfo("Sucesso", message)

    def _on_task_error(self, exc: Exception) -> None:
        self.progress_bar.set(0)
        self._set_status("Falha na operação.")
        messagebox.showerror("Erro", str(exc))

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)
