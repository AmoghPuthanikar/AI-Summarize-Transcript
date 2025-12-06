import os
from pyannote.audio import Pipeline
import torch
from config import Config
from ai_engine.pipeline import update_job_status

class Diarizer:
    def __init__(self):
        self.auth_token = os.getenv("HF_TOKEN")
        if not self.auth_token:
            print("Warning: HF_TOKEN not found. Diarization will fail.")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def diarize(self, job_id, file_path):
        update_job_status(job_id, "processing", 40, "Diarizing speakers...")
        try:
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=self.auth_token)
            pipeline.to(self.device)
            
            # Run diarization
            diarization = pipeline(file_path)
            
            # Convert to list of segments
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            return segments
        except Exception as e:
            print(f"Diarization Error: {e}")
            # Return empty or dummy if it fails (graceful degradation)
            return [] 
