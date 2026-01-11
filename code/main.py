
import pandas as pd
import os
import csv
from config import TEST_CSV, RESULTS_DIR
from retrieval import Retriever
from reasoning import Reasoner

def main():
    print("Starting Track A Inference Engine...")
    
    # 1. Initialize Components
    retriever = Retriever()
    reasoner = Reasoner()
    
    # 2. Load Data
    df = pd.read_csv(TEST_CSV)
    results = []
    
    print(f"Processing {len(df)} test cases...")
    
    for idx, row in df.iterrows():
        story_id = row['book_name']
        backstory = row['content'] # Assuming 'content' field holds the backstory text
        case_id = row['id']
        
        print(f"[{idx+1}/{len(df)}] ID {case_id}: Processing...")
        
        # 3. Retrieve Evidence
        evidence = retriever.retrieve_evidence(backstory, story_id)
        
        # 4. Reason
        assessment = reasoner.assess_consistency(backstory, evidence)
        
        results.append({
            "story_id": story_id, # Re-confirm if this is the ID format required
            "prediction": assessment["prediction"],
            "rationale": assessment["rationale"]
        })
        
    # 5. Write Results
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    output_path = os.path.join(RESULTS_DIR, "results.csv")
    results_df = pd.DataFrame(results)
    
    # Ensure correct columns
    # The prompt asked for: story_id,prediction,rationale
    results_df = results_df[['story_id', 'prediction', 'rationale']]
    
    results_df.to_csv(output_path, index=False)
    print(f"Success! Results written to {output_path}")

if __name__ == "__main__":
    main()
