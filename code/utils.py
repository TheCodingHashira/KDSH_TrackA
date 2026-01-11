
import re
import os
import json
import logging
from typing import List, Dict, Tuple
from config import CHUNK_SIZE, CHUNK_OVERLAP, POS_EARLY, POS_MID, POS_LATE

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    # Remove Gutenberg headers/footers if possible (simple heuristic)
    text = re.sub(r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*? \*\*\*', '', text)
    text = re.sub(r'\[Illustration.*?\]', '', text)
    text = re.sub(r'\[Sidenote.*?\]', '', text)
    return text.strip()

def split_into_chapters(text: str) -> List[str]:
    # Split by Roman Numeral Chapters
    # Pattern looks for "CHAPTER" followed by Roman numerals, on its own line(s)
    pattern = r'\n\s*CHAPTER\s+[IVXLCDM]+\.?\s*\n'
    chapters = re.split(pattern, text)
    # The first element might be preamble.
    # If the first element is huge, it's the start. If small (TOC), strict filtering needed?
    # Simple heuristic: filter out empty or very short strings
    return [c.strip() for c in chapters if len(c.strip()) > 500]

def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    # Simple token estimation: 1 word ~ 1.3 tokens. 
    # Or just char based: 1 token ~ 4 chars. 1000 tokens ~ 4000 chars.
    # User constraint: "Token fallback (approx 1000 tokens)"
    # I'll use word-based chunking for Simplicity/Speed without heavy tokenizer
    words = text.split()
    step = int(chunk_size * 0.8) # overlap logic
    # Actually step = size - overlap
    # If chunk=1000 tokens (~750 words), overlap=200 (~150 words).
    # Let's say 1000 tokens is roughly 750 words.
    
    WORDS_PER_CHUNK = 800 # conservative for 1000 tokens
    OVERLAP_WORDS = 160
    
    chunks = []
    for i in range(0, len(words), WORDS_PER_CHUNK - OVERLAP_WORDS):
        chunk_words = words[i : i + WORDS_PER_CHUNK]
        chunks.append(" ".join(chunk_words))
    return chunks

def assign_relative_position(chunk_idx: int, total_chunks: int) -> str:
    if total_chunks == 0: return POS_MID
    ratio = chunk_idx / total_chunks
    if ratio < 0.33:
        return POS_EARLY
    elif ratio < 0.66:
        return POS_MID
    else:
        return POS_LATE

def process_novel(file_path: str, story_id: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    text = clean_text(raw_text)
    chapters = split_into_chapters(text)
    
    # If chapters failed (e.g. no Roman numerals), treat as one big chapter
    if len(chapters) == 0:
        chapters = [text]
        
    all_chunks = []
    
    # First pass: Generate all chunks to count them? 
    # Or count chapters?
    # "Relative position" usually refers to the whole book.
    
    # Let's flatten everything first
    temp_chunks = []
    for chap_idx, chap_text in enumerate(chapters):
        c_chunks = chunk_text(chap_text)
        for cc in c_chunks:
            temp_chunks.append({
                "text": cc,
                "chapter_index": chap_idx
            })
            
    total_chunks = len(temp_chunks)
    
    processed_data = []
    for i, item in enumerate(temp_chunks):
        processed_data.append({
            "story_id": story_id,
            "chunk_id": f"{story_id}_chunk_{i}",
            "text": item["text"],
            "relative_position": assign_relative_position(i, total_chunks),
            "chapter_index": item["chapter_index"]
        })
        
    return processed_data
