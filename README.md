# YouTube to MP3  

<p align="right">
  <img src="https://img.shields.io/pypi/v/yt2mp3.svg" alt="PyPi"/>
  <img src="https://pypip.in/py_versions/yt2mp3/badge.svg" alt="PyPI - Python Version"/>
  <a href="https://github.com/tterb/yt2mp3/blob/master/LICENSE"><img src="https://img.shields.io/github/license/tterb/yt2mp3.svg" alt="License"/></a>
</p>  

<p align="center">
  <img src="https://user-images.githubusercontent.com/16360374/42131622-f496ba52-7cba-11e8-9891-cf0835793c4d.gif" width="700"/>
</p>

## Description  
This program aims to simplify the process of downloading and converting Youtube videos to MP3 files from the command-line. All you need is the video URL or the name of the artist/track you're looking for.  
The program will attempt to retrieve data for a song matching the provided input by querying the iTunes API and then use the data to find a corresponding YouTube video, if a URL is not provided.  
The video will then be downloaded, converted, and the retrieved data will be used to populate the metadata of the MP3.  
Additionally, if a URL is provided and no match is found for the song data, the program will prompt the user for the track/artist and use the YouTube thumbnail as the album artwork.  

## Install  
You can install the program with the following command:  
```sh
pip install yt2mp3
```

## Usage  
The program can executed via Python 3 as follows:  
```sh
yt2mp3 [-options]
```

#### Options:  
| Arguments        |                                                  |
|------------------|--------------------------------------------------|
| `-t, --track`    | Specify the track name query                     |
| `-a, --artist`   | Specify the artist name query                    |
| `-u, --url`      | Specify a Youtube URL or ID                      |
| `-q, --quiet`    | Suppress program command-line output             |
| `-v, --verbose` | Display a command-line progress bar              |
| `-h, --help`     | Displays information on usage and functionality  |  

Once complete, the resulting MP3 file will be saved to your *Downloads* directory, with the following file-structure `Music/{artist}/{track}.mp3`.  

***Note:*** Displaying the progress bar currently has a significant impact on download performance, due to [#180](https://github.com/nficano/pytube/issues/180).  


## Development  
You can download and install the app with the following commands:  

```sh
# Clone the repository / most up to date is on saftyBranch
git clone https://github.com/tterb/yt2mp3

# Navigate to the directory
cd yt2mp3

# Install program dependencies
pip install -r requirements.txt
```

<br>  
