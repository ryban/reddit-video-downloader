# reddit-video-downloader
A simple python app with a GUI to download reddit videos on Linux and Windows

If there is already an URL in the clipboard it will use it, try to download the reddit video and open the folder that contains the output video. It will bypass the GUI.

Else: it starts the gui and you can download whatever you want from reddit.

Linux requirements: Supported applications for clipboard feature (xclip or xsel), ffmpeg bin path added to BIN variable, python3-tk

`sudo apt-get install xclip ffmpeg python3-tk`

Windows requirements: Windows 10 build 17063 required for native curl, ffmpeg bin path added to PATH variable

Added more detailed exception handling when debugging through terminal (also to prevent application hang)

Added error and success notifications

Added support for videos without audio

It requires tkinter and clipboard.

Videos that are crossposted will yeild a "'NoneType' object is not subscriptable"

Here is a screenshot to show you the wonderful GUI that comes with it :
![screenshot](https://i.imgur.com/NOkrFTZ.png)
