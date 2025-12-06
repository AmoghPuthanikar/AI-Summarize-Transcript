from transformers import pipeline
from ai_engine.pipeline import update_job_status

class Summarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, job_id, text):
        update_job_status(job_id, "processing", 60, "Generating summary...")
        try:
            # Chunking might be needed for very long text
            # Simple truncation for MVP, or loop through chunks
            max_chunk = 1024
            if len(text) > max_chunk * 4: # Approximation
                text = text[:max_chunk * 4] # Truncate for speed/memory in MVP

            summary = self.summarizer(text, max_length=130, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Summarization Error: {e}")
            return "Summary unavailable."
