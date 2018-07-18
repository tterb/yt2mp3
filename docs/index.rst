.. yt2mp3 documentation master file, created by
   sphinx-quickstart on Mon Jul 16 16:39:53 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

yt2mp3
========  

.. image:: https://img.shields.io/pypi/v/yt2mp3.svg
 :target: https://pypi.python.org/pypi/yt2mp3/
 :alt: Pypi

.. image:: https://readthedocs.org/projects/python-pytube/badge/?version=latest
 :target: http://yt2mp3.readthedocs.io/en/latest/?badge=latest
 :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/yt2mp3.svg
 :target: https://pypi.python.org/pypi/yt2mp3/
 :alt: Python Versions
 
.. image:: https://img.shields.io/github/license/tterb/yt2mp3.svg
 :target: https://github.com/tterb/yt2mp3/blob/master/LICENSE
 :alt: License
 
Overview
----------

This program simplifies the process of downloading and converting Youtube videos to MP3 files from the command-line.  

All you need is the video URL or the name of the artist/track you're looking for. The program will then attempt to retrieve data for a song by matching the provided input by querying the iTunes API and find a corresponding YouTube video, if a URL is not provided. The video will then be downloaded, converted, and the gathered data will be used to populate the metadata of the MP3.  

Once finished, the resulting MP3 file will be saved to your *Downloads* directory, with the following file-structure ``Music/{artist}/{track}.mp3``.

***Note***: If a URL is provided and no match is found for the song data, the YouTube thumbnail will be used as the album artwork.  


Contents
==========

.. toctree::
   :maxdepth: 2
  
   install
   usage
   development
   changes
   license


Indices and tables
=====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
