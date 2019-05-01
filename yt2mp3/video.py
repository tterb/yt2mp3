#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/video.py
Brett Stevenson (c) 2018
"""

import sys, re, youtube_dl, urllib, ssl, string
from urllib.request import Request, urlopen
from collections import defaultdict
from bs4 import BeautifulSoup
from yt2mp3 import itunes

def get_url(data, collection=False):
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
            video_data = defaultdict(str, get_metadata(url))
            if data['collection_name'].lower() in video_data['album'].lower():
              return url
          else:
            return url
      # Check video metadata if album has been specified by user
      elif collection:
        video_data = defaultdict(str, get_metadata(url))
        if data['collection_name'].lower() in video_data['album'].lower():
          return url
      return url


def get_data(title):
  """
  Attempts to retrieve song data from the video title
  Args:
    title: A string containing the title of the YouTube video
  Returns:
    A dict of song data if a match is found using the iTunes APi
  """
  # Remove parenthesis, punctuation and nondescript words
  pattern = r'\([^)]*\)|\[[^]]*\]|ft(\.)?|feat(\.)?|\blyrics?\b|official|video|audio|h(d|q)'
  keywords = re.sub(pattern, '', str(title), flags=re.I)
  keywords = keywords.translate(str.maketrans('', '', string.punctuation))
  keywords = ' '.join(keywords.split())
  # Query iTunes API
  return itunes.keyword_search(keywords)


def get_title(url):
  """
  Retrieves the title of the provided YouTube video
  Args:
    url: A YouTube video URL
  Returns:
    A string containing the title of the provided YouTube video
  """
  return youtube_dl.YoutubeDL({'quiet': True}).extract_info(url, download=False)['title']


def get_metadata(url):
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
  section = soup.find('ul', attrs={'class': 'watch-extras-section'})
  video_data = {}
  for item in section.find_all('li', recursive=False):
    key = next(item.find('h4').stripped_strings).lower()
    video_data[key] = next(item.find('li').stripped_strings).lower()
  return video_data


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
