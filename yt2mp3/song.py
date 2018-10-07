#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and 
converting Youtube videos to MP3 files with embedded metadata via the 
iTunes API.
yt2mp3/song.py
Brett Stevenson (c) 2018
"""

import os, io, pydub, youtube_dl, requests, logging
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC, TPOS
from mutagen.easyid3 import EasyID3
from colorama import init, Fore, Style
from PIL import Image
from yt2mp3 import util

class Song():
  """
  A class used to represent a song
  ...
  Attributes
  ----------
  data : dict
    a dictionary containing the Youtube URL and song data provided by 
    the iTunes API
  """
  def __init__(self, data):
    self.track = data['track_name']
    self.artist = data['artist_name']
    self.album = data['collection_name']
    self.genre = data['primary_genre_name']
    self.artwork_url = data['artwork_url_100']
    self.track_number = str(data['track_number'])
    self.track_count = str(data['track_count'])
    self.disc_count = str(data['disc_count'])
    self.disc_number = str(data['disc_number'])
    self.release_date = data['release_date']
    self.filename = data['track_name']
    self.video_url = data['video_url']
    
  # Downloads the video at the provided url
  def download(self, verbose=False):
    temp_dir = os.path.expanduser('~/Downloads/Music/temp/')
    if not os.path.exists(temp_dir):
      os.makedirs(temp_dir)
    video_id = self.video_url.split('watch?v=')[-1]
    ydl_opts = dict()
    ydl_opts['outtmpl'] = temp_dir+'%(id)s.%(ext)s'
    ydl_opts['format'] = 'bestaudio/best'
    ydl_opts['quiet'] = True
    if verbose:
      ydl_opts['progress_hooks'] = [util.showProgressBar]
      logging.info(Fore.YELLOW+'↓ '+Style.RESET_ALL+'Downloading...')
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    video_info = None
    with ydl:
      ydl.download([self.video_url])
      video_info = ydl.extract_info(self.video_url, download=False)
    logging.info(Fore.GREEN+'✔ '+Style.RESET_ALL+'Download Complete')
    path = os.path.join(temp_dir, video_id+'.'+video_info['ext'])
    return path

  # Convert the downloaded video file to MP3
  def convertToMP3(self, video):
    logging.info(Fore.BLUE+'♬ '+Style.RESET_ALL+'Converting to MP3')
    artist_dir = os.path.expanduser('~/Downloads/Music/')
    artist_dir = os.path.join(artist_dir, self.artist.replace('/',''))
    if not os.path.exists(artist_dir):
      os.makedirs(artist_dir)
    song_path = os.path.join(artist_dir, self.filename+'.mp3')
    if os.path.exists(song_path):
      self.filename = self.filename+' ('+self.album+')'
      song_path = os.path.join(artist_dir, self.filename+'.mp3')
    pydub.AudioSegment.from_file(video).export(song_path, format='mp3')
    return song_path
  
  # Generates cover-art URL with the specified resolution
  def getCoverArt(self, res):
    img_url = self.artwork_url
    if 'youtube' not in img_url:
      ext = '/%sx%sbb.jpg' % (res, res)
      img_url = '/'.join(img_url.split('/')[:-1])+ext
    img_path = os.path.expanduser('~/Downloads/Music/CoverArt')
    if not os.path.exists(img_path):
      os.makedirs(img_path)
    img_path = os.path.join(img_path, 'cover.jpg')
    response = requests.get(img_url)
    Image.open(io.BytesIO(response.content)).save(img_path)
    return img_path

  # Sets the ID3 metadata of the MP3 file
  def setID3(self, path, res=480):
    tags = ID3(path)
    tags.delete()
    tags.add(TIT2(encoding=3, text=self.track))
    tags.add(TPE1(encoding=3, text=self.artist))
    tags.add(TPE2(encoding=3, text=self.artist))
    tags.add(TALB(encoding=3, text=self.album))
    tags.add(TCON(encoding=3, text=self.genre))
    tags.add(TRCK(encoding=3, text=self.track_number+'/'+self.track_count))
    tags.add(TPOS(encoding=3, text=self.disc_number+'/'+self.disc_count))
    tags.add(TDRC(encoding=3, text=self.release_date[0:4]))
    # Embed cover-art in ID3 metadata
    img_path = self.getCoverArt(res)
    tags.add(APIC(encoding=3, mime='image/jpg', type=3,
                  desc=u'Cover', data=open(img_path, 'rb').read()))
    tags.save()

  # Checks if a duplicate file exists in the output directory
  def fileExists(self):
    path = os.path.expanduser('~/Downloads/Music/')
    path = os.path.join(path, self.artist.replace('/',''), self.filename+'.mp3')
    if os.path.exists(path):
      tags = EasyID3(path)
      if len(self.album) == '' or self.album in tags['album'][0]:
        return True
    return False
