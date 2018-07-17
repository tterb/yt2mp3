#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and converting
Youtube videos to MP3 files with embedded metadata via the iTunes API.
yt2mp3/__init__.py
Brett Stevenson (c) 2018
"""

import sys, os, re, pytube, pydub, itunespy, urllib, requests, io, ssl, glob, shutil, cursesmenu, logging, string
from urllib.request import Request, urlopen
from collections import defaultdict
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC, TPOS
from PIL import Image
from bs4 import BeautifulSoup

# Get song data from iTunes API
def getSongData(track, artist, exit_on_fail=True):
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
    if exit_on_fail:
      logging.warning("%s", err)
      sys.exit()

# Attempt to retrieve song data from the video title
def getVideoData(title):
  # Remove parenthesis, punctuation and commonly added words
  regex = r'\([^)]*\)|[[^]]*\]|ft|feat|\blyrics?\b|official|video|audio'
  keywords = re.sub(re.compile(regex, re.IGNORECASE), '', title)
  keywords = keywords.translate(str.maketrans('', '', string.punctuation))
  keywords = ' '.join(keywords.split())
  # Query iTunes API
  try:
    return itunespy.search(keywords)[0]
  except LookupError:
    pass

# Get YouTube video title
def getVideoTitle(url):
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  return soup.find('span', {'class':'watch-title'}).get_text().strip()

# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  if selection >= len(options):
    sys.exit()
  return selection

# Scrapes YouTube for a video with the track and artist
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

# Returns a list of video URLs in playlist
def getVideoList(url):
  youtube = pytube.Playlist(url)
  video_list = ['https://www.youtube.com'+i for i in youtube.parse_links()]
  return video_list

# Downloads each of the songs from the playlist
def downloadPlaylist(videos, overwrite):
  for i, url in enumerate(videos):
    title = getVideoTitle(url)
    logging.info('%s of %s: %s', (i+1), len(videos), title)
    result = getVideoData(title)
    video_id = url.split('watch?v=')[-1]
    if not result:
      data = defaultdict(str)
      data['track_name'] = input(' Track: ')
      data['artist_name'] = input(' Artist: ')
      data['video_url'] = url
      data['artwork_url_100'] = 'https://img.youtube.com/vi/'+video_id+'/maxresdefault.jpg'
      result = getSongData(data['track_name'], data['artist_name'])
    if result:
      song = Song(defaultdict(str, result.__dict__))
      song.video_url = url
    else:
      song = Song(data)
    if overwrite or not fileExists(song):
      temp_path = download(url)
      path = convertToMP3(temp_path, song)
      setData(path, song)
  logging.info(' ✔ Done')

# Downloads the video at the provided url
def download(url, progress_bar=False):
  temp_dir = Path.home()/'Downloads'/'Music'/'temp'
  if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
  video_id = url.split('watch?v=')[-1]
  youtube = pytube.YouTube(url)
  if progress_bar:
    logging.info(' Downloading...')
    youtube.register_on_progress_callback(showProgressBar)
  youtube.streams.filter(subtype='mp4', progressive=True).first().download(temp_dir, video_id)
  logging.info(' ✔ Download Complete')
  return glob.glob(os.path.join(str(temp_dir), video_id+'.*'))[0]

# Checks if a duplicate file exists in the output directory
def fileExists(song):
  path = Path.home()/'Downloads'/'Music'/song.artist
  path = os.path.join(path, song.track+'.mp3')
  return os.path.exists(path)

# Convert the downloaded video file to MP3
def convertToMP3(temp_path, song):
  logging.info(' ♬ Converting to MP3')
  output_dir = Path.home()/'Downloads'/'Music'/song.artist
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  path = os.path.join(output_dir, song.track+'.mp3')
  pydub.AudioSegment.from_file(temp_path).export(path, format='mp3')
  shutil.rmtree(Path(temp_path).parent)
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
  img_url = song.artwork_url
  directory = Path.home()/'Downloads'/'Music'/'CoverArt'
  os.system('mkdir -p %s' % (directory))
  img_path = os.path.join(directory, 'cover.jpg')
  response = requests.get(img_url)
  img = Image.open(io.BytesIO(response.content))
  img.save(img_path)
  meta.tags.add(APIC(encoding=3, mime='image/jpg', type=3,
                     desc=u'Cover', data=open(img_path, 'rb').read()))
  meta.save()
  shutil.rmtree(directory)

# Display a download progress bar
def showProgressBar(stream, _chunk, _file_handle, bytes_remaining):
  total = stream.filesize
  current = ((total-bytes_remaining)/total)
  percent = ('{0:.1f}').format(current*100)
  progress = int(50*current)
  status = '█' * progress + '-' * (50 - progress)
  sys.stdout.write(' ↳ |{bar}| {percent}%\r'.format(bar=status, percent=percent))
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
