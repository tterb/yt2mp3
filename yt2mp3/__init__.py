#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and converting Youtube videos to MP3 files with embedded metadata via the iTunes API.
yt2mp3/__init__.py
Brett Stevenson (c) 2018
"""

import sys, os, re, argparse, pytube, pydub, itunespy, urllib, requests, io, ssl, glob, shutil, cursesmenu, logging, string
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3,APIC,TIT2,TPE1,TPE2,TALB,TCON,TRCK,TDRC,TPOS
from urllib.request import Request, urlopen
from collections import defaultdict
from PIL import Image
from pathlib import Path
from bs4 import BeautifulSoup

# Get song data from iTunes API
def getSongData(track, artist, exit=True):
  try:
    if track and artist:
      for s in itunespy.search_track(track):
        if s.artist_name.lower() == artist.lower():
          return s
    elif track:
      return itunespy.search_track(track)
    elif artist:
      songs = []
      artists = itunespy.search_artist(artist)[0]
      for album in artists.get_albums():
        for s in album.get_tracks():
          songs.append(s)
      return songs
    # Attempt to find a close match if no exact matches found
    song = itunespy.search(' '.join([track,artist]))[0]
    if song:
      return song
  except LookupError as e:
    if exit:
      logging.warning(str(e))
      sys.exit()

# Attempt to retrieve song data from URL
def getVideoData(url):
  # Get YouTube video title
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  title = soup.find('span', { 'class':'watch-title' }).get_text().strip()
  # Remove parenthesis contents and commonly added words
  title = re.sub(re.compile(r'\([^)]*\)|ft|feat|\blyrics?\b|official|video|audio', re.IGNORECASE), '', title)
  title = title.translate(str.maketrans('','',string.punctuation))
  title = ' '.join(title.split())
  # Query iTunes API
  try:
    return itunespy.search(title)[0]
  except LookupError:
    pass

# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  if selection >= len(options):
    sys.exit()
  return selection
  
# Scrapes youtube for a video that has track and artist in the name
def getURL(track, artist):
  query = urllib.parse.quote(track+" "+artist)
  url = 'https://www.youtube.com/results?search_query=' + query
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  results = []
  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    results.append('https://www.youtube.com' + vid['href'])
  return results[0]

# Downloads songs from youtube, songs must be a list of track objects
def download(url, progressBar=False):
  tempDir = Path.home()/'Downloads'/'Music'/'temp'
  if not os.path.exists(tempDir):
    os.makedirs(tempDir)
  id = url.split('watch?v=')[-1]
  yt = pytube.YouTube(url)
  if progressBar:
    logging.info(' Downloading...')
    yt.register_on_progress_callback(showProgressBar)
  yt.streams.filter(subtype='mp4', progressive=True).first().download(tempDir, id)
  logging.info(' ✔ Download Complete')
  return glob.glob(os.path.join(str(tempDir), id+'.*'))[0]

# Convert the downloaded video file to MP3
def convertToMP3(tempPath, song):
  logging.info(' ♬ Converting to MP3')
  outputDir = Path.home()/'Downloads'/'Music'/song.artist
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  path = os.path.join(outputDir,song.track+'.mp3')
  pydub.AudioSegment.from_file(tempPath).export(path, format='mp3')
  shutil.rmtree(Path(tempPath).parent)
  return path

# Sets the ID3 metadata of the MP3 file
def setData(path, song):
  meta = ID3(path)
  meta.delete()
  meta.add(TIT2(encoding=3, text=song.track))
  meta.add(TPE1(encoding=3, text=song.artist))
  meta.add(TPE2(encoding=3, text=song.artist))
  meta.add(TALB(encoding=3, text=song.album))
  meta.add(TCON(encoding=3, text=song.genre))
  meta.add(TRCK(encoding=3, text=song.track_number+'/'+song.track_count))
  meta.add(TPOS(encoding=3, text=song.disc_number+'/'+song.disc_count))
  meta.add(TDRC(encoding=3, text=song.release_date[0:4]))
  meta.save()
  # Embed cover-art in ID3 metadata
  meta = MP3(path, ID3=ID3)
  imgURL = song.artwork_url
  dir = Path.home()/'Downloads'/'Music'/'CoverArt'
  os.system('mkdir -p %s' % (dir))
  imgPath = os.path.join(dir,'cover.jpg')
  response = requests.get(imgURL)
  img = Image.open(io.BytesIO(response.content))
  img.save(imgPath)
  meta.tags.add(APIC(encoding=3, mime='image/jpg', type=3, 
                     desc=u'Cover', data=open(imgPath,'rb').read()))
  meta.save()
  shutil.rmtree(dir)

# Display a download progress bar
def showProgressBar(stream, chunk, file_handle, bytes_remaining):
  total = stream.filesize
  iter = ((total-bytes_remaining)/total)
  percent = ('{0:.1f}').format(iter*100)
  progress = int(50*iter)
  bar = '█' * progress + '-' * (50 - progress)
  sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=bar, percent=percent))
  sys.stdout.flush()


class Song(object):
  def __init__(self, data):  
    self.track = data['track_name']
    self.artist = data['artist_name']
    self.video_url = data['video_url']
    self.album = data['collection_name']
    self.genre = data['primary_genre_name']
    self.artwork_url = data['artwork_url_100']
    self.track_number = str(data['track_number'])
    self.track_count = str(data['track_count'])
    self.disc_count = str(data['disc_count'])
    self.disc_number = str(data['disc_number'])
    self.release_date = data['release_date']
