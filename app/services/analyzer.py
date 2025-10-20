import re
from collections import Counter
from hashlib import sha256
from typing import Dict, Any

_ALNUM_RE = re.compile(r"[A-Za-z0-9]")

def _normalize_for_palindrome(s: str) -> str:
    # Keep only alphanumeric characters, lowercase. 
    # This makes "A man, a plan, a canal: Panama" recognized as palindrome.
    return "".join(ch.lower() for ch in s if ch.isalnum())

def compute_properties(value: str) -> Dict[str, Any]:
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    length = len(value)
    normalized = _normalize_for_palindrome(value)
    is_pal = normalized == normalized[::-1]
    unique_chars = len(set(value))
    word_count = len(value.split())
    h = sha256(value.encode("utf-8")).hexdigest()
    freq_map = dict(Counter(value))
    return {
        "length": length,
        "is_palindrome": is_pal,
        "unique_characters": unique_chars,
        "word_count": word_count,
        "sha256_hash": h,
        "character_frequency_map": freq_map,
    }
