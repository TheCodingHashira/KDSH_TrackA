# KDSH 2026 Track A: Narrative Consistency Checker

**Team: Algorythms**

A deterministic, evidence-gated RAG system designed to verify character backstories against long-context novels (Track A).

## 🏆 System Highlights
*   **Zero-Hallucination Logic**: Uses a "Guilty Until Proven Innocent" architecture.
*   **Evidence Gating**: Rejects claims unless explicit Entity + Action overlap is found.
*   **State Inversion**: Automatically detects contradictions like "Dead" vs "Alive".
*   **Dockerized**: Fully reproducible pipeline built on Pathway.

## 🚀 Quick Start

### Prerequisites
*   Docker installed on your machine.
*   Novels placed in `data/`.

### Running the Inference
The entire pipeline (Ingestion -> Retrieval -> Reasoning) is containerized.

```bash
# 1. Build the Image
docker build -t kdsh-track-a .

# 2. Run the Container (Persist results)
docker run --name kdsh_runner kdsh-track-a

# 3. Extract Results
docker cp kdsh_runner:/app/results/results.csv ./results.csv

# 4. Clean Up
docker rm kdsh_runner
```

## 🏗️ Architecture

### 1. The Logic Core ("Evidence Gating")
We define consistency strictly. A prediction of `1` (Consistent) is only granted if:
1.  **Retrieval Success**: Relevant text chunks are found.
2.  **No Contradictions**: No logical state mismatches (e.g., Claim says "Free", Text says "Imprisoned").
3.  **Strong Support**: Explicit overlap of Entities AND Actions.
4.  **Persistence Check**: Traits require multiple evidentiary sources.

### 2. Technology Stack
*   **Orchestration**: Docker
*   **Data Processing**: Pathway
*   **Embedding**: None (Lean Mode) / Sentence-Transformers (High Accuracy Mode supported in code)
*   **Language**: Python 3.10

## 📂 Project Structure
```
.
├── code/
│   ├── ingestion.py    # Pathway table creation & chunking
│   ├── retrieval.py    # Search algos (Jaccard/Cosine)
│   ├── reasoning.py    # The 4-Gate Logic Engine
│   ├── main.py         # Entry point
│   ├── config.py       # Global settings
│   └── utils.py        # Text cleaning helpers
├── data               # Input novels & CSVs
├── Dockerfile          # Reproducible build env
├── requirements.txt    # Python dependencies
|── results/
    ├── results.csv           # Final output
```

## 📊 Performance
*   **Philosophy**: High Specificity. We prefer False Negatives (admitting ignorance) over False Positives (lying).
*   **Validation**: Validated against `train.csv` to ensure rationales are human-readable and evidence-backed.
