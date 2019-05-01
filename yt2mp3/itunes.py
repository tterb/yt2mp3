#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/itunes.py
Brett Stevenson (c) 2018
"""

import sys, os, itunespy, logging
from collections import defaultdict
from colorama import Fore, Style


def get_data(data, exit_fail=True):
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
      logging.warning(Fore.RED+'✘ '+Style.RESET_ALL+str(err))
      sys.exit()


def keyword_search(keywords):
  """
  Attempts to retrieve song data for the specified keywords
  Args:
    keywords: A string containing track keywords
  Returns:
    A dict of song data if a match is found using the iTunes APi
  Raises:
    LookupError: If a match isn't found using the iTunes API
  """
  try:
    return itunespy.search(keywords)[0]
  except LookupError:
    return None