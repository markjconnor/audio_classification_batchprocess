import sys
import os
import time
from transformers import pipeline

# Ensure a file path was passed
if len(sys.argv) < 2:
    print("Error: No audio file provided.")
    sys.exit(1)

audio_file = sys.argv[1]
filename = os.path.basename(audio_file)

# We will time the loading process so you can see the overhead in your logs
start_load = time.time()
print(f"[{filename}] Initializing pipeline and loading model into RAM...")

# This is the bottleneck!
classifier = pipeline(
    "audio-classification", 
    model="dima806/music_genres_classification"
)

end_load = time.time()
print(f"[{filename}] Model loaded in {end_load - start_load:.2f} seconds.")

# Make the prediction
try:
    result = classifier(audio_file)
    print(f"[{filename}] Result: {result[0]['label']}")
except Exception as e:
    print(f"[{filename}] Failed to process: {e}")