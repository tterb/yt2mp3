from pydub import AudioSegment
from time import sleep
import sys, os, pafy

def main():
  url = sys.argv[1]
  video = pafy.new(url)
  ext = getAudio(video)
  # Convert to MP3
  convertMP3(video.title, ext)
  # Cleanup
  os.remove(video.title+'.'+ext)
  os.rename(video.title+'.mp3', os.environ['HOME']+'/Downloads/'+video.title+'.mp3')


def getAudio(video):
  print(f' Title: {video.title}\n Length: {video.duration}')
  best = video.getbestaudio()
  best.download(quiet=True, callback=printProgressBar)
  return best.extension

def convertMP3(title, ext):
  audio = AudioSegment.from_file(title+'.'+ext, format=ext)
  audio.export(title+'.mp3', format='mp3')

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

if __name__ == '__main__':
  main()