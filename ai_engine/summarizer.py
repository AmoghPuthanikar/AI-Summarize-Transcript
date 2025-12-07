from transformers import pipeline
from ai_engine.pipeline import update_job_status
import warnings
import torch

# Filter warnings
warnings.filterwarnings("ignore")

class Summarizer:
    def __init__(self):
        try:
            print("Loading BART Summarizer Model (facebook/bart-large-cnn)...")
            device = 0 if torch.cuda.is_available() else -1
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)
            print("BART Model loaded successfully.")
        except Exception as e:
            print(f"Error loading BART model: {e}")
            self.summarizer = None

    def summarize(self, job_id, text):
        update_job_status(job_id, "processing", 60, "Summarizing content (BART Abstractive)...")
        
        if not self.summarizer:
            return "Summarization failed: Model not initialized."
            
        try:
            if not text or len(text.strip()) < 50:
                return "Text too short to summarize."

            # Chunking strategy for long texts
            # BART has max position embeddings of 1024. 
            # We'll split text into ~3000 chars chunks (approx 750 tokens) to be safe.
            max_chunk_size = 3000
            chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
            
            summary_fragments = []
            for i, chunk in enumerate(chunks):
                # Adjust max_length for very short chunks
                input_len = len(chunk)
                # Heuristics: summary max length should be smaller than input
                # 1 char ~ 0.25 tokens. 3000 chars ~ 750 tokens.
                # max_length=150 tokens (~600 chars).
                # If chunk is small, reduce max_length
                
                # Approximate token count
                approx_tokens = input_len // 4
                max_len = min(150, max(30, int(approx_tokens * 0.5)))
                min_len = min(50, max(10, int(approx_tokens * 0.2)))
                
                res = self.summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)
                if res and len(res) > 0:
                    summary_fragments.append(res[0]['summary_text'])
            
            final_summary = " ".join(summary_fragments)
            return final_summary

        except Exception as e:
            print(f"Summarization Error: {e}")
            return f"Summarization failed: {str(e)}"
