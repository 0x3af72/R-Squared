# R-Squared

R Squared is a windows program to generate videos from reddit posts.

## Requirements

**Background videos**: To create videos, you need to have background videos which are *over 60 seconds*, which you will link when calling functions from `videomaker.py`.

**Python libraries** (pip install): `librosa`, `moviepy`, `selenium`, `pyttsx3`, `validators`, `win32api`

**FFMPEG**: To install FFMPEG, type in the command `scoop install ffmpeg` in Windows Powershell.

**ImageMagick**: Visit the ImageMagick website and scroll down to download the latest windows binary release. **When running the installer, select the option "install legacy utilities".** [(Install ImageMagick)](https://imagemagick.org/script/download.php)

*[Optional]* **Brave Browser**: It is recommended that you use Brave as the browser for selenium. If you do not wish to install Brave, you can modify `videomaker.py` accordingly. [(Install Brave)](https://brave.com/download/)

## How to use

To use R Squared as a library, you just have to `import videomaker.py`.

If you wish to use the builtin UI provided to you, you can run `ui.py`.

## Videomaker functions

`videomaker.generate_reddit_videos_PTC`: Reads title and comments from top posts in subreddit.

`videomaker.generate_reddit_videos_PD`: Reads title and description from top posts in subreddit.
