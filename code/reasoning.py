
import logging
import re
from typing import List, Dict, Tuple, Set

logger = logging.getLogger(__name__)

# --- CONFIG HEURISTICS ---

STATE_PAIRS = {
    # Alive / Dead
    "dead": ["alive", "lived", "survived", "active"],
    "died": ["alive", "lived", "survived", "active"],
    "alive": ["dead", "death", "grave", "killed", "executed"],
    
    # Freedom / Imprisonment
    "imprisoned": ["free", "travel", "wander", "visited", "liberty", "release"],
    "prison": ["free", "travel", "wander", "merged", "society"],
    "captive": ["free", "travel", "escape"],
    
    # Allegiance
    "loyal": ["traitor", "betray", "enemy", "conspire"],
    "betray": ["loyal", "faithful", "devoted", "protect"],
    
    # Moral / Character
    "honest": ["thief", "steal", "criminal", "corrupt"],
    "brave": ["coward", "fear", "run"],
    
    # Status
    "rich": ["poor", "debt", "bankrupt", "beggar"],
    "poor": ["rich", "wealth", "fortune", "gold"],
}

class Reasoner:
    def __init__(self):
        pass

    def extract_entities(self, text: str) -> Set[str]:
        """
        Extract capitalized words > 3 chars as naive entities.
        Explicitly excludes common stopwords if needed.
        """
        words = text.split()
        entities = set()
        for w in words:
            clean_w = re.sub(r'[^\w]', '', w)
            if len(clean_w) > 3 and clean_w[0].isupper():
                entities.add(clean_w.lower())
        return entities

    def classify_claim(self, text: str) -> str:
        """
        Event vs Persistent classification.
        """
        text_lower = text.lower()
        
        # Temporal markers imply Event
        if any(w in text_lower for w in ["year", "when", "then", "after", "before", "during", "date"]):
             return "EVENT"
             
        # Action verbs (heuristic)
        if any(w in text_lower for w in ["went", "traveled", "killed", "met", "found", "saw"]):
             return "EVENT"

        # Defaults (Trait / Belief / Nature)
        # Keywords imply Persistence
        if any(w in text_lower for w in ["always", "never", "nature", "blood", "soul", "character", "trait"]):
            return "PERSISTENT"
            
        return "PERSISTENT" # Default to strict requirements

    def is_strong_support(self, claim: str, sentence: str) -> bool:
        """
        Gated check: Logic requires Entity AND Action/Topic overlap.
        """
        # 1. Entity Overlap
        claim_ents = self.extract_entities(claim)
        sent_ents = self.extract_entities(sentence)
        ent_overlap = len(claim_ents.intersection(sent_ents))
        
        # 2. Topic/Action Overlap (Common words > 3 chars)
        claim_words = set(re.findall(r'\w{4,}', claim.lower()))
        sent_words = set(re.findall(r'\w{4,}', sentence.lower()))
        
        # Exclude entity words from topic overlap to force 'action' match
        claim_topics = claim_words - claim_ents
        sent_topics = sent_words - sent_ents
        
        topic_overlap = len(claim_topics.intersection(sent_topics))
        
        # Rule: At least 1 entity AND (1 topic OR 2 entities)
        # If no entities in claim (rare), require 3 matching topic words.
        if not claim_ents:
             return topic_overlap >= 3
             
        return ent_overlap >= 1 and topic_overlap >= 1

    def assess_consistency(self, backstory: str, evidence: List[str]) -> Dict:
        """
        Strict Evidence-Gated Check.
        """
        if not evidence:
            return {
                "prediction": 0,
                "rationale": "No retrieved passage establishes this claim in the narrative."
            }

        # 1. Classification
        claim_type = self.classify_claim(backstory)
        
        # 2. Contradiction Check (State Inversion)
        backstory_lower = backstory.lower()
        for key, antonyms in STATE_PAIRS.items():
            if key in backstory_lower:
                for sent in evidence:
                    sent_lower = sent.lower()
                    for ant in antonyms:
                        if ant in sent_lower:
                            # Verify they are talking about same entity?
                            if self.is_strong_support(backstory, sent):
                                return {
                                    "prediction": 0,
                                    "rationale": f"Contradicted by evidence asserting '{ant}' state: '{sent[:100]}...'"
                                }

        # 3. Support Check
        support_count = 0
        best_quote = ""
        
        for sent in evidence:
            if self.is_strong_support(backstory, sent):
                support_count += 1
                if not best_quote or len(sent) < len(best_quote): # Keep shortest relevant quote
                    best_quote = sent

        # 4. Final Gates
        if support_count == 0:
             return {
                "prediction": 0,
                "rationale": "No retrieved passage explicitly supports the events/traits described."
            }
            
        if claim_type == "PERSISTENT" and support_count < 2:
             return {
                "prediction": 0,
                "rationale": f"Insufficient evidence (only {support_count} excerpt) to establish persistent trait."
            }
            
        return {
            "prediction": 1,
            "rationale": f"Supported by narrative evidence: '{best_quote[:150]}...'"
        }
