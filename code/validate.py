
import pandas as pd
import os
import sys
from config import DATA_DIR
from retrieval import Retriever
from reasoning import Reasoner

# Map string labels to 0/1
LABEL_MAP = {
    "consistent": 1,
    "contradict": 0
}

def main():
    train_path = os.path.join(DATA_DIR, "train.csv")
    if not os.path.exists(train_path):
        print(f"Error: {train_path} not found.")
        return

    print("Loading training data...")
    df = pd.read_csv(train_path)
    
    print("Initializing Pipeline...")
    retriever = Retriever()
    reasoner = Reasoner()
    
    correct_count = 0
    total_count = 0
    
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    
    results = []

    print(f"Starting Validation on {len(df)} samples...")
    print("-" * 60)

    for idx, row in df.iterrows():
        story_id = row['book_name']
        backstory = row['content']
        ground_truth_str = row['label']
        
        # Clean label (handle potential whitespace/case)
        ground_truth = LABEL_MAP.get(ground_truth_str.strip().lower(), -1)
        if ground_truth == -1:
            print(f"Skipping row {idx}: Unknown label '{ground_truth_str}'")
            continue

        # Inference
        evidence = retriever.retrieve_evidence(backstory, story_id)
        result = reasoner.assess_consistency(backstory, evidence)
        prediction = result["prediction"]
        rationale = result["rationale"]

        # Metrics
        if prediction == ground_truth:
            correct_count += 1
            status = "✅"
        else:
            status = "❌"
            
        # Confusion Matrix
        if prediction == 1 and ground_truth == 1: tp += 1
        if prediction == 0 and ground_truth == 0: tn += 1
        if prediction == 1 and ground_truth == 0: fp += 1
        if prediction == 0 and ground_truth == 1: fn += 1

        total_count += 1
        print(f"[{status}] ID {row.get('id', idx)} | Pred: {prediction} | True: {ground_truth} | {rationale[:60]}...")

    # Final Stats
    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print("-" * 60)
    print(f"TOTAL SAMPLES: {total_count}")
    print(f"ACCURACY:      {accuracy:.2f}%")
    print(f"PRECISION:     {precision:.2f}%")
    print(f"RECALL:        {recall:.2f}%")
    print(f"F1 SCORE:      {f1:.2f}%")
    print("-" * 60)
    print(f"TP: {tp} | TN: {tn} | FP: {fp} | FN: {fn}")
    print("-" * 60)

if __name__ == "__main__":
    main()
