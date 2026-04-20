import os
import shutil
import glob
import re
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Setup SQLAlchemy ORM
Base = declarative_base()

class AudioResult(Base):
    __tablename__ = 'audio_predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    prediction = Column(String, nullable=False)
    score = Column(Float, nullable=False)

# 2. Database Connection
DB_PATH = "sqlite:////beegfs/dataset/results.db"
engine = create_engine(DB_PATH, echo=False)

# Create the table if it doesn't exist
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def parse_and_store_results(log_dir):
    session = Session()
    
    # NEW REGEX: 
    # Example: [3514.wav] Result: {'score': 0.9708396792411804, 'label': 'classical'}
    # Group 1: filename | Group 2: score | Group 3: label
    log_pattern = re.compile(r"\[(.*?)\] Result: \{'score': ([\d\.]+), 'label': '([^']+)'\}")
    
    chunk_files = glob.glob(os.path.join(log_dir, "chunk_*.out"))
    print(f"Found {len(chunk_files)} chunk files to process...")

    total_inserted = 0

    for file_path in chunk_files:
        with open(file_path, 'r') as f:
            for line in f:
                match = log_pattern.search(line)
                if match:
                    filename = match.group(1)
                    score_val = float(match.group(2))
                    prediction = match.group(3)
                    
                    # Create the DB record without inference time
                    new_result = AudioResult(
                        filename=filename,
                        prediction=prediction,
                        score=score_val
                    )
                    
                    # Merge prevents crashing on duplicate filenames
                    session.merge(new_result)
                    total_inserted += 1

    # Commit the transaction to disk
    session.commit()
    session.close()
    print(f"Success! Inserted/Updated {total_inserted} records into the database.")

def reset_metrics():
    metrics_dir = "/home/almalinux/custom_metrics"
    
    # Ensure directory exists before we try to write to it
    os.makedirs(metrics_dir, exist_ok=True)
    
    prom_file = os.path.join(metrics_dir, "audio_processing_totals.prom")
    tmp_file = os.path.join(metrics_dir, "audio_processing_totals.prom.tmp")

    # Use 0.0 for the time counters to maintain float formatting
    metric_data = f"""# HELP audio_model_load_time_total_seconds Cumulative time spent loading models
    # TYPE audio_model_load_time_total_seconds counter
    audio_model_load_time_total_seconds 0.0

    # HELP audio_inference_time_total_seconds Cumulative time spent classifying audio
    # TYPE audio_inference_time_total_seconds counter
    audio_inference_time_total_seconds 0.0

    # HELP audio_files_processed_total Cumulative number of audio files processed
    # TYPE audio_files_processed_total counter
    audio_files_processed_total 0

    # HELP audio_files_success_total Cumulative number of successful classifications
    # TYPE audio_files_success_total counter
    audio_files_success_total 0
    """

    # Atomic write and move
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(metric_data)
    shutil.move(tmp_file, prom_file)
    print("Prometheus metrics successfully reset to 0.")

# ... (the rest of your aggregator code) ...

if __name__ == "__main__":
    LOG_DIRECTORY = "/beegfs/almalinux/"
    parse_and_store_results(LOG_DIRECTORY)
    reset_metrics()
    