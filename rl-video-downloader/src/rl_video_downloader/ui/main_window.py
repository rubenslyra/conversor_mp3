
from __future__ import annotations

import threading
from pathlib import Path
import tkinter.filedialog as fd
import tkinter.messagebox as mb

import customtkinter as ctk

from ..core.downloader import VideoDownloader
from ..core.models import DownloadOptions
from ..core.validators import is_valid_url


class RLVideoDownloaderApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("RL Video Downloader")
        self.geometry("900x680")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.output_dir = Path.cwd() / "downloads"
        self.output_dir.mkdir(exist_ok=True)

        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        title = ctk.CTkLabel(
            self,
            text="RL Video Downloader",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        note = ctk.CTkLabel(
            self,
            text="Baixe apenas conteúdo público, próprio ou com permissão.",
            font=ctk.CTkFont(size=13),
        )
        note.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        url_frame = ctk.CTkFrame(self)
        url_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="Cole a URL do vídeo aqui",
            height=40,
        )
        self.url_entry.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        info_button = ctk.CTkButton(url_frame, text="Buscar informações", command=self.fetch_info)
        info_button.grid(row=0, column=1, padx=(0, 12), pady=12)

        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        options_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(options_frame, text="Pasta de saída:").grid(row=0, column=0, padx=12, pady=12, sticky="w")
        self.output_entry = ctk.CTkEntry(options_frame, height=36)
        self.output_entry.insert(0, str(self.output_dir))
        self.output_entry.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        browse_button = ctk.CTkButton(options_frame, text="Escolher", width=120, command=self.choose_output_dir)
        browse_button.grid(row=0, column=2, padx=(0, 12), pady=12)

        self.audio_only_var = ctk.BooleanVar(value=False)
        self.audio_only_switch = ctk.CTkSwitch(
            options_frame,
            text="Extrair somente áudio (MP3)",
            variable=self.audio_only_var,
        )
        self.audio_only_switch.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="w")

        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=4, column=0, padx=20, pady=10, sticky="nsew")
        action_frame.grid_columnconfigure(0, weight=1)
        action_frame.grid_rowconfigure(1, weight=1)

        self.info_box = ctk.CTkTextbox(action_frame, height=160)
        self.info_box.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.info_box.insert("1.0", "Informações do vídeo aparecerão aqui.")
        self.info_box.configure(state="disabled")

        log_header = ctk.CTkFrame(action_frame)
        log_header.grid(row=1, column=0, padx=12, pady=(0, 0), sticky="ew")
        ctk.CTkLabel(log_header, text="Logs").pack(side="left", padx=4, pady=4)

        self.log_box = ctk.CTkTextbox(action_frame)
        self.log_box.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="nsew")

        button_row = ctk.CTkFrame(self)
        button_row.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.download_button = ctk.CTkButton(button_row, text="Baixar agora", height=42, command=self.download)
        self.download_button.pack(side="left", padx=12, pady=12)

        clear_button = ctk.CTkButton(button_row, text="Limpar logs", height=42, command=self.clear_logs)
        clear_button.pack(side="left", padx=0, pady=12)

    def choose_output_dir(self) -> None:
        selected = fd.askdirectory(initialdir=self.output_entry.get() or str(Path.cwd()))
        if selected:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, selected)

    def fetch_info(self) -> None:
        url = self.url_entry.get().strip()
        if not is_valid_url(url):
            mb.showerror("URL inválida", "Informe uma URL válida começando com http:// ou https://")
            return

        self._run_in_thread(self._fetch_info_worker, url)

    def _fetch_info_worker(self, url: str) -> None:
        try:
            downloader = VideoDownloader(logger=self.append_log)
            info = downloader.get_info(url)
            lines = [
                f"Título: {info.title}",
                f"Duração (s): {info.duration}",
                f"Canal/Uploader: {info.uploader}",
                f"Extractor: {info.extractor}",
                f"Página: {info.webpage_url}",
                f"Thumbnail: {info.thumbnail}",
            ]
            self.after(0, lambda: self._set_info("\n".join(lines)))
            self.append_log("Metadados carregados com sucesso.")
        except Exception as exc:
            self.after(0, lambda: mb.showerror("Erro ao consultar URL", str(exc)))
            self.append_log(f"Erro: {exc}")

    def download(self) -> None:
        url = self.url_entry.get().strip()
        if not is_valid_url(url):
            mb.showerror("URL inválida", "Informe uma URL válida começando com http:// ou https://")
            return

        output_dir = Path(self.output_entry.get().strip() or "downloads")
        request = DownloadOptions(
            url=url,
            output_dir=output_dir,
            audio_only=self.audio_only_var.get(),
            audio_format="mp3",
        )
        self._run_in_thread(self._download_worker, request)

    def _download_worker(self, request: DownloadOptions) -> None:
        try:
            self.after(0, lambda: self.download_button.configure(state="disabled"))
            downloader = VideoDownloader(logger=self.append_log)
            saved_path = downloader.download(request)
            self.after(0, lambda: mb.showinfo("Concluído", f"Arquivo salvo em:\n{saved_path}"))
        except Exception as exc:
            self.after(0, lambda: mb.showerror("Erro no download", str(exc)))
            self.append_log(f"Erro: {exc}")
        finally:
            self.after(0, lambda: self.download_button.configure(state="normal"))

    def _set_info(self, text: str) -> None:
        self.info_box.configure(state="normal")
        self.info_box.delete("1.0", "end")
        self.info_box.insert("1.0", text)
        self.info_box.configure(state="disabled")

    def append_log(self, message: str) -> None:
        def _append() -> None:
            self.log_box.insert("end", f"{message}\n")
            self.log_box.see("end")
        self.after(0, _append)

    def clear_logs(self) -> None:
        self.log_box.delete("1.0", "end")

    def _run_in_thread(self, target, *args) -> None:
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
