import os
import time
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox

class FileCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cleaner - Automation for File Cleanup")
        self.folder_path = tk.StringVar()
        self.days_threshold = tk.IntVar(value=30)
        self.log = []
        
        # GUI Components
        tk.Label(root, text="Select folder to scan:").pack()
        tk.Entry(root, textvariable=self.folder_path, width=50).pack()
        tk.Button(root, text="Browse Folder", command=self.select_folder).pack()
        
        tk.Label(root, text="Days threshold for old files:").pack()
        tk.Entry(root, textvariable=self.days_threshold, width=10).pack()
        
        tk.Button(root, text="Start Scan", command=self.scan_files).pack()
        self.result_label = tk.Label(root, text="")
        self.result_label.pack()
    
    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path.set(path)
    
    def get_file_hash(self, file_path):
        """ Computes hash of a file to check for duplicates """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    
    def scan_files(self):
        folder = self.folder_path.get()
        days_threshold = self.days_threshold.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
        
        now = time.time()
        hashes = {}
        old_files = []
        duplicate_files = []
        
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):
                file_age_days = (now - os.path.getmtime(file_path)) / 86400
                file_hash = self.get_file_hash(file_path)
                
                if file_age_days > days_threshold:
                    old_files.append(file_path)
                if file_hash in hashes:
                    duplicate_files.append(file_path)
                else:
                    hashes[file_hash] = file_path
        
        if old_files or duplicate_files:
            file_list = "\n".join(os.path.basename(f) for f in old_files + duplicate_files)
            result_msg = f"\nFound {len(old_files)} old files and {len(duplicate_files)} duplicate files:\n{file_list}"
            
            # Log file names to a text file
            with open("files_to_delete.log", "w") as log_file:
                log_file.write("Files marked for deletion:\n")
                log_file.write(file_list + "\n")
        else:
            result_msg = "No files found for deletion."
        
        self.result_label.config(text=result_msg)
        
        # Confirm file deletion
        if old_files or duplicate_files:
            confirm = messagebox.askyesno("Confirm Deletion", f"Files found for deletion:\n{file_list}\nProceed?")
            if confirm:
                for f in old_files + duplicate_files:
                    os.remove(f)
                messagebox.showinfo("Deletion Complete", f"Deleted {len(old_files) + len(duplicate_files)} files!")
        else:
            messagebox.showinfo("Result", "No files found for deletion!")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = FileCleaner(root)
    root.mainloop()
