import os.path, pytest, yt2mp3, shutil
from mutagen.id3 import ID3
from collections import defaultdict

@pytest.fixture
def test_data():
    return { 'artist_name': 'The Jimi Hendrix Experience',
             'collection_name': 'Experience Hendrix: The Best of Jimi Hendrix',
             'primary_genre_name': 'Rock',
             'track_name': 'Bold As Love',
             'track_number': 12,
            }

@pytest.fixture
def test_song():
    data = yt2mp3.getSongData('Bold as Love', 'Jimi Hendrix').__dict__
    data['video_url'] = yt2mp3.getVideoURL(data['track_name'], data['artist_name'])
    return yt2mp3.Song(data)
    

def test_get_song_data(test_data):
    data = yt2mp3.getSongData('Bold as Love', 'Jimi Hendrix')
    data = defaultdict(str, data.__dict__)
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_get_video_URL():
    url = yt2mp3.getVideoURL('Bold as Love', 'Jimi Hendrix')
    assert len(url.split('watch?v=')) == 2

def test_video_data(test_data):
    url = 'https://www.youtube.com/watch?v=gkJhnDkdC-0'
    title = yt2mp3.getVideoTitle(url)
    data = yt2mp3.getVideoData(title).__dict__
    assert [test_data[key] == data[key] for key in test_data.keys()]

def test_video_download(test_song):
    video_path = yt2mp3.download(test_song.video_url)
    assert os.path.exists(video_path)

def test_video_download_verbose():
    url = 'https://www.youtube.com/watch?v=C0DPdy98e4c'
    video_path = yt2mp3.download(url, True)
    assert os.path.exists(video_path)

def test_convert_mp3(test_song):
    errors = []
    video_dir = os.path.expanduser('~/Downloads/Music/temp/')
    video_path = os.path.join(video_dir, os.listdir(video_dir)[0])
    song_path = yt2mp3.convertToMP3(video_path, test_song)
    if not os.path.exists(song_path):
        errors.append('The output MP3 file doesn\'t exist')
    if os.path.exists(video_path):
        errors.append('The video file wasn\'t deleted after conversion')
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))

def test_file_check(test_song):
    assert yt2mp3.fileExists(test_song)

def test_set_id3_tags(test_song):
    errors = []
    path = os.path.expanduser('~/Downloads/Music/')
    path = os.path.join(path, test_song.artist, test_song.track+'.mp3')
    yt2mp3.setID3(path, test_song)
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
    playlist = yt2mp3.getVideoList(url)
    assert yt2mp3.getVideoList(url) == ['https://www.youtube.com/watch?v=gkJhnDkdC-0', 'https://www.youtube.com/watch?v=_FrOQC-zEog', 'https://www.youtube.com/watch?v=yvPr9YV7-Xw']

def test_lookup_failure():
    with pytest.raises(SystemExit) as err:
        yt2mp3.getSongData('nomatch', 'test')
    assert err.type == SystemExit

def test_cleanup(test_song):
    errors = []
    directory = os.path.expanduser('~/Downloads/Music/')
    video_dir = os.path.join(directory, 'temp/')
    cover_dir = os.path.join(directory, 'CoverArt/')
    song_dir = os.path.join(directory, test_song.artist)
    shutil.rmtree(song_dir)
    if os.path.isdir(video_dir):
        errors.append('The video file wasn\'t deleted after conversion')
        shutil.rmtree(video_dir)
    if os.path.isdir(cover_dir):
        errors.append('The cover image wasn\'t deleted after embedding')
        shutil.rmtree(cover_dir)
    assert not errors, 'errors occured:\n{}'.format('\n'.join(errors))
    
