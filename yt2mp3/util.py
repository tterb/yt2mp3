#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and 
converting Youtube videos to MP3 files with embedded metadata via the 
iTunes API.
yt2mp3/util.py
Brett Stevenson (c) 2018
"""

import sys, os, re, youtube_dl, pydub, itunespy, urllib, requests, io, ssl, glob, shutil, cursesmenu, logging, string
from urllib.request import Request, urlopen
from colorama import init, Fore, Style
from collections import defaultdict
from bs4 import BeautifulSoup

# Uses the provided data to find a match in iTunes API
def getSongData(data):
  if data['video_url']:
    url = data['video_url']
    result = getVideoData(getVideoTitle(url))
    if not result:
      data['track_name'] = input(' Track: ')
      data['artist_name'] = input(' Artist: ')
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+url.split('watch?v=')[-1]+'/maxresdefault.jpg'
      result = getiTunesData(data, False)
    if result: 
      data = defaultdict(str, result.__dict__)
      data['video_url'] = url
  elif data['artist_name'] and data['track_name']:
    result = getiTunesData(data)
    if result:
      data = defaultdict(str, result.__dict__)
      data['video_url'] = getVideoURL(data)
  else:
    songs = getiTunesData(data)
    if data['track_name']:
      options = ['%-30.25s %10.25s' % (s.track_name, s.artist_name) for s in songs]
    elif data['artist_name']:
      options = [s.track_name for s in songs]
    result = songs[showMenu(options)]
    data = defaultdict(str, result.__dict__);
    data['video_url'] = getVideoURL(data)
  return data

# Attempt to retrieve song data from iTunes API
def getiTunesData(data, exit_fail=True):
  try:
    if data['track_name'] and data['artist_name']:
      for song in itunespy.search_track(data['track_name']):
        if data['artist_name'].lower() == song.artist_name.lower():
          if 'collection_name' not in data.keys():
            return song
          elif data['collection_name'].lower() in song.collection_name.lower(): 
            return song
    elif data['track_name']:
      return itunespy.search_track(data['track_name'])
    elif data['artist_name']:
      songs = []
      artists = itunespy.search_artist(data['artist_name'])[0]
      for album in artists.get_albums():
        for song in album.get_tracks():
          songs.append(song)
      return songs
    # Attempt to find a close match if no exact matches
    song = itunespy.search(' '.join([data['track_name'], data['artist_name'], data['collection_name']]))[0]
    if song:
      return song
  except LookupError as err:
    if exit_fail:
      logging.warning(Fore.RED+'✘ '+Style.RESET_ALL+' %s', err)
      sys.exit()

# Attempt to retrieve song data from the video title
def getVideoData(title):
  # Remove parenthesis, punctuation and nondescript words
  pattern = r'\([^)]*\)|\[[^]]*\]|ft(\.)?|feat(\.)?|\blyrics?\b|official|video|audio|h(d|q)'
  keywords = re.sub(pattern, '', str(title), flags=re.I)
  keywords = keywords.translate(str.maketrans('', '', string.punctuation))
  keywords = ' '.join(keywords.split())
  # Query iTunes API
  try:
    return itunespy.search(keywords)[0]
  except LookupError:
    pass

# Ensures the validity of provided YouTube URLs
# TODO issues with some URL formats
def validateURL(url, playlist=False):
  pattern = r'^(https?\:\/\/)?(www\.)?(youtube\.com\/watch\?v=([a-zA-Z0-9_\-]{11})|youtu\.?be\/([a-zA-Z0-9_\-]{11}))$'
  if playlist:
    pattern = r'^(https?\:\/\/)?(www\.)?youtube\.com\/((playlist\?list=.*)|(watch\?list=.*&v=.*)|(watch\?v=[a-zA-Z0-9_\-]{11}&list=.*))$'
  return bool(re.match(pattern, str(url)))

# Get YouTube video title
def getVideoTitle(url):
  return youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)['title']
  
# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  if selection >= len(options):
    sys.exit()
  return selection

# Scrapes YouTube for a video containing the track and artist
def getVideoURL(data):
  query = urllib.parse.quote(data['track_name']+' '+data['artist_name'])
  url = 'https://www.youtube.com/results?search_query=' + query
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  results = []
  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    url = 'https://www.youtube.com' + vid['href']
    if validateURL(url):
      return url
  if data['collection_name']:
    for url in results:
      video_data = defaultdict(str, getVideoMetadata(url))
      if data['collection_name'].lower() in video_data['album'].lower():
        return url
  return results[0]

def getVideoMetadata(url):
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  video_data = {}
  section = soup.find('ul', attrs={'class': 'watch-extras-section'})
  for li in section.find_all('li', recursive=False):
      key = next(li.find('h4').stripped_strings).lower()
      video_data[key] = next(li.find('li').stripped_strings).lower()
  return video_data

# Returns a list of video URLs in playlist
def getVideoList(url):
  results = youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)
  return [i['webpage_url'] for i in results['entries']]

# Displays a download progress bar
def showProgressBar(status):
  progress = int(50*(status['downloaded_bytes']/status['total_bytes']))
  percent = ('{0:.1f}').format(progress*2)
  bar = '▓'*progress+'-'*(50 - progress)
  sys.stdout.write(Fore.YELLOW+'↳'+Style.RESET_ALL+' |{bar}| {percent}%\r'.format(bar=bar, percent=percent))
  sys.stdout.flush()
  if status['status'] == 'finished':
    logging.info('')

# Removes temporary video and cover-art files 
def cleanup():
  directory = os.path.expanduser('~/Downloads/Music/')
  video_dir = os.path.join(directory, 'temp/')
  cover_dir = os.path.join(directory, 'CoverArt/')
  if os.path.isdir(video_dir):
    shutil.rmtree(video_dir)
  if os.path.isdir(cover_dir):
    shutil.rmtree(cover_dir)
