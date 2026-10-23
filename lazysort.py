import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ollama

# --- CONFIGURATION ---
MONITOR_DIR = "./messy_folder" 
ORGANIZE_DIR = "./organized_folders"
CATEGORIES = ["Coursework", "Projects", "Invoices", "Images", "Random"]

class LazySortHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        filename = os.path.basename(file_path)
        time.sleep(1) 
        
        print(f"New file detected: {filename}")
        self.categorize_and_move(file_path, filename)

    def categorize_and_move(self, file_path, filename):
        prompt = f"""
        You are a highly efficient file organizer. 
        Based on this filename: '{filename}', categorize it into exactly ONE of the following categories: 
        {', '.join(CATEGORIES)}. 
        Reply ONLY with the exact category name. Do not include any other words or punctuation.
        """
        
        try:
            response = ollama.chat(model='llama3.2', messages=[
                {'role': 'user', 'content': prompt}
            ])
            category = response['message']['content'].strip()
            
            if category not in CATEGORIES:
                category = "Random"
                
            target_dir = os.path.join(ORGANIZE_DIR, category)
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, filename)
            shutil.move(file_path, target_path)
            print(f"Moved '{filename}' to -> {category}/")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    os.makedirs(MONITOR_DIR, exist_ok=True)
    os.makedirs(ORGANIZE_DIR, exist_ok=True)
    
    event_handler = LazySortHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=False)
    observer.start()
    
    print(f"Sloth mode activated. Watching {MONITOR_DIR} for new files...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()