import tkinter as tk
from PIL import Image, ImageTk
import sys
import json
import base64
import io
import threading

class GameViewer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kaname's Game Console (External)")
        self.root.geometry("300x350")
        self.root.configure(bg="black")
        
        self.label_score = tk.Label(self.root, text="Waiting...", fg="white", bg="black", font=("Consolas", 14))
        self.label_score.pack(pady=5)
        
        self.canvas = tk.Canvas(self.root, width=200, height=200, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self.label_info = tk.Label(self.root, text="Initializing...", fg="#888", bg="black", font=("Consolas", 10))
        self.label_info.pack(pady=5)
        
        # 標準入力読み込みスレッド
        self.stop_event = threading.Event()
        self.reader_thread = threading.Thread(target=self.read_stdin, daemon=True)
        self.reader_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        self.stop_event.set()
        self.root.destroy()
        sys.exit(0)

    def read_stdin(self):
        """標準入力からJSONを受け取る"""
        buffer = sys.stdin
        while not self.stop_event.is_set():
            try:
                line = buffer.readline()
                if not line:
                    break
                
                data = json.loads(line)
                self.root.after(0, lambda: self.update_ui(data))
            except json.JSONDecodeError:
                continue
            except Exception as e:
                # print(f"Viewer Error: {e}", file=sys.stderr)
                break

    def update_ui(self, data):
        try:
            # 画像デコード
            img_b64 = data.get("image")
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                img = Image.open(io.BytesIO(img_bytes))
                self.tk_img = ImageTk.PhotoImage(img) # 参照保持
                self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            
            # テキスト更新
            score = data.get("score", 0)
            info = data.get("info", "")
            
            self.label_score.config(text=f"Score: {score}")
            self.label_info.config(text=info)
            
        except Exception as e:
            print(f"UI Update Error: {e}")

if __name__ == "__main__":
    try:
        GameViewer()
    except KeyboardInterrupt:
        pass
