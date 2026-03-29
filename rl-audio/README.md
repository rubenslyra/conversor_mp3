# RL Audio Refactored

Projeto desktop em Python para conversão e edição simples de áudio usando **FFmpeg** e **FFprobe**, com interface em **CustomTkinter**.

## O que mudou nesta versão
- remoção de `pydantic` da aplicação desktop
- uso de `dataclasses` no core
- parser amigável para tempo no formato `mm:ss` ou `mm:ss:ms`
- validações centralizadas
- separação clara entre `core` e `ui`
- execução em background para evitar travamento da interface

## Requisitos
- Python 3.11+
- FFmpeg e FFprobe instalados e disponíveis no PATH

## Instalação
### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m rlaudio
```

## Formatos suportados
- mp3
- wav
- aac
- flac
- ogg
- m4a

## Entradas de tempo
Os campos de corte aceitam:
- `mm:ss`
- `mm:ss:ms`

Exemplos:
- `00:30`
- `01:45`
- `02:15:500`

## Estrutura
```text
src/
  rlaudio/
    __main__.py
    app.py
    core/
      models.py
      ffmpeg_service.py
      time_parser.py
      validators.py
    ui/
      main_window.py
```

## Observações
- o app usa chamadas `subprocess` para o FFmpeg
- o app desktop não depende de FastAPI, Celery ou banco
- a arquitetura já deixa espaço para uma API futura
