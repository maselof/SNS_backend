import json
import os
import flask
import psycopg2
from flask import Flask, request, send_file, Response
from config import user, password, host, port, database
import controller_site
from controller_site import ACTIVITY_USERS
import secrets
import requests

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = 'data/'
app = Flask(__name__, static_folder="data")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/api/register', methods=['POST', 'GET'])
def reg():
    data = request.get_json()
    res = controller_site.registration_users(data)
    if 'error' in res.keys():
        return Response('Login is already taken', 400)
    elif res['successfully']:
        id_user = res['successfully']
        if not os.path.isdir(f"{UPLOAD_FOLDER}{id_user}"):
            os.mkdir(f"{UPLOAD_FOLDER}{id_user}")
        return Response('OK', 200)
    else:
        return Response('Server error', 404)


@app.route('/api/auth', methods=['POST', 'GET'])
def join():
    data = request.get_json()
    res = controller_site.join_user(data['username'], data['password'])
    print(ACTIVITY_USERS)
    if 'error' in res.keys():
        if res['error'][9:49] == 'Password or username entered incorrectly':
            return Response('Incorrect password or username', 403)
        else:
            return Response('Server error', 404)
    else:
        return Response(res, 200, mimetype='application/json')


@app.route('/api/account/avatar', methods=['POST'])
def change_avatar():
    avatar_url = 'http://bff:8080/' + request.args.get('avatarUrl')
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.change_avatar_user(ACTIVITY_USERS[user_token])
    if 'successfully' in res.keys():
        open(f"data/{res['successfully']}/img.png", 'wb').write(requests.get(avatar_url).content)
        return Response('OK', 200)
    else:
        return Response('Bad request', 400)


@app.route('/api/playlists', methods=['GET'])
def playlists():
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS:
        return Response('Unauthorized', 401)
    res = controller_site.show_user_playlist(ACTIVITY_USERS[user_token])
    if type(res) == list:
        return Response(res, 200, mimetype='application/json')
    else:
        return Response('Server error', 404)


@app.route('/api/find', methods=['GET'])
def find():
    type_search = request.args.get('type')
    word = request.args.get('word')
    print(ACTIVITY_USERS)
    user_token = request.headers.get('Authorization')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    elif word == '':
        return Response('Bad request', 400)
    elif type_search == 'album':
        res = controller_site.finder_by_word_from_album(word)
        if type(res) == dict:
            return Response('Bad request', 400)
        else:
            return Response(res, 200, mimetype='application/json')
    elif type_search == 'performer':
        res = controller_site.finder_by_word_from_performer(word)
        if type(res) == dict:
            return Response('Bad request', 400)
        else:
            return Response(res, 200, mimetype='application/json')
    elif type_search == 'song':
        res = controller_site.finder_by_word_from_song(word)
        print(res)
        if type(res) == dict:
            return Response('Bad request', 400)
        else:
            return Response(res, 200, mimetype='application/json')


@app.route('/api/albums', methods=['GET'])
def performer_album():
    user_token = request.headers.get('Authorization')
    performer_id = request.args.get('performerId')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.show_performer_album(performer_id)
    if res == 'THE PERFORMER WAS NOT FOUND':
        return Response('THE PERFORMER WAS NOT FOUND', 404)
    elif type(res) == dict:
        return Response('Server error', 404)
    else:
        return Response(res, 200, mimetype='application/json')


@app.route('/api/playlists', methods=['POST'])
def add_playlist():
    user_token = request.headers.get('Authorization')
    playlist_name = request.args.get('playlistName')
    if user_token not in ACTIVITY_USERS.keys():
        return Response('Unauthorized', 401)
    res = controller_site.add_playlist_in_db(playlist_name)
    if type(res) is not dict:
        return Response('OK', 200)
    else:
        return Response('Bad request', 400)


# example for uploading files
@app.route('/api/<filename>')
def upload_file(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
