import psycopg2
from flask import Flask, url_for, request, redirect, send_file
from config import user, password, host, port, database
import controller_site
import os
from werkzeug.utils import secure_filename

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = 'resource/'
app = Flask(__name__)


@app.route('/return_file/<filename>')
def upload_file(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


@app.route('/reg')
def reg():
    return controller_site.registration_users('Maselof', 'admin', 'mr.gindeev@mail.ru', '89613960415')


@app.route('/join')
def join():
    response = controller_site.join_user('Maselof', 'admin')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/playlists')
def playlists():
    return controller_site.show_user_playlist('Maselof')


@app.route('/<id_playlist>/songs')
def playlist_songs(id_playlist):
    return controller_site.show_songs_playlist(id_playlist)


@app.route('/<id_performer>/creativity')
def performer_playlist(id_performer):
    return controller_site.show_playlist_performer(id_performer)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
