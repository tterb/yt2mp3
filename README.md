# YouTube to MP3  

<p align="right">
  <img src="https://img.shields.io/pypi/v/yt2mp3.svg" alt="PyPi"/>
  <img src="https://pypip.in/py_versions/yt2mp3/badge.svg" alt="PyPI - Python Version"/>
  <a href="https://github.com/tterb/yt2mp3/blob/master/LICENSE"><img src="https://img.shields.io/github/license/tterb/yt2mp3.svg" alt="License"/></a>
</p>  

## Description  
A program that simplifies the process of downloading and converting Youtube videos to MP3 files from the command-line. All you need is the video URL or the name of the artist/track you're looking for.  
Once downloaded, the program will also embed the output file with the appropriate metadata and cover art via the iTunes API.  


## Install  
You can download and install the app with the following commands:  

```sh
# Clone the repository / most up to date is on saftyBranch
git clone https://github.com/tterb/yt2mp3

# Navigate to the directory
cd yt2mp3

# Install program dependencies
pip install -r requirements.txt
```

## Usage  
The program can executed via Python 3 as follows:  
```sh
python yt2mp3.py [-options]
```

Once complete, the resulting MP3 file will be saved to your *Downloads* directory, with the following file-structure `Music/{artist}/{track}.mp3`.  

#### Options:  

| Arguments        |                                                  |
|:----------------:|--------------------------------------------------|
| `-t, --track`    | Specify the track name query                     |
| `-a, --artist`   | Specify the artist name query                    |
| `-u, --url`      | Specify a Youtube URL or ID                      |
| `-q, --quiet`    | Suppress program command-line output             |
| `-p, --progress` | Display a command-line progress bar              |
| `-h, --help`     | Displays information on usage and functionality  |  

***Note:*** Displaying the progress bar currently has a significant impact on download performance, due to [#180](https://github.com/nficano/pytube/issues/180).  

<br>  

----

## *Disclaimer*
This program is distributed with the sole intent of being used on non-copyrighted material or copyrighted material for which the user holds the copyright. Use of this program outside of the aforementioned conditions is not permitted.  
