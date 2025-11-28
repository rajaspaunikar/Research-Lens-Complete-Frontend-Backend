import spacy
from collections import Counter
import re

class MetadataExtractor:
    def __init__(self):
        # Assuming the model is downloaded
        try:
            self.nlp = spacy.load('en_core_web_md')
        except:
            self.nlp = spacy.load('en_core_web_sm')

    def extract_keywords(self, text, top_n=15):
        doc = self.nlp(text)
        
        # Common phrases to ignore
        ignore = [
            'this paper', 'this work', 'our method', 'proposed method', 
            'experimental results', 'future work', 'state-of-the-art'
        ]

        # simple acronym mapping
        # e.g. "Large Language Models (LLMs)"
        shorts = {}
        found = re.findall(r'([A-Z][a-zA-Z\s-]{5,})\s+\(([A-Z]{2,}[s]?)\)', text)
        for long_v, short_v in found:
            shorts[short_v.lower()] = long_v.lower()

        final_list = []
        
        for chunk in doc.noun_chunks:
            curr = chunk.text.lower().strip()
            
            if curr in ignore:
                continue
                
            # skip "our model", "the results"
            if chunk[0].text.lower() in ['this', 'that', 'our', 'we', 'the']:
                continue

            if len(curr) < 3 or curr in self.nlp.Defaults.stop_words:
                continue

            # replace acronyms if found
            if curr in shorts:
                curr = shorts[curr]
            
            # singularize
            if curr.endswith('s') and not curr.endswith('ss'):
                 curr = curr[:-1]

            final_list.append(curr)
            
        return Counter(final_list).most_common(top_n)

    def clean_abstract(self, txt):
        txt = re.sub(r'\s+', ' ', txt)
        txt = re.sub(r'[^\w\s.,;:!?-]', '', txt)
        return txt.strip()
    
    def extract_key_findings(self, txt):
        doc = self.nlp(txt)
        sents = list(doc.sents)
        
        res = ""
        high_score = 0
        tag = "info"
        
        # simple scoring system
        keywords = {
            'outperform': 5, 'achieve': 4, 'sota': 6, 'surpass': 5, 
            'improve': 3, 'accuracy': 3, 'novel': 3
        }
        
        for s in sents:
            raw = s.text.lower()
            score = 0
            
            for k, v in keywords.items():
                if k in raw:
                    score += v
            
            # extra points for numbers
            if re.search(r'\d+%', raw) or re.search(r'\d+\.\d+', raw):
                score += 2

            if score > high_score:
                high_score = score
                res = s.text
                
                if 'sota' in raw:
                    tag = "SOTA"
                elif 'outperform' in raw:
                    tag = "PERFORMANCE"
                elif 'novel' in raw:
                    tag = "NOVELTY"
        
        # fallback to last sentence
        if not res and sents:
            res = sents[-1].text
            tag = "CONCLUSION"
            
        return {"text": res, "score": high_score, "type": tag}