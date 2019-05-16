#!/usr/bin/env python3
"""
yt2mp3
A program that simplifies the process of searching, downloading and 
converting Youtube videos to MP3 files with embedded metadata via the 
iTunes API.
tests/test_yt2mp3.py
Brett Stevenson (c) 2018
"""

import os, pytest
from mutagen.id3 import ID3
from collections import defaultdict, deque
from yt2mp3 import itunes, opts, util, video
from yt2mp3.song import Song

@pytest.fixture
def test_data():
    return { 'artist_name': 'Pink Floyd',
             'collection_name': 'Wish You Were Here',
             'primary_genre_name': 'Rock',
             'track_name': 'Have a Cigar',
             'track_number': 3
            }

@pytest.fixture
def test_song():
    data = itunes.get_data({ 'track_name':'Have a Cigar', 
    'artist_name':'Pink Floyd', 'track_time':308000}).__dict__
    data['video_url'] = video.get_url(data)
    return Song(data)

def multiple_inputs(inputs):
    """ 
    Provides a function to call for every input requested.
    """
    def next_input(_):
        # Provides the first item in the list
        return inputs.popleft()
    return next_input

def test_arguments():
    args = opts.parse_options(['-o','-v','-a','pink','floyd','-t','have','a','cigar', '-c'])
    assert args.collection and args.overwrite and args.verbose and not args.quiet
    assert args.resolution == 480
    assert ' '.join(args.artist) == 'pink floyd'
    assert ' '.join(args.track) == 'have a cigar'

def test_get_song_data(test_data):
    input = defaultdict(str, {'track_name': 'Have a Cigar',
                              'artist_name': 'Pink Floyd'})
    data = defaultdict(str, util.get_song_data(input))
    assert [test_data[key] == data[key] for key in test_data.keys()]
    data.clear()
    input.clear()
    input['video_url'] = 'https://www.youtube.com/watch?v=hMr3KtYUCcI'
    data = defaultdict(str, util.get_song_data(input))
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_get_song_collection_data(test_data):
    input = defaultdict(str, {'track_name': 'Have a Cigar',
                              'artist_name': 'Pink Floyd',
                              'collection_name': 'Wish You Were Here'})
    data = defaultdict(str, util.get_song_data(input))
    assert [test_data[key] == data[key] for key in test_data.keys()]
    input['collection_name'] = 'live'
    assert not itunes.get_data(input, False)
    
    
def test_itunes_data(test_data):    
    data, results = defaultdict(str), dict()
    data['track_name'] = 'have a cigar'
    results['track_name'] = util.get_song_data(data)
    data.clear()
    data['artist_name'] = 'pink floyd'
    results['artist_name'] = util.get_song_data(data)
    assert [len(results[key]) > 2 for key in results.keys()]

# Test iTunes lookup failure => Program should exit 
def test_itunes_data_failure():
    fail_data = { 'track_name':'nomatch', 'artist_name':'test' }
    with pytest.raises(SystemExit) as err:
        itunes.get_data(fail_data)
    assert err.type == SystemExit

def test_get_video_url(test_data, test_song):
    url = video.get_url(test_data)
    assert url == test_song.video_url and video.validate_url(url)

def test_url_validation():
    errors = []
    videos = [
        'https://www.youtube.com/watch?v=C0DPdy98e4c',
        'http://youtu.be/C0DPdy98e4c'
    ]
    playlists = [
        'https://www.youtube.com/playlist?list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm',
        'https://www.youtube.com/watch?list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm&v=C0DPdy98e4c',
        'https://www.youtube.com/watch?v=C0DPdy98e4c&list=PLGqB3S8f_uiLkCQziivGYI3zNtLJvfUWm'
    ]
    for url in videos:
        if not video.validate_url(url):
            errors.append('Failed URL Validation: '+url)
    for url in playlists:
        if not video.validate_url(url, playlist=True):
            errors.append('Failed URL Validation: '+url)
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_video_title_data(test_data):
    url = 'https://www.youtube.com/watch?v=hMr3KtYUCcI'
    title = video.get_title(url)
    data = video.get_data(title).__dict__
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_video_metadata(test_data):
    errors = []
    url = 'https://www.youtube.com/watch?v=hMr3KtYUCcI'
    meta = video.get_metadata(url)
    assert test_data['track_name'].lower() in meta['song'].lower()
    assert test_data['artist_name'].lower() in meta['artist'].lower()
    assert test_data['collection_name'].lower() in meta['album'].lower()

# Test video iTunes lookup failure => should use video data
def test_video_itunes_failure(monkeypatch):
    data = defaultdict(str)
    data['video_url'] = 'https://www.youtube.com/watch?v=GI30qzbj5_s'
    monkeypatch.setattr('builtins.input', multiple_inputs(deque(['Black Beatles', 'Merkules'])))
    data = util.get_song_data(data)
    artwork = 'https://img.youtube.com/vi/'+data['video_url'].split('watch?v=')[-1]+'/maxresdefault.jpg'
    assert data['artwork_url_100'] == artwork

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
    song_path = test_song.convert_to_mp3(video_path)
    if not os.path.exists(song_path):
        errors.append('The output MP3 file doesn\'t exist')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_set_id3_tags(test_song):
    errors = []
    path = os.path.expanduser('~/Downloads/Music/')
    path = os.path.join(path, test_song.artist, test_song.track+'.mp3')
    test_song.set_id3(path)
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
    videos = util.get_video_list(url)
    assert videos == ['https://www.youtube.com/watch?v=C0DPdy98e4c', 'https://www.youtube.com/watch?v=_FrOQC-zEog', 'https://www.youtube.com/watch?v=yvPr9YV7-Xw']

# Make sure temporary files are being cleaned up
def test_cleanup(test_song):
    errors = []
    directory = os.path.expanduser('~/Downloads/Music/')
    video_dir = os.path.join(directory, 'temp/')
    cover_dir = os.path.join(directory, 'CoverArt/')
    song_path = os.path.join(directory, test_song.artist, test_song.track+'.mp3')
    util.cleanup()
    # Remove test mp3 file and artist diectory if empty
    if test_song.file_exists():
        os.remove(song_path)
    if not os.listdir(os.path.dirname(song_path)):
        os.rmdir(os.path.dirname(song_path))
    if os.path.isdir(video_dir):
        errors.append('The temporary video files weren\'t cleaned up')
    if os.path.isdir(cover_dir):
        errors.append('The temporary cover-art files weren\'t cleaned up')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
