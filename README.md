# YouTube to MP3

<p align="right">
<a href="https://github.com/tterb/YouTube-to-MP3/blob/master/LICENSE"><img src="https://img.shields.io/github/license/tterb/YouTube-to-MP3.svg" alt="License"/></a>
<a href="https://www.python.org/downloads/release/python-360/"><img src="https://img.shields.io/badge/Python-3.6-blue.svg" alt="Python version"/></a>
</p>  

## Description  
A program that simplifies the process of downloading and converting Youtube videos to MP3 files from the command-line. All you need is the video URL or the name of the artist/track you're looking for.  
Once the file is downloaded the program will also attempt to embed the output file with the appropriate metadata and cover art via the [iTunes API](https://github.com/spaceisstrange/itunespy).  


## Install  
You can download and install the app via the following commands:  

```sh
# Clone the repository / most up to date is on saftyBranch
git clone https://github.com/tterb/YouTube-to-MP3

# Navigate to the directory
cd YouTube-to-MP3

# Install program dependencies
pip install -r requirements.txt
```

## Usage  
The program can executed via Python 3 as follows:  
```sh
python yt2mp3.py [-options]
```

The resulting MP3 file will be saved to your *Downloads* directory, with the following file-structure `Music/{artist}/{track}.mp3`.  

#### Options:  

| Arguments        |                                                    |
|:----------------:|----------------------------------------------------|
| `-t, --track`    | Specify the track name query                       |
| `-a, --artist`   | Specify the artist name query                      |
| `-u, --url`      | Specify a Youtube URL or ID                        |
| `-q, --quiet`    | Suppress program command-line output               |
| `-p, --progress` | Display a command-line progress bar                |
| `-h, --help`     | Displays information on usage and functionality    |  

***Note:*** Displaying the progress bar currently has a significant impact on download performance, due to [#180](https://github.com/nficano/pytube/issues/180).

<br>  

----

## *Disclaimer*
This program is distributed with the sole intent of being used on non-copyrighted material or copyrighted material for which the user holds the copyright. Use of this program outside of the aforementioned conditions is not permitted.
