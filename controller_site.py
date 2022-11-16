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
            return flask.jsonify(
                {
                    'successfully': f"{username}"
                }
            )
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify(
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
            # cursor.execute(
            #     f"""
            #     DELETE FROM users WHERE username = 'Maselof'
            #     """
            # )
            # connection.commit()
            return flask.jsonify({
                'answer': f"{res[0]}"
            })
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify({
            'error': f"{ex}"
        })


def return_res_playlist(prev_res, i):
    if i >= len(prev_res):
        return
    return flask.jsonify({
        'id_playlist': f'{prev_res[i][0]}',
        'playlist_name': f'{prev_res[i][1]}',
        'music_count': f'{prev_res[i][2]}'
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
            return flask.jsonify(res)
    except Exception as ex:
        print('[INFO]', ex)
        return flask.jsonify({
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

# прописать функцию в pgadmin
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