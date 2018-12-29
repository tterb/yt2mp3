#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/util.py
Brett Stevenson (c) 2018
"""

import sys, os, re, youtube_dl, itunespy, urllib, ssl, shutil, cursesmenu, logging, string
from urllib.request import Request, urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from colorama import Fore, Style

def get_song_data(data, collection=False):
  """
  Employs a variety of methods for retrieving song data for the provided input
  Args:
    data: A dict of values provided by the user
    collection: A boolean representing whether an album has been specified
  Returns:
    A dict of the retrieved song data
  """
  if data['video_url']:
    url = data['video_url']
    result = get_video_data(get_video_title(url))
    if not result:
      data['track_name'] = input(' Track: ')
      data['artist_name'] = input(' Artist: ')
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+url.split('watch?v=')[-1]+'/maxresdefault.jpg'
      result = get_itunes_data(data, False)
    if result:
      data = defaultdict(str, result.__dict__)
      data['video_url'] = url
  elif data['artist_name'] and data['track_name']:
    result = get_itunes_data(data)
    if result:
      data = defaultdict(str, result.__dict__)
      data['video_url'] = get_video_url(data, collection)
  else:
    songs = get_itunes_data(data)
    if data['track_name']:
      options = ['%-30.25s %10.25s' % (s.track_name, s.artist_name) for s in songs]
    elif data['artist_name']:
      options = [s.track_name for s in songs]
    result = songs[show_menu(options)]
    data = defaultdict(str, result.__dict__)
    data['video_url'] = get_video_url(data, collection)
  return data

def get_itunes_data(data, exit_fail=True):
  """
  Attempts to retrieve song data from the iTunes API
  Args:
    data: A dict of values provided by the user
    exit_fail: A bool specifying if the program should exit if no match
  Returns:
    A dict of song data retrieved from the iTunes API, if a match is found
  Raises:
    LookupError: If a match isn't found using the iTunes API
  """
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

def get_video_data(title):
  """
  Attempts to retrieve song data from the video title
  Args:
    title: A string containing the title of the YouTube video
  Returns:
    A dict of song data if a match is found using the iTunes APi
  Raises:
    LookupError: If a match isn't found using the iTunes API
  """
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
  
def get_video_url(data, collection=False):
  """
  Scrapes YouTube for a video matching the user input and iTunes track data
  Args:
    data: A dict of values provided by the user
    collection: A boolean representing whether an album has been specified
  Returns:
    The URL of a YouTube video matching the provided values
  """
  query = urllib.parse.quote(data['track_name']+' '+data['artist_name'])
  url = 'https://www.youtube.com/results?search_query='+query
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl.create_default_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  results = list()
  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    url = 'https://www.youtube.com' + vid['href']
    if validate_url(url):
      # Check that video time is similar to the track time
      if 'track_time' in data.keys():
        target = data['track_time']//1000
        vid_time = youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)['duration']
        if abs(target-vid_time) < 20:
          if collection:
            video_data = defaultdict(str, get_video_metadata(url))
            if data['collection_name'].lower() in video_data['album'].lower():
              return url
          else:
            return url
      # Check video metadata if album has been specified by user
      elif collection:
        video_data = defaultdict(str, get_video_metadata(url))
        if data['collection_name'].lower() in video_data['album'].lower():
          return url
      return url

def validate_url(url, playlist=False):
  """
  Confirms the validity of the provided YouTube video/playlist URL
  Args:
    url: A YouTube video/playlist URL
    playlist: A boolean flag to determine playlist URL
  Returns:
    A bool indicating the validity of the provided URL
  """
  pattern = r'^(https?\:\/\/)?(www\.)?(youtube\.com\/watch\?v=([a-zA-Z0-9_\-]{11})|youtu\.?be\/([a-zA-Z0-9_\-]{11}))$'
  if playlist:
    pattern = r'^(https?\:\/\/)?(www\.)?youtube\.com\/((playlist\?list=.*)|(watch\?list=.*&v=.*)|(watch\?v=[a-zA-Z0-9_\-]{11}&list=.*))$'
  return bool(re.match(pattern, str(url)))


def get_video_title(url):
  """
  Retrieves the title of the provided YouTube video
  Args:
    url: A YouTube video URL
  Returns:
    A string containing the title of the provided YouTube video
  """
  return youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)['title']


def get_video_metadata(url):
  """
  Attempts to retrieve relavent data from the YouTube video metadata
  Args:
    url: A YouTube video URL
  Returns:
    A dict of the retrieved song data
  """
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl.create_default_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  video_data = {}
  section = soup.find('ul', attrs={'class': 'watch-extras-section'})
  for item in section.find_all('li', recursive=False):
    key = next(item.find('h4').stripped_strings).lower()
    video_data[key] = next(item.find('li').stripped_strings).lower()
  return video_data
  

def get_video_list(url):
  """
  Retrieves a list of video URL's from the playlist URL
  Args:
    url: A YouTube playlist URL
  Returns:
    A list of individual URL's for each video in the playlist
  """
  results = youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)
  return [i['webpage_url'] for i in results['entries']]

def show_menu(options):
  """
  Displays an interactive menu of matching song entries
  Args:
    options: A list of potential matches from the iTunes API
  Returns:
    The index of the menu entry selected by the user
  """
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  if selection >= len(options):
    sys.exit()
  return selection

def show_progressbar(status):
  """
  Prints a progress-bar for the download status
  Args:
    status: A dict indicating the status of the active download
  """
  progress = int(50*(status['downloaded_bytes']/status['total_bytes']))
  percent = ('{0:.1f}').format(progress*2)
  bar = '▓'*progress+'-'*(50 - progress)
  sys.stdout.write(Fore.YELLOW+'↳'+Style.RESET_ALL+' |{bar}| {percent}%\r'.format(bar=bar, percent=percent))
  sys.stdout.flush()
  if status['status'] == 'finished':
    logging.info('')


def cleanup():
  """
  Cleans up temporary directories/files used by the program
  """
  directory = os.path.expanduser('~/Downloads/Music/')
  video_dir = os.path.join(directory, 'temp/')
  cover_dir = os.path.join(directory, 'CoverArt/')
  if os.path.isdir(video_dir):
    shutil.rmtree(video_dir)
  if os.path.isdir(cover_dir):
    shutil.rmtree(cover_dir)
