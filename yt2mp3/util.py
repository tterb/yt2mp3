#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/util.py
Brett Stevenson (c) 2018
"""

import sys, os, youtube_dl, shutil, cursesmenu, logging
from collections import defaultdict
from colorama import Fore, Style
from yt2mp3 import itunes, video


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
    result = video.get_data(video.get_title(url))
    if not result:
      data['track_name'] = input(' Track: ')
      data['artist_name'] = input(' Artist: ')
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+url.split('watch?v=')[-1]+'/maxresdefault.jpg'
      result = itunes.get_data(data, False)
    if result:
      data = defaultdict(str, result.__dict__)
      data['video_url'] = url
  elif data['artist_name'] and data['track_name']:
    result = itunes.get_data(data)
    if result:
      data = defaultdict(str, result.__dict__)
      data['video_url'] = video.get_url(data, collection)
  else:
    songs = itunes.get_data(data)
    if data['track_name']:
      options = ['%-30.25s %10.25s' % (s.track_name, s.artist_name) for s in songs]
    elif data['artist_name']:
      options = [s.track_name for s in songs]
    result = songs[show_menu(options)]
    data = defaultdict(str, result.__dict__)
    data['video_url'] = video.get_url(data, collection)
  return data


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
