import json
import os
import psycopg2
from flask import Flask, request, send_file, Response
from config import user, password, host, port, database, bff_host
import controller_site
from controller_site import ACTIVITY_USERS
import requests
import re

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = 'data/'
app = Flask(__name__, static_folder="data")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def check_injections(req):
    if re.match("\S[^\'\"|&;[^\--]\(\)]*$", req) and not re.match("--", req):
        return False
    return True


@app.route('/api/register', methods=['POST', 'GET'])
def reg():
    data = request.get_json()
    if check_injections(data['username']) or check_injections(data['password']) or \
            check_injections(data['email']) or check_injections(data['phone']):
        return Response('Forbidden', 403)
    res = controller_site.registration_users(data)
    if 'error' in res.keys():
        if res['error'][0:31] == 'ОШИБКА:  повторяющееся значение':
            return Response('Login is already taken', 400)
        else:
            return Response('Server error', 500)
    elif res['successfully']:
        user_id = res['successfully']
        if not os.path.isdir(f"{UPLOAD_FOLDER}{user_id}"):
            os.mkdir(f"{UPLOAD_FOLDER}{user_id}")
            os.mkdir(f"{UPLOAD_FOLDER}{user_id}/playlists")
            os.mkdir(f"{UPLOAD_FOLDER}{user_id}/playlists/{res['playlist_id']}")
        if data['isPerformer']:
            os.mkdir(f"{UPLOAD_FOLDER}{user_id}/albums")
        return Response('OK', 200)


@app.route('/api/auth', methods=['POST', 'GET'])
def join():
    data = request.get_json()
    if check_injections(data['username']) or check_injections(data['password']):
        return Response('Forbidden', 403)
    res = controller_site.join_user(data['username'], data['password'])
    print(res)
    if 'error' in res.keys():
        if res['error'][9:49] == 'Password or username entered incorrectly':
            return Response('Incorrect password or username', 403)
        else:
            return Response('Server error', 500)
    else:
        return Response(json.dumps(res), 200, mimetype='application/json')


@app.route('/api/account/avatar', methods=['POST', 'GET'])
def change_avatar():
    avatar_url = bff_host + request.args.get('avatarUrl')
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.change_avatar_user(user_token)
    if 'successfully' in res.keys():
        r = requests.get(avatar_url)
        with open(f"data/{res['successfully']}/img.png", 'wb') as f:
            f.write(r.content)
        return Response(f"data/{res['successfully']}/img.png", 200)
    else:
        return Response('Bad request', 400)


@app.route('/api/playlists', methods=['GET'])
def show_playlists():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS:
        return Response('Unauthorized', 401)
    user_id = request.args.get('userId')
    if check_injections(user_id):
        return Response('Forbidden', 403)
    res = controller_site.show_user_playlist(user_id)
    if type(res) == list:
        return Response(json.dumps(res), 200, mimetype='application/json')
    else:
        return Response('Server error', 500)


@app.route('/api/find', methods=['GET'])
def find():
    type_search = request.args.get('type')
    word = request.args.get('word')
    if check_injections(type_search) or check_injections(word):
        return Response('Forbidden', 403)
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    elif type_search == 'album':
        res = controller_site.finder_by_word_from_album(word)
        if type(res) == dict:
            return Response(json.dumps(''), 200, mimetype='application/json')
        else:
            return Response(json.dumps(res), 200, mimetype='application/json')
    elif type_search == 'performer':
        res = controller_site.finder_by_word_from_performer(word, user_token)
        if type(res) == dict:
            return Response(json.dumps(''), 200, mimetype='application/json')
        else:
            return Response(json.dumps(res), 200, mimetype='application/json')
    elif type_search == 'song':
        res = controller_site.finder_by_word_from_song(word, user_token)
        if type(res) == dict:
            return Response(json.dumps(''), 200, mimetype='application/json')
        else:
            return Response(json.dumps(res), 200, mimetype='application/json')


@app.route('/api/albums', methods=['GET'])
def performer_album():
    user_token = request.headers.get('Authorization')
    performer_id = request.args.get('performerId')
    if check_injections(performer_id):
        return Response('Forbidden', 403)
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.show_performer_album(performer_id)
    if res == 'THE PERFORMER WAS NOT FOUND':
        return Response('THE PERFORMER WAS NOT FOUND', 404)
    elif type(res) == dict:
        return Response('Server error', 500)
    else:
        return Response(json.dumps(res), 200, mimetype='application/json')


@app.route('/api/album/songs', methods=['GET'])
def songs_album():
    user_token = request.headers.get('Authorization')
    album_id = request.args.get('albumId')
    if check_injections(album_id):
        return Response('Forbidden', 403)
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.show_songs_in_album(album_id, user_token)
    if type(res) == dict:
        return Response('Album not found', 404)
    else:
        return Response(json.dumps(res), 200, mimetype='application/json')


@app.route('/api/albums', methods=['POST'])
def add_album():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    album_name = request.args.get('albumName')
    if check_injections(album_name):
        return Response('Forbidden', 403)
    cover_url = bff_host + request.args.get('coverUrl')
    res = controller_site.add_album_in_db(album_name, user_token)
    if 'successfully' in res.keys():
        if not os.path.isdir(res['cover_url']):
            os.mkdir(res['cover_url'])
        r = requests.get(cover_url)
        with open(f"{res['cover_url']}/img.png", 'wb') as f:
            f.write(r.content)
        return Response(str(res['successfully']), 200)
    else:
        return Response('Bad request', 400)


@app.route('/api/album/songs', methods=['POST'])
def add_song_in_album():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    album_id = request.args.get('albumId')
    song_name = request.args.get('songName')
    if check_injections(album_id) or check_injections(song_name):
        return Response('Forbidden', 403)
    audio_url = bff_host + request.args.get('audioUrl')
    res = controller_site.add_song_in_album(album_id, song_name, user_token)
    if 'successfully' in res.keys():
        r = requests.get(audio_url)
        with open(res['audio_url'], 'wb') as f:
            f.write(r.content)
        return Response(str(res['successfully']), 200)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Bad request', 400)


@app.route('/api/album/songs', methods=['DELETE'])
def delete_song_in_album():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    song_id = request.args.get('songId')
    res = controller_site.delete_song_on_album(song_id, user_token)
    if 'successfully' in res.keys():
        if os.path.isfile(res['successfully']):
            os.remove(res['successfully'])
            return Response('OK', 200)
        else:
            return Response('Song not found', 404)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Bad request', 400)


@app.route('/api/albums', methods=['DELETE'])
def delete_album():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    album_id = request.args.get('albumId')
    res = controller_site.delete_album(album_id, user_token)
    if 'successfully' in res.keys():
        if os.path.isdir(f"data/{res['successfully']}/albums/{album_id}"):
            list_dir = os.listdir(f"data/{res['successfully']}/albums/{album_id}")
            for name in list_dir:
                os.remove(f"data/{res['successfully']}/albums/{album_id}/{name}")
            os.rmdir(f"data/{res['successfully']}/albums/{album_id}")
            return Response('OK', 200)
        else:
            return Response('Album not found', 404)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Bad request', 400)


@app.route('/api/playlists', methods=['POST'])
def add_playlist():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    playlist_name = request.args.get('playlistName')
    if check_injections(playlist_name):
        return Response('Forbidden', 403)
    cover_url = bff_host + request.args.get('coverUrl')
    res = controller_site.add_playlist(playlist_name, user_token)
    if 'successfully' in res.keys():
        if not os.path.isdir(res['cover_url']):
            os.mkdir(res['cover_url'])
        r = requests.get(cover_url)
        with open(f"{res['cover_url']}/img.png", 'wb') as f:
            f.write(r.content)
        return Response(str(res['successfully']), 200)
    else:
        return Response('Bad request', 400)


@app.route('/api/playlist/songs', methods=['POST'])
def add_song():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    playlist_id = request.args.get('playlistId')
    song_id = request.args.get('songId')
    res = controller_site.add_song_in_playlist(playlist_id, song_id, user_token)
    if 'successfully' in res.keys():
        return Response('OK', 200)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Album or song not found', 404)


@app.route('/api/playlist/songs', methods=['DELETE'])
def delete_song_from_playlist():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    song_id = request.args.get('songId')
    playlist_id = request.args.get('playlistId')
    res = controller_site.delete_song_from_playlist(song_id, playlist_id, user_token)
    if 'successfully' in res.keys():
        return Response('OK', 200)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Song or playlist not found', 404)


@app.route('/api/playlists', methods=['DELETE'])
def delete_playlist():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    playlist_id = request.args.get('playlistId')
    res = controller_site.delete_playlist(playlist_id, user_token)
    if 'successfully' in res.keys():
        if os.path.isdir(f"data/{res['successfully']}/playlists/{playlist_id}"):
            list_dir = os.listdir(f"data/{res['successfully']}/playlists/{playlist_id}")
            for name in list_dir:
                os.remove(f"data/{res['successfully']}/playlists/{playlist_id}/{name}")
            os.rmdir(f"data/{res['successfully']}/playlists/{playlist_id}")
            return Response('OK', 200)
    else:
        if res['error'] == 403:
            return Response('Forbidden', 403)
        else:
            return Response('Playlist not found', 404)


@app.route('/api/playlist/songs', methods=['GET'])
def show_songs_playlist():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    playlist_id = request.args.get('playlistId')
    res = controller_site.show_songs_playlist(playlist_id, user_token)
    if type(res) == list:
        return Response(json.dumps(res), 200, mimetype='application/json')
    else:
        return Response('Playlist not found', 404)


@app.route('/api/performers', methods=['POST'])
def like_performer():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    performer_id = request.args.get('performerId')
    like = request.args.get('like')
    res = controller_site.like_performer(performer_id, like, user_token)
    if 'successfully' in res.keys():
        return Response('OK', 200)
    else:
        return Response('Performer not found', 404)


@app.route('/api/performers', methods=['GET'])
def show_liked_performers():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.show_liked_performer(user_token)
    if type(res) == list:
        return Response(json.dumps(res), 200, mimetype='application/json')
    else:
        return Response('Server error', 404)


# example for uploading files
@app.route('/api/<filename>')
def upload_file(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
