import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import queue
import sounddevice as sd
import vosk
import json
import sys
import os
import threading
from datetime import datetime
# Fix for PyInstaller - Add Vosk DLLs to the path
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    base_path = sys._MEIPASS
    vosk_path = os.path.join(base_path, 'vosk')
    if os.path.exists(vosk_path):
        os.add_dll_directory(vosk_path)
else:
    # Running as script
    pass

class OssamasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ossama's App - Speech to Text")
        self.root.geometry("1200x900")
        
        # Beautiful color scheme
        self.bg_color = "#1a237e"
        self.header_color = "#3949ab"
        self.root.configure(bg=self.bg_color)
        
        # Language settings
        self.languages = {
            "English": "model_en",
            "العربية (Arabic)": "model_ar"
        }
        self.current_language = "English"
        self.current_model_path = "model_en"
        self.model = None
        
        # ========== HEADER ==========
        header = tk.Frame(root, bg=self.header_color, height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🎤 Ossama's App", 
                        font=('Arial', 40, 'bold'), 
                        bg=self.header_color, fg='white')
        title.pack(pady=15)
        
        # ========== SUBTITLE ==========
        subtitle = tk.Label(root, text="💙 Helping people who can't hear 💙", 
                           font=('Arial', 16, 'bold'), 
                           bg=self.bg_color, fg='#bbdefb')
        subtitle.pack(pady=15)
        
        # ========== LANGUAGE SELECTOR ==========
        lang_frame = tk.Frame(root, bg=self.bg_color)
        lang_frame.pack(pady=10)
        
        tk.Label(lang_frame, text="🌍 Select Language:", 
                font=('Arial', 12, 'bold'), 
                bg=self.bg_color, fg='white').pack(side=tk.LEFT, padx=10)
        
        self.lang_var = tk.StringVar(value="English")
        lang_menu = tk.OptionMenu(lang_frame, self.lang_var, *self.languages.keys(),
                                 command=self.change_language)
        lang_menu.config(font=('Arial', 12), bg='#5c6bc0', fg='white',
                        highlightthickness=0)
        lang_menu['menu'].config(bg='#5c6bc0', fg='white', font=('Arial', 12))
        lang_menu.pack(side=tk.LEFT, padx=10)
        
        # ========== TEXT DISPLAY AREA ==========
        text_frame = tk.Frame(root, bg='white', bd=5, relief=tk.FLAT, 
                             highlightthickness=3, highlightbackground=self.header_color)
        text_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(text_frame, 
                                                   wrap=tk.WORD,
                                                   width=70, 
                                                   height=14,
                                                   font=('Arial', 22, 'bold'),
                                                   bg='#fafafa',
                                                   fg='#1a237e',
                                                   relief=tk.FLAT,
                                                   padx=20,
                                                   pady=20)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ========== BUTTON FRAME ==========
        btn_frame = tk.Frame(root, bg=self.bg_color)
        btn_frame.pack(pady=20)
        
        button_style = {
            "font": ('Arial', 14, 'bold'),
            "width": 18,
            "height": 2,
            "cursor": 'hand2',
            "bd": 0,
            "relief": tk.FLAT,
            "activeforeground": "white"
        }
        
        # START BUTTON
        self.start_btn = tk.Button(btn_frame, 
                                   text="🎤 START LISTENING",
                                   command=self.start_listening,
                                   bg='#66bb6a',
                                   fg='white',
                                   activebackground='#43a047',
                                   **button_style)
        self.start_btn.grid(row=0, column=0, padx=10)
        
        # STOP BUTTON
        self.stop_btn = tk.Button(btn_frame, 
                                  text="⏹ STOP",
                                  command=self.stop_listening,
                                  bg='#ef5350',
                                  fg='white',
                                  activebackground='#e53935',
                                  state='disabled',
                                  **button_style)
        self.stop_btn.grid(row=0, column=1, padx=10)
        
        # CLEAR BUTTON
        self.clear_btn = tk.Button(btn_frame, 
                                   text="🗑 CLEAR TEXT",
                                   command=self.clear_text,
                                   bg='#78909c',
                                   fg='white',
                                   activebackground='#607d8b',
                                   **button_style)
        self.clear_btn.grid(row=0, column=2, padx=10)
        
        # SAVE BUTTON
        self.save_btn = tk.Button(btn_frame, 
                                  text="💾 SAVE FILE",
                                  command=self.save_text,
                                  bg='#42a5f5',
                                  fg='white',
                                  activebackground='#1e88e5',
                                  **button_style)
        self.save_btn.grid(row=0, column=3, padx=10)
        
        # ========== STATUS BAR ==========
        status_frame = tk.Frame(root, bg='#283593', height=60)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(status_frame, 
                                    text="Loading...",
                                    font=('Arial', 14, 'bold'),
                                    bg='#283593',
                                    fg='white')
        self.status_label.pack(pady=15)
        
        # Initialize
        self.q = queue.Queue()
        self.is_listening = False
        
        # Load initial model
        self.load_model()
    
    def change_language(self, language):
        """Change the language and load corresponding model"""
        self.current_language = language
        self.current_model_path = self.languages[language]
        
        # Stop if listening
        if self.is_listening:
            self.stop_listening()
        
        # Load new model
        self.load_model()
    
    def load_model(self):
        """Load the voice recognition model"""
        model_path = self.current_model_path
        
        print(f"Loading model from: {os.path.abspath(model_path)}")
        
        if not os.path.exists(model_path):
            self.status_label.config(
                text=f"❌ ERROR: Model folder '{model_path}' not found!",
                fg='#ffcdd2'
            )
            messagebox.showerror(
                "Error", 
                f"Model folder '{model_path}' not found!\n\n"
                f"Please download:\n"
                f"- English: vosk-model-small-en-us-0.15.zip → extract to C:\\OssamasApp\\model_en\n"
                f"- Arabic: vosk-model-ar-mgb2-0.4.zip → extract to C:\\OssamasApp\\model_ar\n\n"
                f"Download from: alphacephei.com/vosk/models"
            )
            self.start_btn.config(state='disabled')
            return
        
        try:
            print(f"Loading {self.current_language} model...")
            self.model = vosk.Model(model_path)
            self.status_label.config(
                text=f"✓ READY ({self.current_language}) - Click 'START LISTENING'",
                fg='#c8e6c9'
            )
            self.start_btn.config(state='normal')
            print(f"✓ {self.current_language} model loaded successfully!")
        except Exception as e:
            print(f"Model load error: {e}")
            messagebox.showerror("Model Error", f"Could not load model:\n{e}")
            self.status_label.config(
                text=f"❌ Error: {e}",
                fg='#ffcdd2'
            )
            self.start_btn.config(state='disabled')
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio status: {status}")
        self.q.put(bytes(indata))
    
    def start_listening(self):
        """Start listening to microphone"""
        if self.model is None:
            messagebox.showerror("Error", "Model not loaded!")
            return
        
        self.is_listening = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(
            text=f"🎤 LISTENING ({self.current_language})... Speak now!",
            fg='#c8e6c9'
        )
        
        thread = threading.Thread(target=self.listen_thread, daemon=True)
        thread.start()
        print(f"✓ Started listening in {self.current_language}...")
    
    def listen_thread(self):
        """Background thread for speech recognition"""
        try:
            device_info = sd.query_devices(None, 'input')
            samplerate = int(device_info['default_samplerate'])
            
            print(f"Microphone: {device_info['name']}")
            print(f"Sample rate: {samplerate}")
            
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000,
                                 dtype='int16', channels=1,
                                 callback=self.audio_callback):
                rec = vosk.KaldiRecognizer(self.model, samplerate)
                
                while self.is_listening:
                    data = self.q.get()
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get('text', '')
                        
                        if text.strip():
                            # Add timestamp
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            formatted_text = f"[{timestamp}] {text}\n\n"
                            
                            self.text_area.insert(tk.END, formatted_text)
                            self.text_area.see(tk.END)
                            print(f"Recognized: {text}")
        
        except Exception as e:
            print(f"Error in listen thread: {e}")
            self.root.after(0, self.stop_listening)
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="⏹ STOPPED", fg='#ffcdd2')
        print("Stopped listening")
    
    def clear_text(self):
        """Clear all text"""
        self.text_area.delete(1.0, tk.END)
        print("Text cleared")
    
    def save_text(self):
        """Save text to file"""
        text = self.text_area.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("Warning", "No text to save!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"Recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write("OSSAMA'S APP - SPEECH TO TEXT RECORDING\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Language: {self.current_language}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(text)
                
                messagebox.showinfo("Success", f"✓ Saved to:\n{filename}")
                self.status_label.config(
                    text=f"✓ Saved: {os.path.basename(filename)}",
                    fg='#c8e6c9'
                )
                print(f"File saved: {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

if __name__ == "__main__":
    print("=" * 60)
    print("STARTING OSSAMA'S APP")
    print("=" * 60)
    
    root = tk.Tk()
    app = OssamasApp(root)
    
    print("\n✓ Application window opened")
    print("\nInstructions:")
    print("1. Select language (English or Arabic)")
    print("2. Click 'START LISTENING'")
    print("3. Speak into your microphone")
    print("4. Click 'SAVE FILE' to save the recording")
    print("\n" + "=" * 60)
    
    root.mainloop()