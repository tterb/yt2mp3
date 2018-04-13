#!/usr/bin/env python3
# yt-to-mp3.py

import sys, os, pafy, argparse, configparser
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3

def main():
  parser = argparse.ArgumentParser(description='YouTube to MP3 Converter')
  parser.add_argument('-i','--info', action='store_true', help='Add ID3 tags to the generated MP3 file')
  parser.add_argument('-c','--config', action='store_true', help='Configure application preferences')
  parser.add_argument('url', help='YouTube URL you want to convert')
  args = parser.parse_args()

  config = configparser.ConfigParser()
  config.read('config.ini')
  config.sections()
  if args.config:
    configure(config)
    path = config['USER']['path']
  elif not os.path.isfile('config.ini'):
    config['DEFAULT'] = { 'path': os.environ['HOME']+'/Downloads/' }
    with open('config.ini', 'w') as configfile:
      config.write(configfile)
  elif 'USER' in config.sections():
    path = config['USER']['path']
  else:
    path = config['DEFAULT']['path']
  video = pafy.new(args.url)
  ext = getAudio(video)
  # Convert to MP3
  convertMP3(video.title, ext)
  # Cleanup
  os.remove(video.title+'.'+ext)
  if args.info:
    d = getInfo(video.title)
    setID3(d)
    os.rename(video.title+'.mp3', path+d['title']+' - '+d['artist']+'.mp3')
  else:
    os.rename(video.title+'.mp3', path+video.title+'.mp3')


# Get best audio stream from video
def getAudio(video):
  print(f' Title: {video.title}\n Length: {video.duration}')
  best = video.getbestaudio()
  best.download(quiet=True, callback=printProgressBar)
  return best.extension

# Convert audio file to MP3
def convertMP3(title, ext):
  audio = AudioSegment.from_file(title+'.'+ext, format=ext)
  audio.export(title+'.mp3', format='mp3')

# Get audio info for ID3 tags
def getInfo(vid_title):
  d = {'video' : vid_title}
  info = []
  if ' - ' in vid_title:
    info = vid_title.split(' - ')
  else:
    info = [vid_title]
  info = [i.strip('\'"').replace('_', ' ').title() for i in info]
  for n in ['Artist', 'Title']:
    for j,i in enumerate(info):
      inp = input(f'{n}: {i}? (y/n) ')
      if inp.lower() in ['y', 'yes']:
        d[n.lower()] = i
        break
      elif j == len(info)-1:
        d[n.lower()] = input(f'{n}: ')
  d['album'] = input('Album: ')
  d['genre'] = input('Genre: ')
  return d

# Set MP3 ID3 tags
def setID3(d):
  song = EasyID3(d['video']+'.mp3')
  song['title'] = d['title']
  song['artist'] = d['artist']
  song['album'] = d['album']
  song['genre'] = d['genre']
  song.save()

# Print iterations progress
def printProgressBar(size, recvd, ratio, rate, eta, prefix = '', suffix = '', total = 100, decimals = 1, length = 45, fill = '█'):
  iteration = ratio*total
  percent = ("{0:." + str(decimals) + "f}").format(iteration)
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + '-' * (length - filledLength)
  prefix = float("%0.2f"%eta)
  print("\r %ss |%s| %s%% %s" % (prefix, bar, percent, suffix), end="\r")
  if iteration == total:
    print()
    print(u' \u2713 Complete')


def configure(config):
  config['DEFAULT'] = { 'path': os.environ['HOME']+'/Downloads/' }
  config['USER'] = {}
  config['USER']['path'] = input('Destination for downloads: ').replace('~', os.environ['HOME'])
  with open('config.ini', 'w') as configfile:
    config.write(configfile)


if __name__ == '__main__':
  main()
