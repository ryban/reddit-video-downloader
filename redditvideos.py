#!/usr/bin/env python
# Windows 10 build 17063 required for native curl
from tkinter import Entry,Button,Tk,messagebox
import tkinter.font as tkFont
import tkinter.ttk
import requests
import os
import sys
import clipboard
from urllib.request import urlopen, HTTPError
import platform

osys = platform.system()
real_path = os.path.dirname(os.path.realpath(__file__))

class RedditDownloader:
    def __init__(self):
        self.url = clipboard.paste()
        if isinstance(self.url, str) and (str(self.url).startswith("https://www.reddit.com") or str(self.url).startswith("https://old.reddit.com")):
            #download video directly, no ui
            self.reddit_downloader()
        else:
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
        self.reddit_downloader()

    def reddit_downloader(self):
        try:
            # use UA headers to prevent 429 error
            headers = {
                "User-Agent": "My User Agent 1.0",
                "From": "testyouremail@domain.com"
            }
            json_url = self.url + ".json"
            data = requests.get(json_url, headers=headers).json()
            media_data = data[0]["data"]["children"][0]["data"]["media"]
            title = data[0]["data"]["children"][0]["data"]["title"]

            # sanitize title
            invalid = """<>:"/\|?*. """
            for char in invalid:
                title = title.replace(char, "")

            video_path  = os.path.join(real_path,"Output",title)+".mp4"
            folder_path = os.path.join(real_path,"Output")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            video_url = media_data["reddit_video"]["fallback_url"]
            audio_url = video_url.split("DASH_")[0] + "audio"

            # audio may not exist
            try:
                urlopen(audio_url)
            except HTTPError as err:
                if err.code == 403:
                    # no audio, download video to Output directly
                    os.system("curl -o {} {}".format(video_path, video_url))
                    messagebox.showinfo("Success", "{} was downloaded.".format(self.url))
                    return

            os.system("curl -o video.mp4 {}".format(video_url))
            os.system("curl -o audio.wav {}".format(audio_url))

            if osys == "Windows":
                # add ffmpeg bin directory to PATH environment variable or full path to binary in the next line
                os.system("ffmpeg.exe -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -strict experimental \""+video_path+"\"")
                os.system("start " + folder_path)
            elif osys == "Linux":
                os.system("ffmpeg -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -strict experimental '"+video_path+"'")
                os.system("xdg-open " + folder_path)
            else:
                messagebox.showerror("Error", "{} is not supported".format(osys))
                return
            messagebox.showinfo("Success", "{} was downloaded.".format(self.url))
        except Exception as err:
            messagebox.showerror("Error", err)
            e_type, exc_obj, exc_tb = sys.exc_info()
            print(err, e_type, exc_tb.tb_lineno)

    def quit(self):
        self.win.destroy()
        return


if __name__ == "__main__":
    RedditDownloader()
