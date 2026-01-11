
import numpy as np
import pandas as pd
from typing import List, Dict
import pathway as pw
from config import POS_EARLY, POS_MID, POS_LATE
from ingestion import build_index

class Retriever:
    def __init__(self):
        print("Initializing Retrieval Layer (Calculating Vectors)...")
    def __init__(self):
        print("Initializing Retrieval Layer (Calculating Vectors)...")
        self.vector_resource = build_index() 
        
        # In strict Pathway mode, we assume this is a Table.
        # However, for downstream Pandas logic in this specific script, 
        # we still convert to Pandas for the iteration step (simple integration).
        # In a full Pathway app, we would use `pw.io` to write results.
        self.data_df = pw.debug.table_to_pandas(self.vector_resource)
            
        print("Vectors calculated. Index ready.")
        
    def retrieve_evidence(self, backstory: str, story_id: str, top_k: int = 5) -> List[str]:
        """
        Retrieves relevant chunks from early, mid, and late sections.
        Enforces diversity: No more than 30% from the same chapter.
        """
        # Filter by story_id
        story_df = self.data_df[self.data_df['story_id'] == story_id].copy()
        
        if story_df.empty:
            return []

        # LEAN MODE: Word Overlap Scoring
        # Simple Jaccard-like or keyword counting
        query_words = set(backstory.lower().split())
        
        def calculate_score(text):
            # Very simple overlap
            text_words = set(str(text).lower().split())
            intersection = query_words.intersection(text_words)
            if not text_words: return 0.0
            return len(intersection) / (len(query_words) + 1.0) # Simple ratio
            
        # Apply scoring
        # In a real Pathway app, this would be a UDF.
        # Here we do it via apply since we are in Pandas mode (stub or not).
        story_df['score'] = story_df['text'].apply(calculate_score)
        
        # Multi-slice retrieval strategy
        # Slice 1: Early
        early_top = self._get_slice_top_k(story_df, POS_EARLY, 3)
        # Slice 2: Mid
        mid_top = self._get_slice_top_k(story_df, POS_MID, 3)
        # Slice 3: Late
        late_top = self._get_slice_top_k(story_df, POS_LATE, 3)
        
        # General top (ignoring position) to catch strong signals anywhere
        global_top = story_df.nlargest(5, 'score')
        
        # Merge
        candidates = pd.concat([early_top, mid_top, late_top, global_top]).drop_duplicates(subset=['chunk_id'])
        
        # Sort by score
        candidates = candidates.sort_values('score', ascending=False)
        
        # Diversity Constraint
        final_chunks = []
        chapter_counts = {}
        max_per_chapter = max(1, int(top_k * 0.3)) # e.g., 30% of 10 is 3
        
        for _, row in candidates.iterrows():
            chap = row['chapter_index']
            if chapter_counts.get(chap, 0) < max_per_chapter:
                final_chunks.append(row['text'])
                chapter_counts[chap] = chapter_counts.get(chap, 0) + 1
            
            if len(final_chunks) >= top_k:
                break
                
        return final_chunks

    def _get_slice_top_k(self, df, pos, k):
        return df[df['relative_position'] == pos].nlargest(k, 'score')

