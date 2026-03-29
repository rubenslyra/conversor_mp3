<h1>
  <img src="rl-audio/src/rlaudio/assets/logo.png" alt="Logo do projeto" width="34" valign="middle" />
  RL Audio + RL Video Downloader
</h1>

Projeto desenvolvido como parte dos meus estudos em Engenharia de Software, com foco em  **processamento de mídia, automação com Python e arquitetura de aplicações reais** .

A ideia foi construir duas aplicações complementares:

* 🎵 **RL Audio** → conversor e editor de áudio (corte, trim, formatos)
* 🎬 **RL Video Downloader** → download de vídeos por URL (com extração opcional de áudio)

Ambos foram desenvolvidos com uma abordagem prática, pensando em evoluir para um produto mais robusto no futuro.

---

## 🚀 Funcionalidades

### 🎧 RL Audio

* Conversão de vídeo → áudio (MP3, WAV, FLAC, AAC, etc.)
* Corte de áudio usando formato amigável (`mm:ss` ou `mm:ss:ms`)
* Integração com FFmpeg e FFprobe
* Interface desktop com CustomTkinter
* Execução em background (sem travar UI)

### 🎬 RL Video Downloader

* Download de vídeos via URL
* Extração de áudio (MP3)
* Exibição de metadados (título, duração, etc.)
* Logs em tempo real
* Interface simples e funcional

---

## 🧠 Motivação

Esse projeto nasceu da necessidade de entender, na prática:

* Como manipular mídia com ferramentas profissionais
* Como estruturar aplicações Python além de scripts simples
* Como separar responsabilidades (UI, core, serviços)
* Como preparar algo que possa evoluir para uma API futuramente

---

## 🛠️ Tecnologias utilizadas

* Python 3.12+
* CustomTkinter (interface)
* FFmpeg
* FFprobe
* yt-dlp
* MoviePy
* threading (execução assíncrona)

---

## 🔗 Referências principais

* FFmpeg
* FFprobe
* MoviePy
* OpenAI Codex IDE

---

## 📦 Estrutura do projeto

```bash
conversor_mp3/
│
├── rl-audio/
│   └── src/
│
├── rl-video-downloader/
│   └── src/
│
└── .venv/
```

---

## ⚙️ Como executar

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente

```bash
# Windows
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r rl-audio/requirements.txt
pip install -r rl-video-downloader/requirements.txt
```

### 4. Rodar aplicações

#### RL Audio

```bash
cd rl-audio
set PYTHONPATH=src
python -m rlaudio
```

#### RL Video Downloader

```bash
cd rl-video-downloader
set PYTHONPATH=src
python -m rl_video_downloader
```

---

## ⚠️ Observações importantes

* É necessário ter **FFmpeg e FFprobe instalados no sistema**
* O downloader deve ser utilizado apenas para:
  * conteúdo público
  * conteúdo próprio
  * conteúdo com permissão

---

## 📈 Próximos passos (roadmap)

* [X] Drag & Drop de arquivos
* [X] Visualização de waveform
* [X] Histórico de conversões/downloads
* [X] Backend com FastAPI
* [X] Processamento assíncrono com filas (Celery)
* [X] Deploy como aplicação distribuída

---

## 👨‍💻 Autor

**Rubinho Lyra**
Projeto acadêmico + portfólio pessoal

---

## 💡 Considerações finais

Esse projeto foi importante para consolidar conceitos de:

* arquitetura de software
* manipulação de mídia
* UX em aplicações desktop
* integração com ferramentas externas (FFmpeg)

E também mostrou claramente os desafios de sair do nível de script para aplicações reais.
