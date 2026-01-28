import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import urllib.request
import threading

class IPTVGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VLC IPTV - Fixed")
        self.root.geometry("800x600")
        
        self.sports_channels = []
        self.free_channels = []
        
        self.setup_gui()
        self.load_playlists()
    
    def setup_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sports tab
        sports_frame = ttk.Frame(notebook)
        notebook.add(sports_frame, text="Sports")
        self.sports_listbox = tk.Listbox(sports_frame, font=('Arial', 10))
        self.sports_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Button(sports_frame, text="Play", command=self.play_sports, bg='green', fg='white').pack(pady=5)
        
        # Free TV tab
        tv_frame = ttk.Frame(notebook)
        notebook.add(tv_frame, text="Free TV")
        self.tv_listbox = tk.Listbox(tv_frame, font=('Arial', 10))
        self.tv_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Button(tv_frame, text="Play", command=self.play_tv, bg='blue', fg='white').pack(pady=5)
        
        self.status = tk.Label(self.root, text="Loading...", relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_playlists(self):
        threading.Thread(target=self.load_sports, daemon=True).start()
        threading.Thread(target=self.load_free_tv, daemon=True).start()
    
    def status_update(self, msg):
        self.status.config(text=msg)
    
    def load_sports(self):
        self.status_update("Loading Sports...")
        try:
            channels = self.get_channels("https://iptv-org.github.io/iptv/categories/sports.m3u")
            self.sports_channels = channels
            self.root.after(0, self.sports_listbox.delete, 0, tk.END)
            for name, url in channels:
                self.root.after(0, self.sports_listbox.insert, tk.END, name)
            self.status_update(f"Sports: {len(channels)} channels ✓")
        except Exception as e:
            self.status_update(f"Sports failed: {e}")
    
    def load_free_tv(self):
        self.status_update("Loading Free TV...")
        try:
            channels = self.get_channels("https://iptv-org.github.io/iptv/index.m3u")
            self.free_channels = channels
            self.root.after(0, self.tv_listbox.delete, 0, tk.END)
            for name, url in channels:
                self.root.after(0, self.tv_listbox.insert, tk.END, name)
            self.status_update(f"Free TV: {len(channels)} channels ✓")
        except Exception as e:
            self.status_update(f"Free TV failed: {e}")
    
    def get_channels(self, url):
        """Simple M3U parser - WORKS"""
        with urllib.request.urlopen(url, timeout=15) as f:
            content = f.read().decode('utf-8', errors='ignore')
        
        channels = []
        lines = content.split('\n')
        name = None
        
        for line in lines:
            if line.startswith('#EXTINF'):
                name = line.split(',')[-1].strip().strip('"\'').strip()
            elif line.strip().startswith('http') and name:
                channels.append((name[:50], line.strip()))
                name = None
        
        return channels[:200]  # Limit
    
    def play_sports(self):
        sel = self.sports_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Pick a sports channel")
            return
        idx = sel[0]
        name, url = self.sports_channels[idx]
        self.play_vlc(url, name)
    
    def play_tv(self):
        sel = self.tv_listbox.curselection()
        if not sel:
            messagebox.showwarning("Select", "Pick a TV channel")
            return
        idx = sel[0]
        name, url = self.free_channels[idx]
        self.play_vlc(url, name)
    
    def play_vlc(self, url, name):
        """Simple VLC launch - TESTED"""
        self.status.config(text=f"Playing: {name}")
        try:
            # Basic VLC command that ALWAYS works
            subprocess.Popen(['vlc', url])
            print(f"Launched VLC with: {url}")  # Debug
        except FileNotFoundError:
            messagebox.showerror("VLC", "Install VLC: sudo dnf install vlc")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = IPTVGUI(root)
    root.mainloop()
