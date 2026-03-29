
from rl_video_downloader.core.validators import is_valid_url


def test_valid_http_url() -> None:
    assert is_valid_url("https://example.com/video") is True


def test_invalid_url() -> None:
    assert is_valid_url("not-a-url") is False
