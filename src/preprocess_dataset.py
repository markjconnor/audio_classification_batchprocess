import os
import shutil

# 1. Configuration
DATASET_DIR = "/beegfs/dataset"
FLAT_DIR = os.path.join(DATASET_DIR, "audio_files")

def flatten_and_clean():
    print("Scanning dataset for .wav files...")
    
    # Ensure our target "flat" directory exists
    os.makedirs(FLAT_DIR, exist_ok=True)
    
    # Dictionary to track the largest file for each filename
    # Format: { "song1.wav": {"path": "/original/path/song1.wav", "size": 1024000} }
    best_files = {}
    
    # 2. Recursively walk through EVERY folder in the dataset
    for root, dirs, files in os.walk(DATASET_DIR):
        # Prevent the script from scanning our new target directory
        if FLAT_DIR in root:
            continue
            
        for file in files:
            if file.lower().endswith('.wav'):
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                
                # If we haven't seen this filename before, record it
                if file not in best_files:
                    best_files[file] = {"path": filepath, "size": size}
                else:
                    # COLLISION DETECTED! (e.g., IA snippet vs TRAIN_V2 full song)
                    existing_size = best_files[file]["size"]
                    
                    # If the newly found file is larger, overwrite the record
                    if size > existing_size:
                        best_files[file] = {"path": filepath, "size": size}

    print(f"Found {len(best_files)} unique .wav files. Moving them to {FLAT_DIR}...")
    
    # 3. Move the winning files to the flat directory
    for filename, data in best_files.items():
        source_path = data["path"]
        dest_path = os.path.join(FLAT_DIR, filename)
        
        # Move the file safely
        shutil.move(source_path, dest_path)
        
    print("All audio files flattened! Cleaning up old directories...")

    # 4. Safely delete all other content (except our new flat folder and important DB/Text files)
    # We only delete directories here to ensure we don't accidentally nuke results.db or scripts
    for item in os.listdir(DATASET_DIR):
        item_path = os.path.join(DATASET_DIR, item)
        
        # If it's a directory and it's NOT our new flat directory, nuke it
        if os.path.isdir(item_path) and item_path != FLAT_DIR:
            shutil.rmtree(item_path)
            print(f"Deleted old directory: {item}")

    print("Preprocessing complete!")

if __name__ == "__main__":
    flatten_and_clean()