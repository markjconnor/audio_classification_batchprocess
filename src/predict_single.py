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

load_time = time.time() - start_load # model load time

# 2. Measure Inference Time
start_infer = time.time()
try:
    audio_array, sampling_rate = sf.read(audio_file)
    audio_input = {"array": audio_array, "sampling_rate": sampling_rate}
    
    result = classifier(audio_input)
    
    infer_time = time.time() - start_infer
    
    # Updated print statement to match your new dictionary format!
    print(f"[{filename}] Result: {result[0]}")
    success = 1
except Exception as e:
    print(f"[{filename}] Failed to process: {e}")
    infer_time = time.time() - start_infer
    success = 0

# ---------------------------------------------------------
# PROMETHEUS METRICS EXPORT (Cumulative Counter Pattern)
# ---------------------------------------------------------
metrics_dir = "/home/almalinux/custom_metrics"
os.makedirs(metrics_dir, exist_ok=True)

# We use ONE single file per worker node now!
prom_file = os.path.join(metrics_dir, "audio_processing_totals.prom")
tmp_file = os.path.join(metrics_dir, "audio_processing_totals.prom.tmp")

# 1. Read the existing totals (if the file already exists)
total_load_time = 0.0
total_infer_time = 0.0
total_processed = 0
total_success = 0

if os.path.exists(prom_file):
    with open(prom_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("audio_model_load_time_total_seconds"):
                total_load_time = float(line.split()[1])
            elif line.startswith("audio_inference_time_total_seconds"):
                total_infer_time = float(line.split()[1])
            elif line.startswith("audio_files_processed_total"):
                total_processed = int(line.split()[1])
            elif line.startswith("audio_files_success_total"):
                total_success = int(line.split()[1])

# 2. Add the current run's metrics to the running total
total_load_time += load_time
total_infer_time += infer_time
total_processed += 1
total_success += success

# 3. Format the new data as Prometheus Counters
# Note: We append "_total" to the metric names, which is the Prometheus standard for Counters
metric_data = f"""# HELP audio_model_load_time_total_seconds Cumulative time spent loading models
# TYPE audio_model_load_time_total_seconds counter
audio_model_load_time_total_seconds {total_load_time:.4f}

# HELP audio_inference_time_total_seconds Cumulative time spent classifying audio
# TYPE audio_inference_time_total_seconds counter
audio_inference_time_total_seconds {total_infer_time:.4f}

# HELP audio_files_processed_total Cumulative number of audio files processed
# TYPE audio_files_processed_total counter
audio_files_processed_total {total_processed}

# HELP audio_files_success_total Cumulative number of successful classifications
# TYPE audio_files_success_total counter
audio_files_success_total {total_success}
"""

# 4. Atomic write and move (Prevents Node Exporter from reading a half-written file)
with open(tmp_file, "w", encoding="utf-8") as f:
    f.write(metric_data)
shutil.move(tmp_file, prom_file)