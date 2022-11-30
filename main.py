import flask
import psycopg2
import requests
from flask import Flask, url_for, request, redirect, send_file
from config import user, password, host, port, database
import controller_site

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = 'resource/'
app = Flask(__name__)


@app.route('/api/register', methods=['POST', 'GET'])
def reg():
    data = request.get_json()
    return controller_site.registration_users(data['username'], data['password'],
                                              data['email'], data['phone'])


@app.route('/api/auth', methods=['POST', 'GET'])
def join():
    data = request.get_json()
    return controller_site.join_user(data['username'], data['password'])


@app.route('/api/playlists')
def playlists():
    return controller_site.show_user_playlist('Maselof')


@app.route('/api/<id_playlist>/songs')
def playlist_songs(id_playlist):
    return controller_site.show_songs_playlist(id_playlist)


@app.route('/api/<id_performer>/creativity')
def performer_playlist(id_performer):
    return controller_site.show_playlist_performer(id_performer)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
