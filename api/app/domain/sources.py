"""Deep-linking into a Source at its exact position.

A Recommendation without a Source does not exist, and a Source cites the exact
position within itself. These helpers turn a stored ``position_seconds`` into a
clickable link and a human-readable label. We use the W3C Media Fragments syntax
(``#t=<seconds>``), which the major podcast and video players honour.
"""

from __future__ import annotations


def format_timestamp(position_seconds: int) -> str:
    """Render a position as ``m:ss`` or ``h:mm:ss`` for display.

    >>> format_timestamp(75)
    '1:15'
    >>> format_timestamp(3725)
    '1:02:05'
    """
    if position_seconds < 0:
        raise ValueError("position_seconds must not be negative")
    hours, remainder = divmod(position_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def source_deep_link(url: str, position_seconds: int) -> str:
    """Return ``url`` with a media fragment pointing at ``position_seconds``.

    Any existing fragment is replaced so re-linking is idempotent.

    >>> source_deep_link("https://ex.com/ep/1", 90)
    'https://ex.com/ep/1#t=90'
    """
    if position_seconds < 0:
        raise ValueError("position_seconds must not be negative")
    base = url.split("#", 1)[0]
    return f"{base}#t={position_seconds}"
