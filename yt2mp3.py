#!/usr/bin/env python3
# yt2mp3.py

import sys, os, itunespy, argparse, urllib, requests, ssl, glob, shutil, cursesmenu
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3,APIC,TIT2,TPE1,TPE2,TALB,TCON,TRCK,TDRC,TPOS
from urllib.request import Request, urlopen
from PIL import Image
from io import BytesIO
from pathlib import Path
from bs4 import BeautifulSoup
from pytube import YouTube
from pydub import AudioSegment


def main():
  parser = argparse.ArgumentParser(description='YouTube to MP3 Converter')
  parser.add_argument('-t','--track', default='', help='Specify the track name query')
  parser.add_argument('-a','--artist', default='', help='Specify the artist name query')
  parser.add_argument('-u','--url', help='YouTube URL you want to convert')
  args = parser.parse_args()
  # Get song track/artist from user
  info = {}
  if args.track or args.artist:
    info['track'] = args.track
    info['artist'] = args.artist
  else:
    info['track'] = input('Track: ')
    info['artist'] = input('Artist: ')
  if args.url:
    path = download(args.url)
    try:
      song = getSongData(info['track'], info['artist'])
      setData(path, song)
    except Exception as e:
      setID3(path, info)
      pass
  else:
    if info['track'] and info['artist']:
      song = getSongData(info['track'], info['artist'])
    elif info['track'] or info['artist']:
      songs = getSongData(info['track'], info['artist'])
      if info['track']:
        options = [str("%-30.25s %10.25s" % (s.track_name, s.artist_name)) for s in songs]
      else:
        options = [str(s.track_name) for s in songs]
      selection = showMenu(options)
      if selection >= len(songs):
        sys.exit()
      song = songs[selection]
      info['track'] = song.track_name
    if song:
      url = getURL(song.track_name, song.artist_name)
      tempPath = download(url)
      path = convertToMP3(tempPath, song)
      setData(path, song)
    else:
      print('Sorry, no results were found.')
      sys.exit()
  # setPath(path, info['track'], info['artist'])

  
def getSongData(track, artist):
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
  return

# Displays an interactive menu of songs
def showMenu(options):
  menu = cursesmenu.SelectionMenu(options, title='Select an song')
  selection = menu.get_selection(options)
  return selection
  
# Scrapes youtube for a video that has track and artist in the name
def getURL(track, artist):
  query = urllib.parse.quote(track+" "+artist)
  url = "https://www.youtube.com/results?search_query=" + query
  req = Request(url, headers={'User-Agent':'Mozilla/5.0'})
  response = urlopen(req, context=ssl._create_unverified_context())
  soup = BeautifulSoup(response.read(), 'lxml')
  results = []
  for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    results.append('https://www.youtube.com' + vid['href'])
  return results[0]

# Downloads songs from youtube, songs must be a list of track objects
def download(url):
  tempDir = os.path.join(Path.home(),'Downloads','YDL')
  id = url.split('=')[-1]
  if not os.path.exists(tempDir):
    os.makedirs(tempDir)
  if len(url) <= 15:
    url = 'https://www.youtube.com/watch?v='+url
  # ydl.download(url)
  yt = YouTube(url)
  yt.streams.filter(subtype='mp4', progressive=True).first().download(tempDir, id)
  print(u' \u2713 Download Complete')
  return glob.glob(str(Path.home()/'Downloads'/'YDL')+'/'+id+'.*')[0]

# def convertToMP3(stream, file_handle):
def convertToMP3(tempPath, song):
  print(u' \u266b Converting to MP3')
  outputDir = Path.home()/'Downloads'/'Music'/song.artist_name
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  AudioSegment.from_file(tempPath).export(os.path.join(outputDir,song.track_name+'.mp3'), format="mp3")
  shutil.rmtree(Path.home()/'Downloads'/'YDL')
  return os.path.join(outputDir,song.track_name+'.mp3')

# Sets the ID3 meta data of the MP3 file found at the end of path
def setData(path, song):
  data = ID3(path)
  data.delete()
  data.add(TIT2(encoding=3, text=song.track_name))
  data.add(TPE1(encoding=3, text=song.artist_name))
  data.add(TPE2(encoding=3, text=song.artist_name))
  data.add(TALB(encoding=3, text=song.collection_name))
  data.add(TCON(encoding=3, text=song.primary_genre_name))
  data.add(TRCK(encoding=3, text=str(song.track_number)+'/'+str(song.track_count)))
  data.add(TPOS(encoding=3, text=str(song.disc_number)+'/'+str(song.disc_count)))
  data.add(TDRC(encoding=3, text=song.release_date[0:4]))
  data.save()
  # Embed cover-art in ID3 metadata
  data = MP3(path, ID3=ID3)
  imgURL = song.artwork_url_100
  dir = str(Path.home()/'Downloads'/'CoverArt')
  os.system('mkdir -p %s' % (dir))
  imgPath = os.path.join(dir,song.collection_name+'.jpg')
  response = requests.get(imgURL)
  img = Image.open(BytesIO(response.content))
  img.save(imgPath)
  data.tags.add(APIC(encoding=3, mime="image/jpg", type=3, 
                     desc=u"Cover", data=open(imgPath, "rb").read()))
  data.save()
  shutil.rmtree(dir)

# Sets the file path of song to: Music/[artist]/[track].mp3
def setPath(path, track, artist):
  # make artist directory
  dir = str(Path.home()/'Downloads'/'Music')
  if artist:
    dir = os.path.join(dir, artist)
  os.system('mkdir -p %s' % (dir.replace(' ', '_')))
  # add song to artist directory
  newPath = os.path.join(dir,track+'.mp3')
  os.system('mv %s %s' % (path, newPath.replace(' ', '_')))
  shutil.rmtree(Path.home()/'Downloads'/'YDL')
  
# Set MP3 ID3 tags
def setID3(path, info):
  song = EasyID3(path)
  song['track'] = info['track']
  song['artist'] = info['artist']
  song.save()  



if __name__ == '__main__':
  main()
