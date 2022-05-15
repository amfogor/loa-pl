import pathlib
import subprocess as SP

def stamp_to_sec(v):
    parts = v.split(':')
    if(len(parts) == 2):
        min,sec = parts
        return int(min) * 60 + int(sec)
    elif(len(parts) == 3):
        hour,min,sec = parts
        return int(hour) * 3600 + int(min) * 60 + int(sec)
    raise Exception('Invalid stamp format')

def get_titles(ids, f):
    procs = []
    for i, id in enumerate(ids):
        cmd = [ 'yt-dlp', '-e', '--',  f'{id}' ]
        p = SP.Popen(cmd, encoding='utf-8', stderr=SP.PIPE, stdout=SP.PIPE)
        procs.append( (i,p) )
    for i,proc in procs:
        proc.wait()
        if(proc.returncode != 0):
            print('\nfailed on ' + ids[i])
            print(proc.stdout.read())
            print(proc.stderr.read())
            exit(1)
        else:
            f(i, proc.stdout.read())

def get_playlist(file, f):
    lines = open(file, 'r').read().split('\n')
    for line in lines:
        parts = line.split('  ')
        if(len(parts) != 2):
            raise Exception(f'{file} has a problem')
        stamp,song = parts
        f(stamp, song)

class Video:
    def __init__(self, id):
        self.id = id
        self.playlist = []
        self.title = '<title>'

urlPrefix = 'https://youtu.be'

videos = []
songToStamps = {}

for i, file in enumerate(sorted(pathlib.Path('setlists').iterdir())):
    vd = Video(file.name)
    def f(stamp, song):
        vd.playlist.append( (stamp, song) )
        if song not in songToStamps:
            songToStamps[song] = []
        songToStamps[song].append( (i, len(vd.playlist) - 1) )
    get_playlist(file, f)
    videos.append(vd)

def f(i, v):
    videos[i].title = v
get_titles([vd.id for vd in videos], f)


output = open('by_song.md', 'w')

for song in sorted(songToStamps.keys()):
    stamps = songToStamps[song]
    output.write(f'### {song}\n')
    for vd_i, s_i in stamps:
        vd = videos[vd_i]
        id = vd.id
        title = vd.title
        stamp, song = vd.playlist[s_i]
        t = stamp_to_sec(stamp)
        songUrl = f'{urlPrefix}/{id}?t={t}s'
        output.write(f'- [{id}]({songUrl}) {title}\n')

output = open('by_video.md', 'w')

for vd in videos:
    title = vd.title
    playlist = vd.playlist
    videoUrl = f'{urlPrefix}/{id}'
    output.write(f'### [{id}]({videoUrl}) {title}\n')
    for stamp, song in playlist:
        t = stamp_to_sec(stamp)
        songUrl = f'{videoUrl}?t={t}s'
        output.write(f'- [{stamp} {song}]({songUrl})\n')
