from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..schemas import StringCreate, StringResponse, StringProperties
from ..services.analyzer import compute_properties
from ..models import StringModel
from ..dependencies import get_db
from sqlalchemy import and_, or_, select

router = APIRouter()

@router.post("/strings", response_model=StringResponse, status_code=201)
def create_string(payload: StringCreate, db: Session = Depends(get_db)):
    value = payload.value
    if not isinstance(value, str):
        raise HTTPException(status_code=422, detail="value must be a string")
    if value.strip() == "":
        raise HTTPException(status_code=400, detail="value cannot be empty")

    props = compute_properties(value)
    sha = props["sha256_hash"]

    existing = db.query(StringModel).filter(StringModel.id == sha).first()
    if existing:
        raise HTTPException(status_code=409, detail="String already exists")

    entry = StringModel(
        id=sha,
        value=value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        character_frequency_map=props["character_frequency_map"],
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    response = {
        "id": entry.id,
        "value": entry.value,
        "properties": {
            "length": entry.length,
            "is_palindrome": entry.is_palindrome,
            "unique_characters": entry.unique_characters,
            "word_count": entry.word_count,
            "sha256_hash": entry.id,
            "character_frequency_map": entry.character_frequency_map,
        },
        "created_at": entry.created_at
    }
    return response

@router.get("/strings/{string_value}", response_model=StringResponse)
def get_string(string_value: str, db: Session = Depends(get_db)):
    # We look up by exact value (unique index) — URL should be encoded by client.
    entry = db.query(StringModel).filter(StringModel.value == string_value).first()
    if not entry:
        raise HTTPException(status_code=404, detail="String not found")
    return {
        "id": entry.id,
        "value": entry.value,
        "properties": {
            "length": entry.length,
            "is_palindrome": entry.is_palindrome,
            "unique_characters": entry.unique_characters,
            "word_count": entry.word_count,
            "sha256_hash": entry.id,
            "character_frequency_map": entry.character_frequency_map,
        },
        "created_at": entry.created_at
    }

@router.get("/strings")
def list_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=0),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
    db: Session = Depends(get_db)
):
    q = db.query(StringModel)
    filters_applied = {}
    if is_palindrome is not None:
        q = q.filter(StringModel.is_palindrome == is_palindrome)
        filters_applied["is_palindrome"] = is_palindrome
    if min_length is not None:
        q = q.filter(StringModel.length >= min_length)
        filters_applied["min_length"] = min_length
    if max_length is not None:
        q = q.filter(StringModel.length <= max_length)
        filters_applied["max_length"] = max_length
    if word_count is not None:
        q = q.filter(StringModel.word_count == word_count)
        filters_applied["word_count"] = word_count
    if contains_character is not None:
        # JSON field contains check: character_frequency_map -> keys
        # simplest cross-DB approach: use LIKE on value (slower) or JSON containment for Postgres
        # We'll use value LIKE for broad compatibility:
        q = q.filter(StringModel.value.contains(contains_character))
        filters_applied["contains_character"] = contains_character

    results = q.all()
    data = []
    for e in results:
        data.append({
            "id": e.id,
            "value": e.value,
            "properties": {
                "length": e.length,
                "is_palindrome": e.is_palindrome,
                "unique_characters": e.unique_characters,
                "word_count": e.word_count,
                "sha256_hash": e.id,
                "character_frequency_map": e.character_frequency_map,
            },
            "created_at": e.created_at
        })
    return {"data": data, "count": len(data), "filters_applied": filters_applied}

# Very simple natural language to filters parser
def _parse_nl_query(q: str):
    q = q.lower()
    parsed = {}
    if "palind" in q:  # palindromic, palindrome, etc.
        parsed["is_palindrome"] = True
    if "single word" in q or "single-word" in q or "one word" in q:
        parsed["word_count"] = 1
    # strings longer than N characters
    import re
    m = re.search(r'longer than (\d+)', q)
    if m:
        n = int(m.group(1))
        parsed["min_length"] = n + 1
    m = re.search(r'(\d+)\s*characters', q)
    if m and "longer than" not in q:  # e.g. "longer than" handled above
        # example: "strings longer than 10 characters" is handled above; this is fallback
        parsed["min_length"] = int(m.group(1))
    # containing the letter x
    m = re.search(r'letter (\w)', q)
    if m:
        parsed["contains_character"] = m.group(1)
    if "containing the letter" in q:
        # try to get last word char
        m = re.search(r'containing the letter (\w)', q)
        if m:
            parsed["contains_character"] = m.group(1)
    return parsed

@router.get("/strings/filter-by-natural-language")
def filter_by_nl(query: str = Query(...), db: Session = Depends(get_db)):
    try:
        parsed = _parse_nl_query(query)
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to parse natural language query")

    # validate conflicts (basic)
    if "min_length" in parsed and "max_length" in parsed and parsed["min_length"] > parsed["max_length"]:
        raise HTTPException(status_code=422, detail="Conflicting filters")

    # reuse list_strings flow by applying parsed filters manually
    q = db.query(StringModel)
    if parsed.get("is_palindrome") is True:
        q = q.filter(StringModel.is_palindrome == True)
    if parsed.get("word_count") is not None:
        q = q.filter(StringModel.word_count == parsed["word_count"])
    if parsed.get("min_length") is not None:
        q = q.filter(StringModel.length >= parsed["min_length"])
    if parsed.get("max_length") is not None:
        q = q.filter(StringModel.length <= parsed["max_length"])
    if parsed.get("contains_character") is not None:
        q = q.filter(StringModel.value.contains(parsed["contains_character"]))

    results = q.all()
    data = [{
        "id": e.id,
        "value": e.value,
        "properties": {
            "length": e.length,
            "is_palindrome": e.is_palindrome,
            "unique_characters": e.unique_characters,
            "word_count": e.word_count,
            "sha256_hash": e.id,
            "character_frequency_map": e.character_frequency_map,
        },
        "created_at": e.created_at
    } for e in results]

    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed
        }
    }

@router.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    entry = db.query(StringModel).filter(StringModel.value == string_value).first()
    if not entry:
        raise HTTPException(status_code=404, detail="String not found")
    db.delete(entry)
    db.commit()
    return None
