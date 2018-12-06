from sclib import SoundcloudAPI, Track, Playlist
from pydub import AudioSegment
import simpleaudio as sa

class QueueEmptyError(Exception):
    """Raised when there are no more tracks in the TrackQueue"""
    pass

class TrackNode:

    def __init__(self, data):
        self.data = data
        self.next = None

class TrackQueue:

    def __init__(self):
        self.head = None
        self.rear = None

    def enqueue_track(self, track):
        if self.is_empty():
            self.head = TrackNode(track)
            self.rear = self.head
        else:
            self.rear.next = TrackNode(track)
            self.rear = self.rear.next

    def dequeue_track(self):
        if self.is_empty():
            return None
        else:
            track_to_return = self.head.data
            self.head = self.head.next
            return track_to_return

    def is_empty(self):
        return self.head is None or self.rear is None

    def print_queue(self, message = ''):
        def print_queue_helper(node, num):
            if node is None:
                print('End')
            else:
                print('{}) {} by {}'.format(num, node.data.title, node.data.artist))
                print_queue_helper(node.next, num + 1)
        print(message)
        if self.is_empty():
            print('No Tracks')
        elif self.head is self.rear:
            print('1) {}'.format(self.head.data.title))
        else:
            print('1) {}'.format(self.head.data.title))
            print_queue_helper(self.head.next, num = 2)

class Player:

    api = SoundcloudAPI()

    def __init__(self, playlist_url):
        self.playlist_url = playlist_url
        self.track_playlist = []
        self.current_track = None
        self.song_queue = TrackQueue()

    def fetch_playlist(self):
        playlist = Player.api.resolve(self.playlist_url)
        for track in playlist:
            if is_valid_title(track):
                self.track_playlist.append(track)
            else:
                continue
        self.track_playlist.sort(key = lambda x: x.title)

    def play_song(self):
        try:
            current_track = self.song_queue.dequeue_track()
            if current_track is None:
                raise QueueEmptyError
        except QueueEmptyError:
            message = 'Your music queue is now empty.  Please choose new songs to play.\n'
            chosen_music = self.display_songs_and_choose_music(message)
            self.estalish_queue(chosen_music)
            current_track = self.song_queue.dequeue_track()
            response = str(input('Play music now ?  Enter Y for yes and N for no:  ')).lower()
            if response == 'n':
                return
        self.current_track = current_track
        print('\nNow playing: {} by {}\n'.format(current_track.title, current_track.artist))
        filename = '{}.mp3'.format(current_track.title)

        with open(filename, 'wb+') as song_file:
            current_track.write_mp3_to(song_file)

        #convert .mp3 to .wav format
        sound = AudioSegment.from_mp3(filename)
        sound.export('{}.wav'.format(current_track.title), format = 'wav')

        wave_obj = sa.WaveObject.from_wave_file('{}.wav'.format(current_track.title))
        play_obj = wave_obj.play()
        return play_obj

    def estalish_queue(self, chosen_music):
        print()
        for song_index in chosen_music:
            int_index = int(song_index.replace(' ', ''))
            self.song_queue.enqueue_track(self.track_playlist[int_index - 1])
        message = 'These songs are on your song queue:'
        self.song_queue.print_queue(message)

    def display_songs_and_choose_music(self, *messages):
        for message in messages:
            print(message)
        for i in range(len(self.track_playlist)):
            print('{}) {} - {}'.format(i + 1, self.track_playlist[i].title, self.track_playlist[i].artist))
        chosen_music = str(input('\nEnter your choices here:  ')).split(',')
        return chosen_music

def is_valid_title(track):
    for char in track.title:
        if ord(char) not in range(128):
            return False
        else:
            continue
    return True

def prompt_user():
    playlist_url = str(input('Please enter the URL of your Soundcloud playlist:   '))
    player = Player(playlist_url)
    print('Loading...\n')
    player.fetch_playlist()
    message_to_user = '*********************************************************\nHere is a list of your songs that are availiable to play.\n\nPick the number corresponding to the song you want to play.'
    second_message = '\nIf you want to play a series of songs in succession, just separate the numbers with a comma!\n*********************************************************\n'
    chosen_music = player.display_songs_and_choose_music(message_to_user, second_message)
    player.estalish_queue(chosen_music)
    response = str(input('\nPlay music now ? Enter Y for yes and N for no:  ')).lower()
    if response == 'y':
        song = player.play_song()
        while song.is_playing():
            options = str(input('***********************\nEnter s to skip song\nEnter e to exit this program\nEnter a to add a song to the queue\nEnter v to display the song queue\n***********************\n')).lower()
            if options == 'p':
                song.stop()
            elif options == 's':
                song.stop()
                song = player.play_song()
            elif options == 'e':
                break
            elif options == 'a':
                message = 'Which song/songs do you want to add to the queue?\n'
                chosen_music = player.display_songs_and_choose_music(message)
                player.estalish_queue(chosen_music)
            elif options == 'v':
                message = 'These songs are in your queue:\n'
                player.song_queue.print_queue(message)
            else:
                print('\nInvalid command')
                continue
        print('Music Player Exited.')
    else:
        print('ok')

if __name__ == '__main__':
    prompt_user()
