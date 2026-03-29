python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m rl_video_downloader
