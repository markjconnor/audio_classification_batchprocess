import sys
import os
import time
import shutil
import torch
import torchaudio
import soundfile as sf
from transformers import pipeline

if len(sys.argv) < 2:
    print("Error: No audio file provided.")
    sys.exit(1)

audio_file = sys.argv[1]
filename = os.path.basename(audio_file)

# 1. Measure Model Load Time
start_load = time.time()
print(f"[{filename}] Initializing pipeline and loading model into RAM...")

classifier = pipeline(
    "audio-classification", 
    model="dima806/music_genres_classification"
)

load_time = time.time() - start_load
print(f"[{filename}] Model loaded in {load_time:.2f} seconds.")

# 2. Measure Inference Time
start_infer = time.time()
try:
    audio_array, sampling_rate = sf.read(audio_file)
    audio_input = {"array": audio_array, "sampling_rate": sampling_rate}
    
    result = classifier(audio_input)
    
    infer_time = time.time() - start_infer
    print(f"[{filename}] Result: {result[0]['label']} (Inference took {infer_time:.2f}s)")
    success = 1
except Exception as e:
    print(f"[{filename}] Failed to process: {e}")
    infer_time = time.time() - start_infer
    success = 0

# ---------------------------------------------------------
# PROMETHEUS METRICS EXPORT
# ---------------------------------------------------------
# We use the Process ID (PID) so parallel jobs don't overwrite each other
pid = os.getpid()
metrics_dir = "/home/almalinux/custom_metrics"

# Ensure the directory exists
os.makedirs(metrics_dir, exist_ok=True)

tmp_file = os.path.join(metrics_dir, f"audio_processing_{pid}.prom.tmp")
prom_file = os.path.join(metrics_dir, f"audio_processing_{pid}.prom")

# Format the data according to Prometheus Textfile standards
metric_data = f"""# HELP audio_model_load_time_seconds Time spent loading the model into RAM
# TYPE audio_model_load_time_seconds gauge
audio_model_load_time_seconds{{worker="{os.uname()[1]}", pid="{pid}"}} {load_time:.4f}

# HELP audio_inference_time_seconds Time spent classifying the audio
# TYPE audio_inference_time_seconds gauge
audio_inference_time_seconds{{worker="{os.uname()[1]}", pid="{pid}"}} {infer_time:.4f}

# HELP audio_processing_success Whether the classification succeeded (1) or failed (0)
# TYPE audio_processing_success gauge
audio_processing_success{{worker="{os.uname()[1]}", pid="{pid}"}} {success}
"""

# Atomic write and move
with open(tmp_file, "w", encoding="utf-8") as f:
    f.write(metric_data)
shutil.move(tmp_file, prom_file)