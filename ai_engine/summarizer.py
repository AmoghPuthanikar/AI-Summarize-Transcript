import requests
import json
from ai_engine.pipeline import update_job_status
import warnings

# Filter warnings
warnings.filterwarnings("ignore")

class Summarizer:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/generate"
        print(f"Initialized Ollama Summarizer with model: {self.model_name}")

    def summarize(self, job_id, text):
        update_job_status(job_id, "processing", 60, f"Summarizing content (Ollama {self.model_name})...")
        
        if not text or len(text.strip()) < 50:
            return "Text too short to summarize."

        try:
            # Construct the prompt
            prompt = f"""
            You are an expert summarizer. Summarize the following content directly and concisely.
            
            Guidelines:
            - Write in a direct, objective tone.
            - Do NOT use phrases like "The transcript says", "The speaker discusses", or "The text mentions".
            - Focus purely on the Information and Actionable Insights.
            - Organize with clear headings or bullet points if appropriate.
            
            Content:
            {text}
            
            Summary:
            """
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 4096 # Context window size (increase if needed)
                }
            }
            
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            summary = result.get("response", "")
            
            if not summary:
                 return "Ollama returned an empty summary."
                 
            return summary.strip()

        except requests.exceptions.ConnectionError:
            print("Ollama Connection Error: is 'ollama serve' running?")
            return "Summarization failed: Could not connect to Ollama. Make sure 'ollama serve' is running."
        except Exception as e:
            print(f"Summarization Error: {e}")
            return f"Summarization failed: {str(e)}"
