import sys
import os
import time
import torch
import torchaudio
import soundfile as sf  # <-- Import the soundfile library
from transformers import pipeline

# Ensure a file path was passed
if len(sys.argv) < 2:
    print("Error: No audio file provided.")
    sys.exit(1)

audio_file = sys.argv[1]
filename = os.path.basename(audio_file)

start_load = time.time()
print(f"[{filename}] Initializing pipeline and loading model into RAM...")

classifier = pipeline(
    "audio-classification", 
    model="dima806/music_genres_classification"
)

end_load = time.time()
print(f"[{filename}] Model loaded in {end_load - start_load:.2f} seconds.")

try:
    # 1. Read the audio file directly using soundfile to bypass FFmpeg
    audio_array, sampling_rate = sf.read(audio_file)
    
    # 2. Package it into the dictionary format that Hugging Face expects
    audio_input = {
        "array": audio_array,
        "sampling_rate": sampling_rate
    }
    
    # 3. Pass the raw data to the classifier instead of the file path
    result = classifier(audio_input)
    print(f"[{filename}] Result: {result[0]['label']}")
    
except Exception as e:
    print(f"[{filename}] Failed to process: {e}")