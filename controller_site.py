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

def finder_by_word_from_album(word):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_in_album('{word}'); 
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'albumId': data[0],
                    'albumName': data[1],
                    'performerId': data[2],
                    'performerName': data[3],
                    'followers': data[4],
                    'songsCount': data[5]
                })
            return res
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
            res = list()
            cursor.execute(
                f"""
                SELECT * FROM performer WHERE id_performer = {id_performer}
                """
            )
            data_performer = cursor.fetchone()
            cursor.execute(
                f"""
                SELECT * FROM show_album_performer('{id_performer}');
                """
            )
            print(data_performer)
            for data in cursor.fetchall():
                res.append({
                    'albumId': data[0],
                    'albumName': data[1],
                    'performerId': data[2],
                    'songsCount': data[3],
                    'performerName': data_performer[1],
                    'followers': data_performer[2]
                })
            return res
    except Exception as ex:
        print(ex)
        return dict({
            'error': ex
        })


def finder_by_word_from_performer(word):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_performer('{word}');
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'performerId': data[0],
                    'performerName': data[1],
                    'followers': data[2]
                })
            return res
    except Exception as ex:
        print(ex)
        return dict({
            'error': ex
        })


def finder_by_word_from_song(word):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_song('{word}');
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'songID': data[0],
                    'songName': data[1],
                    'albumId': data[2],
                    'albumName': data[3],
                    'performerId': data[4],
                    'performerName': data[5],
                    'url': data[6],
                    'duration': data[7],
                    'text': data[8]
                })
            return res
    except Exception as ex:
        print(ex)
        return dict({
            'error': ex
        })
