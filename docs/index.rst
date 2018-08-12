.. yt2mp3 documentation master file, created by
   sphinx-quickstart on Mon Jul 16 16:39:53 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========
yt2mp3
========  

.. image:: https://img.shields.io/pypi/v/yt2mp3.svg
  :target: https://pypi.python.org/pypi/yt2mp3/
  :alt: Pypi version

.. image:: https://travis-ci.org/tterb/yt2mp3.svg?branch=master
  :target: https://travis-ci.org/tterb/yt2mp3
  :alt: Travis Build Status

.. image:: https://codecov.io/gh/tterb/yt2mp3/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/tterb/yt2mp3
  :alt: Codecov coverage

.. image:: https://img.shields.io/pypi/pyversions/yt2mp3.svg
  :target: https://pypi.python.org/pypi/yt2mp3/
  :alt: Python Version
 
.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
  :target: https://yt2mp3.readthedocs.io/en/latest/license.html
  :alt: License

A program that simplifies the process of searching, downloading and converting Youtube videos to MP3 files from the command-line.  

-------------------

Overview
^^^^^^^^^^

All you need is the video URL or the name of the artist/track you're looking for, the program will then attempt to retrieve data for a song by matching the provided input by querying the iTunes API and find a corresponding YouTube video, if one isn't provided. The video will then be downloaded, converted, and the gathered data will be used to populate the metadata of the MP3.   

**Note:** If a URL is provided and no match is found for the song data, the program will prompt the user for the title/artist and the YouTube thumbnail will be used as the album artwork.  


Contents
^^^^^^^^^^

.. toctree::
  :maxdepth: 1
  
  install
  getting_started
  additional_setup
  changelog
  contributing
  license


Indices and tables
^^^^^^^^^^^^^^^^^^^^^

* :ref:`genindex`
* :ref:`search`
