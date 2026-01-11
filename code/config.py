
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

TRAIN_CSV = os.path.join(DATA_DIR, "train.csv")
TEST_CSV = os.path.join(DATA_DIR, "test.csv")

# Model Config
# EMBEDDING_MODEL removed for lean pipeline
LLM_MODEL = "gemini-1.5-flash" # Placeholder

# Processing Config
VERSION = "1.1-StrictReasoning"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200 # 20% of 1000

# Constants
POS_EARLY = "early"
POS_MID = "mid"
POS_LATE = "late"
