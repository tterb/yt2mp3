import setuptools

with open('README.md') as f:
  long_description = f.read()

setuptools.setup(
  name = 'yt2mp3',
  version = '1.2.4',
  description = 'Simplifies the process of searching, downloading and converting Youtube videos to MP3 files',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Brett Stevenson',
  author_email = 'bstevensondev@gmail.com',
  url = 'https://github.com/tterb/yt2mp3',
  download_url = 'https://github.com/tterb/yt2mp3/archive/1.2.0.tar.gz',
  keywords = ['youtube', 'convert', 'mp3', 'download', 'itunes', 'music', 'cli'],
  packages = setuptools.find_packages(),
  scripts=['bin/yt2mp3'],
  setup_requires=['pytest-runner'],
  tests_require=['pytest', 'pytest-cov'],
  install_requires=[
    'beautifulsoup4>=4.6.3',
    'colorama==0.4.1',
    'curses_menu>=0.5.0',
    'itunespy==1.5.5',
    'lxml>=4.2.5',
    'mutagen==1.45.1',
    'Pillow>=5.3.0',
    'pydub==0.23.1',
    'requests>=2.21.0',
    'setuptools>=40.6.3',
    'youtube_dl>=2018.12.17',
  ],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ]
)
