import json

import psycopg2
from flask import Flask, request, send_file, make_response, Response
from config import user, password, host, port, database
import controller_site
import secrets

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = 'resource/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ACTIVITY_USERS = dict()


@app.route('/api/register', methods=['POST', 'GET'])
def reg():
    data = request.get_json()
    res = controller_site.registration_users(data['username'], data['password'],
                                             data['email'], data['phone'])
    if 'error' in res.keys():
        return Response('Login is already taken', 400)
    elif res['successfully']:
        return Response('OK', 200)
    else:
        return Response('Server error', 404)


@app.route('/api/auth', methods=['POST', 'GET'])
def join():
    data = request.get_json()
    # data = dict()
    # data['username'] = request.args.get('username')
    # data['password'] = request.args.get('password')
    res = controller_site.join_user(data['username'], data['password'])
    generate_token = secrets.token_hex(32)
    ACTIVITY_USERS[generate_token] = data['username']
    if res['answer'] == 'Password or username entered incorrectly':
        return Response('Incorrect password or username', 403)
    elif res['answer'] == 'The data entered is correct':
        return Response(generate_token, 200)
    else:
        return Response('Server error', 404)


@app.route('/api/<user_token>/playlists', methods=['GET'])
def playlists(user_token):
    if user_token not in ACTIVITY_USERS:
        return Response('Unauthorized', 401)
    res = controller_site.show_user_playlist(ACTIVITY_USERS[user_token])
    if type(res) == list:
        return Response(json.dumps(res, indent=4), 200, mimetype='application/json')
    else:
        return Response('Server error', 404)


@app.route('/api/<id_playlist>/songs')
def playlist_songs(id_playlist):
    return controller_site.show_songs_playlist(id_playlist)


@app.route('/api/<id_performer>/creativity')
def performer_playlist(id_performer):
    return controller_site.show_playlist_performer(id_performer)


@app.route('/api/albums')
def performer_album():
    user_token = request.headers.get('Authorization')
    performer_id = request.args.get('performerid')
    if user_token not in ACTIVITY_USERS:
        return Response('Unauthorized', 401)
    res = controller_site.show_performer_album(performer_id)
    if res == 'THE PERFORMER WAS NOT FOUND':
        return Response('THE PERFORMER WAS NOT FOUND', 404)
    elif 'error' in res.keys():
        return Response('Server error', 404)
    else:
        return Response(json.dumps(res, indent=4), 200, mimetype='application/json')


# example for uploading files
@app.route('/api/<filename>')
def upload_file(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
