#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and 
converting Youtube videos to MP3 files with embedded metadata via the 
iTunes API.
yt2mp3/tests/test_yt2mp3.py
Brett Stevenson (c) 2018
"""

import os, pytest
from mutagen.id3 import ID3
from collections import defaultdict
from yt2mp3 import util, opts
from yt2mp3.song import Song

@pytest.fixture
def test_data():
    return { 'artist_name': 'The Jimi Hendrix Experience',
             'collection_name': 'Experience Hendrix: The Best of Jimi Hendrix',
             'primary_genre_name': 'Rock',
             'track_name': 'Bold As Love',
             'track_number': 12
            }

@pytest.fixture
def test_song():
    data = util.getiTunesData('Bold as Love', 'Jimi Hendrix').__dict__
    data['video_url'] = util.getVideoURL(data['track_name'], data['artist_name'])
    return Song(data)
    
def test_arguments():
    errors = []
    args = opts.parseOptions(['-o', '-v', '-a', 'jimi', 'hendrix', '-t', 'bold', 'as', 'love'])
    assert args.overwrite and args.verbose and not args.quiet
    assert args.resolution == 480
    assert ' '.join(args.artist) == 'jimi hendrix'
    assert ' '.join(args.track) == 'bold as love'

def test_get_song_data(test_data):
    input = defaultdict(str, {'track_name': 'Bold as Love',
                              'artist_name': 'Jimi Hendrix'})
    data = defaultdict(str, util.getSongData(input))
    assert [test_data[key] == data[key] for key in test_data.keys()]
    data.clear()
    input.clear()
    input['video_url'] = 'https://www.youtube.com/watch?v=gkJhnDkdC-0'
    data = defaultdict(str, util.getSongData(input))
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_itunes_data(test_data):    
    data, results = defaultdict(str), dict()
    data['track_name'] = 'bold as love'
    results['track_name'] = util.getSongData(data)
    data.clear()
    data['artist_name'] = 'jimi hendrix'
    results['artist_name'] = util.getSongData(data)
    assert [len(results[key]) > 2 for key in results.keys()]

# Test iTunes lookup failure => Program should exit 
def test_itunes_data_failure():
    with pytest.raises(SystemExit) as err:
        util.getiTunesData('nomatch', 'test')
    assert err.type == SystemExit

def test_get_video_URL(test_song):
    url = util.getVideoURL(test_song.track, test_song.artist)
    assert url == test_song.video_url and util.validateURL(url)

def test_validate_URL():
    errors = []
    urls = ['https://www.youtube.com/watch?v=gkJhnDkdC-0', 'http://youtu.be/gkJhnDkdC-0']
    playlists = ['https://www.youtube.com/playlist?list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm','https://www.youtube.com/watch?v=gkJhnDkdC-0&list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm', 'https://www.youtube.com/watch?list=PL1F9CA2A03CF286C2&v=pFS4zYWxzNA&']
    for url in urls:
        if not util.validateURL(url):
            errors.append('Failed URL Validation: '+url) 
    for url in playlists:
        if not util.validateURL(url, playlist=True):
            errors.append('URL Validation: '+url)
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_video_data(test_data):
    url = 'https://www.youtube.com/watch?v=gkJhnDkdC-0'
    title = util.getVideoTitle(url)
    data = util.getVideoData(title).__dict__
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_video_download(test_song):
    video_path = test_song.download(False)
    assert os.path.exists(video_path)

def test_video_download_verbose(test_song):
    test_song.video_url = 'https://www.youtube.com/watch?v=C0DPdy98e4c'
    video_path = test_song.download(True)
    assert os.path.exists(video_path)

def test_convert_mp3(test_song):
    errors = []
    video_dir = os.path.expanduser('~/Downloads/Music/temp/')
    video_path = os.path.join(video_dir, os.listdir(video_dir)[0])
    song_path = test_song.convertToMP3(video_path)
    if not os.path.exists(song_path):
        errors.append('The output MP3 file doesn\'t exist')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_set_id3_tags(test_song):
    errors = []
    path = os.path.expanduser('~/Downloads/Music/')
    path = os.path.join(path, test_song.artist, test_song.track+'.mp3')
    test_song.setID3(path)
    song = ID3(path)
    if test_song.track != song['TIT2'].text[0]:
        errors.append('[TIT2] Title tag does not match expected result')
    if test_song.artist != song['TPE1'].text[0]:
        errors.append('[TPE1] Artist tag does not match expected result')
    if test_song.album != song['TALB'].text[0]:
        errors.append('[TALB] Album tag does not match expected result')
    if test_song.genre != song['TCON'].text[0]:
        errors.append('[TCON] Genre tag does not match expected result')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_get_playlist_videos():
    url = 'https://www.youtube.com/playlist?list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm'
    videos = util.getVideoList(url)
    assert videos == ['https://www.youtube.com/watch?v=gkJhnDkdC-0', 'https://www.youtube.com/watch?v=_FrOQC-zEog', 'https://www.youtube.com/watch?v=yvPr9YV7-Xw']

# Make sure temporary files are being cleaned up
def test_cleanup(test_song):
    errors = []
    directory = os.path.expanduser('~/Downloads/Music/')
    video_dir = os.path.join(directory, 'temp/')
    cover_dir = os.path.join(directory, 'CoverArt/')
    song_path = os.path.join(directory, test_song.artist, test_song.track+'.mp3')
    util.cleanup()
    # Remove test mp3 file and artist diectory if empty
    if test_song.fileExists():
        os.remove(song_path)
    if os.listdir(os.path.dirname(song_path)):
        os.rmdir(os.path.dirname(song_path))
    if os.path.isdir(video_dir):
        errors.append('The temporary video files weren\'t cleaned up')
    if os.path.isdir(cover_dir):
        errors.append('The temporary cover-art files weren\'t cleaned up')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
