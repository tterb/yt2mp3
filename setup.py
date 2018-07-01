import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
  name = 'yt2mp3',
  version = '1.0.5',
  description = 'Simplifies the process of searching, downloading and converting Youtube videos to MP3 files',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Brett Stevenson',
  author_email = 'bstevensondev@gmail.com',
  url = 'https://github.com/tterb/yt2mp3',
  download_url = 'https://github.com/tterb/yt2mp3/archive/1.0.5.tar.gz',
  keywords = ['youtube', 'convert', 'mp3', 'download', 'itunes', 'music', 'cli'],
  packages = setuptools.find_packages(),
  scripts=['bin/yt2mp3'],
  install_requires=[
    'pydub==0.21.0',
    'mutagen==1.40.0',
    'curses_menu==0.5.0',
    'requests==2.18.4',
    'setuptools==39.2.0',
    'itunespy==1.5.5',
    'pytube==9.2.2',
    'Pillow==5.1.0',
    'lxml==4.2.3',
    'beautifulsoup4==4.6.0'
  ],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Natural Language :: English'
  ],
)
