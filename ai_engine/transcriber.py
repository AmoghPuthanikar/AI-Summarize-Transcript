from faster_whisper import WhisperModel
import torch
from ai_engine.pipeline import update_job_status
import os

class Transcriber:
    def __init__(self, model_size="base"): # Upgraded to base for accuracy, still fast with faster-whisper
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        print(f"Loading Faster-Whisper model ({model_size}) on {self.device} with {self.compute_type}...")
        self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)

    def transcribe(self, job_id, file_path):
        update_job_status(job_id, "processing", 20, "Transcribing audio (Faster-Whisper)...")
        try:
            # Enforce English Language
            segments, info = self.model.transcribe(file_path, beam_size=5, language="en")
            
            # Format segments to match previous structure
            formatted_segments = []
            full_text = []
            
            for segment in segments:
                formatted_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                })
                full_text.append(segment.text)
            
            return {
                "text": " ".join(full_text),
                "segments": formatted_segments
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {e}")

# Singleton (load once) or load on demand? 
# For now, load on demand or global if memory permits. 
# We'll instantiate inside the task for memory safety if concurrency is low.
