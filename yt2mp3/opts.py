#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and
converting Youtube videos to MP3 files with embedded metadata via the
iTunes API.
yt2mp3/opts.py
Brett Stevenson (c) 2018
"""

import argparse

def parse_options(args):
  """
  Parses command-line options and default states
  Args:
    args: A list of provided command-line options
  Returns:
    A parser object for handling command-line options
  """
  parser = argparse.ArgumentParser(prog='yt2mp3', usage='%(prog)s [options]', add_help=True)
  parser.add_argument('--version', action='version', version='v1.2.4', help='show the program version number and exit')
  parser.add_argument('-t', '--track', nargs='+', help='specify the track name query', default='')
  parser.add_argument('-a', '--artist', nargs='+', help='specify the artist name query', default='')
  parser.add_argument('-c', '--collection', action='store_true', help='specify the album name query')
  parser.add_argument('-u', '--url', help='specify the YouTube URL/ID of the video to convert')
  parser.add_argument('-p', '--playlist', help='specify the YouTube URL/ID of the playlist to convert')
  parser.add_argument('-r', '--resolution', type=int, help='specify the resolution for the cover-art image', default=480)
  parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite file if one exists in output directory')
  parser.add_argument('-v', '--verbose', action='store_true', help='display a download progress bar')
  parser.add_argument('-q', '--quiet', action='store_true', help='suppress command-line output')
  return parser.parse_args(args)
