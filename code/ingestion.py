
import pathway as pw
from config import DATA_DIR
from utils import process_novel
import os
import pandas as pd
# Helper to check if Pathway is the stub version
import sys

def is_pathway_stub():
    # Heuristic: check if we can actually import a core module or if it crashed before
    try:
        import pathway.internals
        return False
    except:
        return True

class NovelIngestion:
    def __init__(self):
        self.novel_files = {
            "The Count of Monte Cristo": "The Count of Monte Cristo.txt",
            "In Search of the Castaways": "In search of the castaways.txt"
        }
        
    def load_and_chunk(self):
        all_chunks = []
        for book_name, filename in self.novel_files.items():
            path = os.path.join(DATA_DIR, filename)
            if os.path.exists(path):
                print(f"Processing {book_name}...")
                chunks = process_novel(path, book_name)
                all_chunks.extend(chunks)
            else:
                print(f"Warning: File {filename} not found.")
        return all_chunks

    def create_table(self):
        """
        Ingests chunks into a Pathway table.
        """
        data = self.load_and_chunk()
        df = pd.DataFrame(data)
        
        # Strict Pathway Execution
        # We use table_from_pandas for static ingestion in this script context.
        # In a live app, we would use pw.io.fs.read(...)
        print("Creating Pathway Table...")
        table = pw.debug.table_from_pandas(df)
        return table

def build_index():
    ingestor = NovelIngestion()
    table = ingestor.create_table()
    
    # LEAN MODE: No Embeddings for now.
    # Just return the raw text table. Retrieval will use keyword/overlap.
    print("Ingestion Complete (Text Only).")
    
    return table
