import psycopg2
from flask import Flask, url_for, request, redirect
from config import user, password, host, port, database
import controller_site
import os
from werkzeug.utils import secure_filename

connection = psycopg2.connect(user=user,
                              password=password,
                              host=host,
                              port=port,
                              database=database)
UPLOAD_FOLDER = '/resource'
ALLOWED_EXTENSION = {'.jpg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSION


@app.route('/')
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form> 
    """


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
