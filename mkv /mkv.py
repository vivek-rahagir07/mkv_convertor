import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import re
import time


class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MKV Converter Ultra Pro — Masterpiece")
        self.root.geometry("1000x850")
        self.root.minsize(900, 750)

       
        self.dark_mode = True
        self.style = tb.Style(theme="darkly")
    
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status_text = tk.StringVar(value="SYSTEM READY")
        self.progress_percent = tk.StringVar(value="0%")
        self.progress_value = tk.DoubleVar(value=0)
        self.is_converting = False

        self.create_ui()
        self.log_event("SUCCESS", "Neural Engine Initialized")
        self.log_event("INFO", "Ready for high-performance transcoding")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        theme = "darkly" if self.dark_mode else "flatly"
        self.style.theme_use(theme)
        self.log_event("INFO", f"Visual matrix shifted to {theme.upper()}")

    def create_ui(self):
        """Constructs the Masterpiece UI with robust string-based styling."""
        self.main = tb.Frame(self.root, padding=40)
        self.main.pack(fill="both", expand=True)

        
        header = tb.Frame(self.main)
        header.pack(fill="x", pady=(0, 25))
        
        title_box = tb.Frame(header)
        title_box.pack(side="left")
        
        tb.Label(
            title_box,
            text="MKV ➔ MP4",
            font=("Montserrat", 46, "bold"),
            bootstyle="primary"
        ).pack(anchor="w")

        tb.Label(
            title_box,
            text="ULTRA-PERFORMANCE ENGINE • v3.0 MASTERPIECE",
            font=("Consolas", 10, "bold"),
            bootstyle="secondary"
        ).pack(anchor="w", padx=5)

        tb.Button(
            header,
            text=" 🌗 THEME ",
            command=self.toggle_theme,
            bootstyle="secondary-outline",
            padding=10
        ).pack(side="right", pady=(10, 0))

        tb.Separator(self.main, bootstyle="secondary").pack(fill="x", pady=25)

      
        self.drop_card = tb.LabelFrame(self.main, text=" CORE INTERFACE ")
        self.drop_card.pack(fill="x", pady=10)
        
        drop_inner = tb.Frame(self.drop_card, padding=10)
        drop_inner.pack(fill="x")

        self.drop_zone = tb.Label(
            drop_inner,
            text=" \n🎬 DRAG & DROP MKV FILE HERE\n \nOR CLICK TO BROWSE TARGET\n ",
            font=("Inter", 16, "bold"),
            padding=40,
            bootstyle="inverse-dark",
            anchor="center",
            cursor="hand2"
        )
        self.drop_zone.pack(fill="x")
        
    
        if hasattr(self.root, 'drop_target_register'):
            self.drop_zone.drop_target_register("DND_Files")
            self.drop_zone.dnd_bind("<<Drop>>", self.handle_drop)
        
        self.drop_zone.bind("<Button-1>", lambda e: self.browse_input())

       
        settings = tb.Frame(self.main, padding=(0, 20))
        settings.pack(fill="x")

        out_frame = tb.LabelFrame(settings, text=" DESTINATION CONFIGURATION ")
        out_frame.pack(fill="x")
        
        out_inner = tb.Frame(out_frame, padding=15)
        out_inner.pack(fill="x")

        self.output_entry = tb.Entry(
            out_inner,
            textvariable=self.output_path,
            font=("Consolas", 11),
            bootstyle="dark"
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))

        tb.Button(
            out_inner,
            text="SET TARGET",
            command=self.browse_output,
            bootstyle="primary-outline",
            width=12
        ).pack(side="right")

   
        specs = tb.Frame(self.main, padding=(10, 20))
        specs.pack(fill="x")
        
        self.spec_lbl = tb.Label(
            specs,
            text="STATUS: WAITING FOR PAYLOAD",
            font=("Consolas", 10, "bold"),
            bootstyle="info"
        )
        self.spec_lbl.pack(side="left")

        prog_box = tb.Frame(self.main)
        prog_box.pack(fill="x", pady=(10, 30))
        
        prog_header = tb.Frame(prog_box)
        prog_header.pack(fill="x", pady=(0, 10))
        
        tb.Label(
            prog_header,
            textvariable=self.status_text,
            font=("Montserrat", 11, "bold"),
            bootstyle="success"
        ).pack(side="left")
        
        tb.Label(
            prog_header,
            textvariable=self.progress_percent,
            font=("Consolas", 12, "bold"),
            bootstyle="info"
        ).pack(side="right")

        self.progress_bar = tb.Progressbar(
            prog_box,
            variable=self.progress_value,
            maximum=100,
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill="x")


        log_label = tb.Frame(self.main, padding=(0, 0, 0, 8))
        log_label.pack(fill="x")
        tb.Label(log_label, text="SYSTEM ACTIVITY LOG", font=("Consolas", 9, "bold"), bootstyle="secondary").pack(side="left")
        
        self.log_widget = ScrolledText(
            self.main,
            height=8,
            autohide=True,
            font=("Consolas", 9),
            bootstyle="dark"
        )
        self.log_widget.pack(fill="both", expand=True)
        
   
        self.log_widget.text.config(state="normal", bg="#0d1117", fg="#c9d1d9")
        self.log_widget.text.tag_config("SUCCESS", foreground="#3fb950")
        self.log_widget.text.tag_config("ERROR", foreground="#f85149")
        self.log_widget.text.tag_config("INFO", foreground="#58a6ff")
        self.log_widget.text.tag_config("PROCESS", foreground="#d29922")
        self.log_widget.text.config(state="disabled")

    def log_event(self, level, message):
        timestamp = time.strftime("[%H:%M:%S]")
        icons = {"SUCCESS": "✔", "ERROR": "✖", "INFO": "ℹ", "PROCESS": "⚙"}
        icon = icons.get(level, "•")
        
        self.log_widget.text.config(state="normal")
        self.log_widget.text.insert("end", f"{timestamp} ", "INFO")
        self.log_widget.text.insert("end", f"{icon} {level:<8} ", level)
        self.log_widget.text.insert("end", f"| {message}\n")
        self.log_widget.text.see("end")
        self.log_widget.text.config(state="disabled")

    def handle_drop(self, event):
        path = event.data.strip("{}")
        if path.lower().endswith(".mkv"):
            self.input_path.set(path)
            self.output_path.set(os.path.splitext(path)[0] + ".mp4")
            
            size = os.path.getsize(path) / (1024 * 1024)
            name = os.path.basename(path)
            self.spec_lbl.config(text=f"DETECTED: {name} | SIZE: {size:.2f} MB")
            
            self.log_event("SUCCESS", f"Payload Loaded: {name}")
            self.status_text.set("STARTING CONVERSION...")
            threading.Thread(target=self.run_conversion, daemon=True).start()
        else:
            self.log_event("ERROR", "Invalid file format. MKV required.")
            messagebox.showerror("Error", "Please drop an MKV file.")

    def browse_input(self):
        file = filedialog.askopenfilename(filetypes=[("MKV Files", "*.mkv")])
        if file:
            class FakeEvent: pass
            ev = FakeEvent()
            ev.data = file
            self.handle_drop(ev)

    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".mp4")
        if file:
            self.output_path.set(file)
            self.log_event("INFO", "Output vectors updated")

    def run_conversion(self):
        if self.is_converting: return
        self.is_converting = True
        
        inp = self.input_path.get()
        out = self.output_path.get()
        
        if not inp or not out or inp == out:
            self.root.after(0, lambda: self.finish_error("Invalid I/O configuration"))
            return

        cmd = [
            "ffmpeg", "-y", "-i", inp,
            "-c", "copy", out
        ]

        self.log_event("PROCESS", "Executing ULTRA-FAST Stream Copy Sequence")
        
        try:
            process = subprocess.Popen(
                cmd, stderr=subprocess.PIPE, universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            duration = None
            for line in process.stderr:
                if "Duration" in line:
                    match = re.search(r"Duration: (\d+):(\d+):(\d+).(\d+)", line)
                    if match:
                        h, m, s, ms = map(int, match.groups())
                        duration = h * 3600 + m * 60 + s

                if "time=" in line and duration:
                    match = re.search(r"time=(\d+):(\d+):(\d+).(\d+)", line)
                    if match:
                        h, m, s, ms = map(int, match.groups())
                        cur = h * 3600 + m * 60 + s
                        pct = int((cur / duration) * 100)
                        self.root.after(0, self.progress_value.set, pct)
                        self.root.after(0, self.progress_percent.set, f"{pct}%")
                        self.root.after(0, self.status_text.set, f"CONVERTING... {pct}%")

            process.wait()
            if process.returncode == 0:
                self.root.after(0, self.finish_success)
            else:
                self.root.after(0, self.finish_error)
        except Exception as e:
            self.root.after(0, lambda: self.finish_error(str(e)))

    def finish_success(self):
        self.is_converting = False
        self.progress_value.set(100)
        self.progress_percent.set("100%")
        self.status_text.set("COMPLETED ✔")
        self.log_event("SUCCESS", "Transcoding finalized")
        messagebox.showinfo("Success", "Masterpiece Rendered!")

    def finish_error(self, err="Failed"):
        self.is_converting = False
        self.status_text.set("ERROR ❌")
        self.log_event("ERROR", f"Kernel Fault: {err}")
        messagebox.showerror("Error", f"Conversion failed: {err}")


if __name__ == "__main__":
    if TkinterDnD:
        try:
            root = TkinterDnD.Tk()
            app = VideoConverterApp(root)
            root.mainloop()
        except Exception:
            # Fallback
            root = tb.Window()
            app = VideoConverterApp(root)
            root.mainloop()
    else:
        root = tb.Window()
        app = VideoConverterApp(root)
        root.mainloop()