from __future__ import annotations

import re


TIME_PATTERN = re.compile(r"^(?P<mm>\d{1,3}):(?P<ss>\d{1,2})(?::(?P<ms>\d{1,3}))?$")


def parse_time_input(value: str) -> float:
    """
    Aceita:
    - mm:ss
    - mm:ss:ms

    Exemplos:
    - 01:30 -> 90.0
    - 02:15:500 -> 135.5
    - 00:09:250 -> 9.25
    """
    if value is None:
        raise ValueError("Tempo não informado.")

    normalized = value.strip()
    if not normalized:
        raise ValueError("Tempo não informado.")

    match = TIME_PATTERN.fullmatch(normalized)
    if not match:
        raise ValueError("Formato inválido. Use mm:ss ou mm:ss:ms.")

    minutes = int(match.group("mm"))
    seconds = int(match.group("ss"))
    milliseconds = int(match.group("ms")) if match.group("ms") else 0

    if not 0 <= seconds <= 59:
        raise ValueError("Os segundos devem estar entre 00 e 59.")
    if not 0 <= milliseconds <= 999:
        raise ValueError("Os milissegundos devem estar entre 000 e 999.")

    return (minutes * 60) + seconds + (milliseconds / 1000.0)


def format_seconds(total_seconds: float) -> str:
    if total_seconds < 0:
        raise ValueError("Tempo não pode ser negativo.")

    whole_seconds = int(total_seconds)
    milliseconds = int(round((total_seconds - whole_seconds) * 1000))

    if milliseconds == 1000:
        whole_seconds += 1
        milliseconds = 0

    minutes = whole_seconds // 60
    seconds = whole_seconds % 60

    if milliseconds:
        return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
    return f"{minutes:02d}:{seconds:02d}"
