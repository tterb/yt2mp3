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
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TCON, TRCK, TDRC, TPOS
from PIL import Image
from bs4 import BeautifulSoup

# Get song data from iTunes API
def getSongData(track, artist, exit_fail=True):
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
def fileExists(song):
  path = os.path.expanduser('~/Downloads/Music/')
  path = os.path.join(path, song.artist, song.track+'.mp3')
  return os.path.exists(path)

# Downloads the video at the provided url
def download(url, verbose=False):
  temp_dir = os.path.expanduser('~/Downloads/Music/temp/')
  if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
  video_id = url.split('watch?v=')[-1]
  youtube = pytube.YouTube(url)
  if verbose:
    logging.info(' Downloading...')
    youtube.register_on_progress_callback(showProgressBar)
  youtube.streams.filter(subtype='mp4', progressive=True).first().download(temp_dir, video_id)
  logging.info(' ✔ Download Complete')
  return os.path.join(temp_dir, video_id+'.mp4')

# Returns a list of video URLs in playlist
def getVideoList(url):
  youtube = pytube.Playlist(url)
  video_list = ['https://www.youtube.com'+i for i in youtube.parse_links()]
  return video_list

# Downloads each of the songs from the playlist
def downloadPlaylist(videos, verbose=False, overwrite=False):
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
      video_path = download(url, verbose)
      song_path = convertToMP3(video_path, song)
      setID3(song_path, song)
  logging.info(' ✔ Done')

# Convert the downloaded video file to MP3
def convertToMP3(video, song):
  logging.info(' ♬ Converting to MP3')
  artist_dir = os.path.expanduser('~/Downloads/Music/')
  artist_dir = os.path.join(artist_dir, song.artist)
  if not os.path.exists(artist_dir):
    os.makedirs(artist_dir)
  song_path = os.path.join(artist_dir, song.track+'.mp3')
  pydub.AudioSegment.from_file(video).export(song_path, format='mp3')
  shutil.rmtree(os.path.dirname(video))
  return song_path

# Sets the ID3 metadata of the MP3 file
def setID3(path, song):
  tags = ID3(path)
  tags.delete()
  tags.add(TIT2(encoding=3, text=song.track))
  tags.add(TPE1(encoding=3, text=song.artist))
  tags.add(TPE2(encoding=3, text=song.artist))
  tags.add(TALB(encoding=3, text=song.album))
  tags.add(TCON(encoding=3, text=song.genre))
  tags.add(TRCK(encoding=3, text=song.track_number+'/'+song.track_count))
  tags.add(TPOS(encoding=3, text=song.disc_number+'/'+song.disc_count))
  tags.add(TDRC(encoding=3, text=song.release_date[0:4]))
  # Embed cover-art in ID3 metadata
  img_url = '/'.join(song.artwork_url.split('/')[:-1])+'/480x480bb.jpg'
  img_path = os.path.expanduser('~/Downloads/Music/CoverArt')
  if not os.path.exists(img_path):
    os.makedirs(img_path)
  img_path = os.path.join(img_path, 'cover.jpg')
  response = requests.get(img_url)
  Image.open(io.BytesIO(response.content)).save(img_path)
  tags.add(APIC(encoding=3, mime='image/jpg', type=3,
                desc=u'Cover', data=open(img_path, 'rb').read()))
  tags.save()
  shutil.rmtree(os.path.dirname(img_path))

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
    self.album = data['collection_name']
    self.genre = data['primary_genre_name']
    self.artwork_url = data['artwork_url_100']
    self.track_number = str(data['track_number'])
    self.track_count = str(data['track_count'])
    self.disc_count = str(data['disc_count'])
    self.disc_number = str(data['disc_number'])
    self.release_date = data['release_date']
    self.video_url = data['video_url']
