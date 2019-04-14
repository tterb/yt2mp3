#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/cli.py
Brett Stevenson (c) 2018
"""

import sys, logging, inquirer
from collections import defaultdict
from colorama import Fore, Style
from yt2mp3 import util

def get_input(args, data):
  """
   Prompts user for necessary input
   Args:
     args: A list of provided command-line options
     data: A dict of provided user-input
   Returns:
     A dict with additional user-input data
   """
  if not args.track and not args.artist:
    data['track_name'] = input(' Track: ')
    data['artist_name'] = input(' Artist: ')
    if args.collection:
      data['collection_name'] = input(' Album: ')

  if data['track_name'] and data['artist_name']:
    data = util.get_song_data(data, args.collection)
  else:
    if data['artist_name'] and data['collection_name']:
        data = get_album_track(data['artist_name'], data['collection_name'])
    elif data['artist_name']:
      data = get_track(data['artist_name'])
    elif data['track_name']:
      data = get_artist(data['track_name'])
  data['video_url'] = util.get_video_url(data)
  return data

def get_artist(track):
  """
   Get the users `Artist` selection from the matching tracks
   Args:
     track: A user-input track string provided by the user 
   Returns:
     A dict of the track data selected by the user
   """
  opts = util.get_artist_options(track)
  if opts:
    questions = [ inquirer.List('artist', message='Select the artist:',
                    choices=list(opts.keys()), carousel=True) ]
    artist = inquirer.prompt(questions)['artist']
    return defaultdict(str, opts[artist].__dict__)
  else:
    logging.warning(Fore.RED+'✘ '+Style.RESET_ALL+' A match couldn\'t be found')
    sys.exit()

def get_track(artist):
  """
   Get the users `Track` selection for the matching artist
   Args:
     artist: A user-input artist string provided by the user 
   Returns:
     A dict of the track data selected by the user
   """
  opts = util.get_track_options(artist)
  if opts:
    questions = [ inquirer.List('track', message='Select a track:',
                    choices=list(opts.keys()), carousel=True) ]
    track = inquirer.prompt(questions)['track']
    return defaultdict(str, opts[track].__dict__)
  else:
    logging.warning(Fore.RED+'✘ '+Style.RESET_ALL+' A match couldn\'t be found')
    sys.exit()

def get_album_track(artist, collection):
  """
   Get the users `Track` selection for the matching artist and album
   Args:
     artist: A user-input artist string provided by the user 
     collectiokn: A user-input album string provided by the user 
   Returns:
     A dict of the track data selected by the user
   """
  opts = util.get_collection_tracks(artist, collection)
  # opts = [song.track_name for song in tracks]
  if opts:
    questions = [ inquirer.List('track', message='Select a track:',
                    choices=list(opts.keys())) ]
    track = inquirer.prompt(questions)['track']
    return defaultdict(str, opts[track].__dict__)
  else:
    logging.warning(Fore.RED+'✘ '+Style.RESET_ALL+' A match couldn\'t be found')
    sys.exit()
