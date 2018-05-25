import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
  name = 'yt2mp3',
  version = '1.0.2',
  description = 'Simplifies the process of downloading and converting Youtube videos to MP3 files',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Brett Stevenson',
  author_email = 'bstevensondev@gmail.com',
  url = 'https://github.com/tterb/yt2mp3',
  download_url = 'https://github.com/tterb/yt2mp3/archive/1.0.2.tar.gz',
  keywords = ['youtube', 'mp3', 'download', 'itunes', 'music'],
  packages = setuptools.find_packages(),
  classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.4', 'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Natural Language :: English'
  ],
)
