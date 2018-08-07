#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and 
converting Youtube videos to MP3 files with embedded metadata via the 
iTunes API.
yt2mp3/__init__.py
Brett Stevenson (c) 2018
"""

import sys, os, re, pytube, pydub, itunespy, urllib, requests, io, ssl, glob, shutil, cursesmenu, logging, string
from urllib.request import Request, urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from yt2mp3.song import Song


def getSongData(data, overwrite=False):
  if data['video_url']:
    url = data['video_url']
    title = pytube.YouTube(url).title
    result = getVideoData(title)
    if not result: 
      data['track_name'] = input(' Track: ')
      data['artist_name'] = input(' Artist: ')
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+url.split('watch?v=')[-1]+'/maxresdefault.jpg'
      result = getiTunesData(data['track_name'], data['artist_name'], False)
      if result: 
        data = defaultdict(str, result.__dict__)
        data['video_url'] = url
  elif data['artist_name'] or data['track_name']:
    result = getiTunesData(data['track_name'], data['artist_name'])
    if result: 
      data = defaultdict(str, result.__dict__)
      data['video_url'] = getVideoURL(data['track_name'], data['artist_name'])
  return data

# Get song data from iTunes API
def getiTunesData(track, artist, exit_fail=True):
  try:
    if track and artist:
      for song in itunespy.search_track(track):
        if song.artist_name.lower() == artist.lower():
          return song
    elif track:
      return itunespy.search_track(track)
    elif artist:
      songs = []
      artists = itunespy.search_artist(artist)[0]
      for album in artists.get_albums():
        for song in album.get_tracks():
          songs.append(song)
      return songs
    # Attempt to find a close match if no exact matches
    song = itunespy.search(' '.join([track, artist]))[0]
    if song:
      return song
  except LookupError as err:
    if exit_fail:
      logging.warning(" ✘ %s", err)
      sys.exit()

# Attempt to retrieve song data from the video title
def getVideoData(title):
  # Remove parenthesis, punctuation and nondescript words
  pattern = r'\([^)]*\)|\[[^]]*\]|ft(\.)?|feat(\.)?|\blyrics?\b|official|video|audio|h(d|q)'
  print(title)
  keywords = re.sub(pattern, '', str(title), flags=re.I)
  keywords = keywords.translate(str.maketrans('', '', string.punctuation))
  keywords = ' '.join(keywords.split())
  print(keywords)
  sys.exit()
  # Query iTunes API
  try:
    return itunespy.search(keywords)[0]
  except LookupError:
    pass

# Get YouTube video title
def getVideoTitle(url):
  return pytube.YouTube(url).title

# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  if selection >= len(options):
    sys.exit()
  return selection

# Scrapes YouTube for a video with the track and artist
def getVideoURL(track, artist):
  query = urllib.parse.quote(track+" "+artist)
  url = 'https://www.youtube.com/results?search_query=' + query
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  results = []
  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    results.append('https://www.youtube.com' + vid['href'])
  return results[0]

# Checks if a duplicate file exists in the output directory
def fileExists(artist, track):
  path = os.path.expanduser('~/Downloads/Music/')
  path = os.path.join(path, artist, track+'.mp3')
  return os.path.exists(path)

# Downloads the video at the provided url
# def download(url, verbose=False):
#   temp_dir = os.path.expanduser('~/Downloads/Music/temp/')
#   if not os.path.exists(temp_dir):
#     os.makedirs(temp_dir)
#   video_id = url.split('watch?v=')[-1]
#   youtube = pytube.YouTube(url)
#   if verbose:
#     logging.info(' Downloading...')
#     youtube.register_on_progress_callback(showProgressBar)
#   youtube.streams.filter(subtype='mp4', progressive=True).first().download(temp_dir, video_id)
#   logging.info(' ✔ Download Complete')
#   return os.path.join(temp_dir, video_id+'.mp4')

# Returns a list of video URLs in playlist
def getVideoList(url):
  youtube = pytube.Playlist(url)
  video_list = ['https://www.youtube.com'+i for i in youtube.parse_links()]
  return video_list

# Downloads each of the songs from the playlist
# def downloadPlaylist(videos, verbose=False, overwrite=False):
#   for i, url in enumerate(videos):
#     title = getVideoTitle(url)
#     logging.info('%s of %s: %s', (i+1), len(videos), title)
#     result = getVideoData(title)
#     video_id = url.split('watch?v=')[-1]
#     if not result:
#       data = defaultdict(str)
#       data['track_name'] = input(' Track: ')
#       data['artist_name'] = input(' Artist: ')
#       data['video_url'] = url
#       data['artwork_url_100'] = 'https://img.youtube.com/vi/'+video_id+'/maxresdefault.jpg'
#       result = getiTunesData(data['track_name'], data['artist_name'])
#     if result:
#       song = Song(defaultdict(str, result.__dict__))
#       song.video_url = url
#     else:
#       song = Song(data)
#     if overwrite or not fileExists(data['artist_name'], data['track_name']):
#       video_path = song.download(verbose)
#       song_path = song.convertToMP3(video_path)
#       song.setID3(song_path)
#   logging.info(' ✔ Done')

# Display a download progress bar
def showProgressBar(stream, _chunk, _file_handle, bytes_remaining):
  total = stream.filesize
  current = ((total-bytes_remaining)/total)
  percent = ('{0:.1f}').format(current*100)
  progress = int(50*current)
  status = '█' * progress + '-' * (50 - progress)
  sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
  sys.stdout.flush()
