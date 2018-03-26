# YouTube to MP3

## Description  
A program that simplifies the process of downloading and converting Youtube videos to MP3 files from the command-line.

## Usage  
The program can be run using Python 3 as follows:
```sh
python yt-to-mp3.py <video-url>
```
The resulting MP3 file will be saved to your *Downloads* directory, by default.  

#### Options:  

| Arguments   |                                                    |
|:----------:|----------------------------------------------------|
| -i, --info | Allows for the interactive setting of MP3 metadata |
| -h, --help | Displays information on usage and functionality    |

## Dependencies  
The following dependencies must be installed to utilize the program:  
  * [**Python 3**](https://www.python.org/download/releases/3.0/)  
  * [**pafy**](https://github.com/mps-youtube/pafy)  
  * [**pydub**](https://github.com/jiaaro/pydub)  
  * [**mutagen**](https://github.com/quodlibet/mutagen)  

Additionally, if you have Python 3 installed, you can install all dependencies with the following command:  

```sh
pip install -r requirements.txt
```
  
  
----  

## *Disclaimer*  
This program should only be used on non-copyrighted material or copyrighted material for which you hold the copyright. Use of this program outside of the aforementioned conditions is not permitted.