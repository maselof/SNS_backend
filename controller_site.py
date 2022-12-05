import flask
import psycopg2
import config

connection = psycopg2.connect(user=config.user,
                              password=config.password,
                              host=config.host,
                              port=config.port,
                              database=config.database)


def registration_users(username, user_password, email, phone_number):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT create_user('{username}', '{user_password}', '{email}', '{phone_number}');
                """
            )
            connection.commit()
            return dict(
                {
                    'successfully': f"{username}"
                }
            )
    except Exception as ex:
        print('[INFO]', ex)
        return dict(
            {
                'error': f"{ex}"
            }
        )


def join_user(username, user_password):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT check_user('{username}', '{user_password}');
                """
            )
            res = cursor.fetchone()
            return dict({
                'answer': f"{res[0]}"
            })
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify({
            'error': f"{ex}"
        })


def show_user_playlist(username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM  show_user_playlist('{username}');
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'id_playlist': data[0],
                    'name_playlist': data[1],
                    'music_count': data[2]
                })
            return res
    except Exception as ex:
        print('[INFO]', ex)
        return dict({
            'error': f"{ex}"
        })


def show_songs_playlist(id_playlist):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_songs_playlist({id_playlist});
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'id_song': data[0],
                    'song_name': data[1],
                    'creator_name': data[2],
                    'song_link': data[3],
                    'duration': data[4],
                    'song_text': data[5],
                    'id_album': data[6]
                })
            return flask.jsonify(res)
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify({
            'error': ex
        })

# прописать функцию в postegres
def show_playlist_performer(id_performer):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_playlist_performer({id_performer});
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'id_playlist': data[0],
                    'name_playlist': data[1],
                    'music_count': data[2]
                })
            return flask.jsonify(res)
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify({
            'error': ex
        })


def show_performer_album(id_performer):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT check_performer({id_performer});
                """
            )
            check = cursor.fetchone()
            if check[0] == 'THE PERFORMER WAS NOT FOUND':
                return check[0]
            res = dict()
            cursor.execute(
                f"""
                SELECT * FROM performer WHERE id_performer = {id_performer}
                """
            )
            for data in cursor.fetchall():
                res = {
                    'id_performer': data[0],
                    'performer_name': data[1],
                    'followers_count': data[2],
                    'album': list()
                }
            cursor.execute(
                f"""
                SELECT * FROM show_album_performer('{id_performer}');
                """
            )
            for data in cursor.fetchall():
                res['album'].append({
                    'id_album': data[0],
                    'album_name': data[1],
                    'creator_id': data[2],
                    'songs_count': data[3]
                })
            return res
    except Exception as ex:
        return dict({
            'error': ex
        })


