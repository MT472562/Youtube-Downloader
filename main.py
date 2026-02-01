import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp as youtube_dl
import os
import imageio_ffmpeg  # ★追加: これがFFmpegを連れてきてくれる魔法のライブラリ

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader (Smart)")
        self.geometry("500x350")
        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # --- URL入力 ---
        self.url_label = ttk.Label(self, text="YouTube URL:")
        self.url_label.pack(pady=5)
        self.url_entry = ttk.Entry(self, width=50)
        self.url_entry.pack(pady=5)

        # --- 保存先選択 ---
        self.dir_button = ttk.Button(
            self, text="Choose Download Directory", command=self.choose_directory
        )
        self.dir_button.pack(pady=5)
        self.dir_label = ttk.Label(self, text="")
        self.dir_label.pack(pady=5)

        # --- オプション ---
        self.playlist_var = tk.BooleanVar()
        self.playlist_check = ttk.Checkbutton(
            self, text="Download Playlist", variable=self.playlist_var
        )
        self.playlist_check.pack(pady=5)

        self.audio_var = tk.BooleanVar()
        self.audio_check = ttk.Checkbutton(
            self, text="Download Audio Only", variable=self.audio_var
        )
        self.audio_check.pack(pady=5)

        self.maxsize_label = ttk.Label(self, text="Max Filesize (bytes):")
        self.maxsize_label.pack(pady=5)
        self.maxsize_entry = ttk.Entry(self, width=20)
        self.maxsize_entry.pack(pady=5)

        # --- ダウンロードボタン ---
        self.download_button = ttk.Button(self, text="Download", command=self.download)
        self.download_button.pack(pady=20)

    def choose_directory(self):
        path = filedialog.askdirectory(title="Choose Download Directory")
        if path:
            self.dir_label.config(text=path)

    def download(self):
        url = self.url_entry.get()
        save_path = self.dir_label.cget("text")

        if not url or not save_path:
            messagebox.showerror("Error", "URLと保存先を指定してください。")
            return

        # ★ここが革新的！
        # ライブラリに「FFmpegどこ？」と聞くだけで、絶対パスを返してくれます。
        # ユーザーがexeを用意する必要はもうありません。
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        options = {
            "verbose": True,
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            
            # ここでライブラリから取得したパスを渡すだけ！
            "ffmpeg_location": ffmpeg_path,
            
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        }

        if not self.playlist_var.get():
            options["noplaylist"] = True

        if self.audio_var.get():
            options["format"] = "bestaudio/best"
            options["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        max_size = self.maxsize_entry.get()
        if max_size:
            try:
                options["max_filesize"] = int(max_size)
            except ValueError:
                pass
        
        try:
            self.download_button.config(state="disabled")
            self.update()
            
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([url])
                messagebox.showinfo("Success", "ダウンロード完了！")
        
        except Exception as e:
            messagebox.showerror("Error", f"エラー:\n{str(e)}")
        
        finally:
            self.download_button.config(state="normal")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
