#!/usr/bin/env python
# Windows 10 build 17063 required for native curl
from tkinter import Entry, Button, Tk, messagebox
import tkinter.font as tkFont
import tkinter.ttk
import requests
import os
import pathlib
import subprocess
import sys
import clipboard
from urllib.request import urlopen, HTTPError
import platform
import string

osys = platform.system()
real_path = pathlib.Path(__file__).parent.resolve()


class RedditDownloader:
    def __init__(self):
        self.url = clipboard.paste()
        self.download_completed = False
        # use UA headers to prevent 429 error
        self.headers = {
            "User-Agent": "My User Agent 1.0",
            "From": "testyouremail@domain.com"
        }

    def run(self):
        self.determine_url()
        if not self.download_completed:
            #setup UI
            self.win = Tk()
            self.win.attributes("-fullscreen", False)
            myFont = tkFont.Font(family="Mono", size=15, weight="bold")
            self.win.title("Reddit-video-downloader")
            self.win.geometry("1280x90")
            self.win.configure(background="black")

            self.urlInput = Entry(self.win)
            self.urlInput.place(x=150, y=20, height=50, width=980)

            bDownload = Button(self.win, text="Download", font=myFont, command=self.get_url_and_download)
            bDownload.place(x=20, y=20, height=50, width=120)

            bQuitter = Button(self.win, text="Exit", font=myFont, command=self.quit)
            bQuitter.place(x=1140, y=20, height=50, width=120)
            self.win.mainloop()

    def get_url_and_download(self):
        self.url = self.urlInput.get()
        self.determine_url()

    def determine_url(self):
        if isinstance(self.url, str) and (str(self.url).startswith("https://www.reddit.com") or str(self.url).startswith("https://old.reddit.com")):
            self.reddit_downloader()
        elif isinstance(self.url, str) and str(self.url).startswith("https://v.redd.it"):
            # resolve url and request with correct url
            self.resolve_vreddit_url()

    def resolve_vreddit_url(self):
        self.url = requests.get(self.url, headers=self.headers).url
        self.reddit_downloader()

    def open_output_dir(self, path):
        if osys == "Windows":
            # Calling explorer directly was giving me a 116 error code for some reason
            # With explorer we could use /select to make the new file highlighted
            os.startfile(str(path), 'explore')
            return
        elif osys == "Linux":
            opener = "xdg-open"
        elif osys == "Darwin":
            opener = "open"
        subprocess.check_call([opener, str(path)])

    def reddit_downloader(self):
        try:
            self.download_completed = True
            json_url = self.url + ".json"
            data = requests.get(json_url, headers=self.headers).json()
            media_data = data[0]["data"]["children"][0]["data"]["media"]
            title = data[0]["data"]["children"][0]["data"]["title"]

            # sanitize title
            for char in string.punctuation:
                title = title.replace(char, "")

            output_dir = real_path / "Output"
            video_path = (output_dir / title).with_suffix(".mp4")
            if not output_dir.exists():
                output_dir.mkdir(parents=True)

            video_url = media_data["reddit_video"]["fallback_url"]
            audio_url = video_url.split("DASH_")[0] + "audio"
            print("Video URL: ", video_url)
            inputs = ["-i", "video.mp4"]
            try:
                urlopen(audio_url)
                inputs.extend(["-i", "audio.wav"])
            except HTTPError as err:
                if err.code == 403:
                    audio_url = None

            subprocess.check_call(["curl", "-o", "video.mp4", video_url])
            if audio_url:
                subprocess.check_call(["curl", "-o", "audio.wav", audio_url])

            # add ffmpeg bin directory to PATH environment variable or full path to binary when ffmpeg is called with os.system()
            subprocess.check_call(["ffmpeg", "-y"] + inputs + ["-c:v", "copy", "-strict", "experimental", str(video_path)])
            video_file = real_path / "video.mp4"
            audio_file = real_path / "audio.wav"
            print("Removing {}".format(video_file))
            video_file.unlink()
            print("Removing {}".format(audio_file))
            audio_file.unlink()
            self.open_output_dir(output_dir)
        except Exception as err:
            messagebox.showerror("Error", err)
            e_type, exc_obj, exc_tb = sys.exc_info()
            print(err, e_type, exc_tb.tb_lineno)

    def quit(self):
        self.win.destroy()


if __name__ == "__main__":
    RedditDownloader().run()
