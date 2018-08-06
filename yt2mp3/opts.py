import argparse

def getOptions():
  parser = argparse.ArgumentParser(prog='yt2mp3', usage='%(prog)s [options]', add_help=True)
  parser.add_argument('--version', action='version', version='v1.0.5', help='show the program version number and exit')
  parser.add_argument('-t', '--track', default='', help='Specify the track name query', nargs='+')
  parser.add_argument('-a', '--artist', default='', help='specify the artist name query', nargs='+')
  parser.add_argument('-u', '--url', help='specify the YouTube URL/ID of the video to convert')
  parser.add_argument('-p', '--playlist', help='specify the YouTube URL/ID of the playlist to convert')
  parser.add_argument('-r', '--res', help='specify the resolution for the cover-art image')
  parser.add_argument('-o', '--overwrite', help='overwrite file if one exists in output directory', action='store_true')
  parser.add_argument('-v', '--verbose', help='display a download progress bar', action='store_true')
  parser.add_argument('-q', '--quiet', help='suppress command-line output', action='store_true')
  return parser.parse_args()
