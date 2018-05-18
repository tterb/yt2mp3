# YouTube to MP3

<p align="right"><a href="https://www.python.org/downloads/release/python-360/"><img src="https://img.shields.io/badge/Python-3.6-blue.svg"/></a></p>  

## Description
A program that simplifies the process of downloading and converting Youtube videos to MP3 files from the command-line. Additionally, the program also utilizes the iTunes API to populate the metadata of output files.  


## Install  
If Python 3 is installed, you can install the program dependencies with the following command:  

```sh
pip install -r requirements.txt
```

## Usage  
The program can executed via Python 3 as follows:  
```sh
python yt2mp3.py [-options]
```
The resulting MP3 file will be saved to your *Downloads* directory, with the following file structure `Music/{artist}/{track}.mp3`.  

#### Options:  

| Arguments      |                                                    |
|:--------------:|----------------------------------------------------|
| `-t, --track`  | Specify the track name query                       |
| `-a, --artist` | Specify the artist name query                      |
| `-u, --url`    | Allows the user to specify a Youtube URL           |
| `-h, --help`   | Displays information on usage and functionality    |  


<br>  

----

## *Disclaimer*
This program is distributed with the sole intent of being used on non-copyrighted material or copyrighted material for which the user holds the copyright. Use of this program outside of the aforementioned conditions is not permitted.
