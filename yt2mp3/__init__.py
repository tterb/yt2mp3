#!/usr/bin/env python3
# yt2mp3.py

import sys, os, argparse, pytube, pydub, itunespy, urllib, requests, io, ssl, glob, shutil, cursesmenu, logging
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3,APIC,TIT2,TPE1,TPE2,TALB,TCON,TRCK,TDRC,TPOS
from urllib.request import Request, urlopen
from collections import defaultdict
from PIL import Image
from pathlib import Path
from bs4 import BeautifulSoup


def main():
  parser = argparse.ArgumentParser(description='YouTube to MP3 Converter')
  parser.add_argument('-t','--track', default='', help='Specify the track name query')
  parser.add_argument('-a','--artist', default='', help='Specify the artist name query')
  parser.add_argument('-u','--url', help='Specify the YouTube URL you want to convert')
  parser.add_argument('-p','--progress', help='Display a command-line progress bar', action='store_true')
  parser.add_argument('-q','--quiet', help='Suppress command-line output', action='store_true')
  args = parser.parse_args()
  logging.basicConfig(level=logging.WARNING if args.quiet else logging.INFO, format='%(message)s')
  # Get song track/artist from user
  data = defaultdict(str)
  if args.track or args.artist:
    data['track_name'] = args.track
    data['artist_name'] = args.artist
  else:
    data['track_name'] = input(' Track: ')
    data['artist_name'] = input(' Artist: ')
  if args.url:
    data['video_url'] = args.url
    if len(args.url) <= 12:
      data['video_url'] = 'https://www.youtube.com/watch?v='+args.url
    res = getSongData(data['track_name'], data['artist_name'])
    if res:
      song = Song(defaultdict(str, res.__dict__))
    else:
      id = data['video_url'].split('=')[-1]
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+id+'/maxresdefault.jpg'
      song = Song(data)
  else:
    if data['track_name'] and data['artist_name']:
      res = getSongData(data['track_name'], data['artist_name'])
    elif data['track_name'] or data['artist_name']:
      songs = getSongData(data['track_name'], data['artist_name'])
      if data['track_name']:
        options = ['%-30.25s %10.25s' % (s.track_name, s.artist_name) for s in songs]
      else:
        options = [s.track_name for s in songs]
      select = showMenu(options)
      if select >= len(songs):
        sys.exit()
      res = songs[select]
    if res:
      data = defaultdict(str, res.__dict__)
      data['video_url'] = getURL(data['track_name'], data['artist_name'])
      song = Song(data)
    else:
      logging.warning('Sorry, no results were found.')
      sys.exit()
  tempPath = download(song.video_url, args.progress)
  path = convertToMP3(tempPath, song)
  setData(path, song)
    
# Get song data from iTunes API
def getSongData(track, artist):
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
  return

# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
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
  id = url.split('=')[-1]
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


if __name__ == '__main__':
  main()
