# RL Video Downloader

Aplicação desktop em Python para baixar **vídeos públicos ou com permissão** a partir de uma URL e, opcionalmente, extrair áudio com FFmpeg.

## Recursos
- Interface gráfica com CustomTkinter
- Consulta de metadados do vídeo
- Download de vídeo
- Extração de áudio em MP3
- Seleção de pasta de saída
- Logs em tempo real
- Worker em thread para não travar a interface

## Aviso importante
Use esta aplicação apenas para baixar conteúdo:
- público,
- de sua propriedade, ou
- para o qual você tenha permissão.

Ela **não foi projetada para burlar DRM, paywall, autenticação indevida ou outras proteções**.

## Requisitos
- Python 3.11+
- `ffmpeg` e `ffprobe` no PATH do sistema
- Internet para acessar a URL do vídeo

## Instalação rápida no Windows
```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m rl_video_downloader
```

## Instalação rápida via BAT
```cmd
setup.bat
```

## Estrutura
```text
src/rl_video_downloader/
  __main__.py
  app.py
  core/
    downloader.py
    models.py
    validators.py
  ui/
    main_window.py
```
