import flask
import psycopg2
import config
import secrets

connection = psycopg2.connect(user=config.user,
                              password=config.password,
                              host=config.host,
                              port=config.port,
                              database=config.database)

ACTIVITY_USERS = dict()


def registration_users(data):
    try:
        with connection.cursor() as cursor:
            if data['isPerformer']:
                cursor.execute(
                    f"""
                    SELECT create_performer_user('{data['username']}', '{data['password']}', 
                    '{data['email']}', '{data['phone']}');
                    """
                )
                res = cursor.fetchone()[0]
                connection.commit()
                return dict(
                    {
                        'successfully': f"{res}"
                    }
                )
            else:
                cursor.execute(
                    f"""
                    SELECT create_user('{data['username']}', '{data['password']}', 
                    '{data['email']}', '{data['phone']}');
                    """
                )
                connection.commit()
                res = cursor.fetchone()[0]
                print(res)
                return dict(
                    {
                        'successfully': f"{res}"
                    }
                )
    except Exception as ex:
        connection.rollback()
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
                SELECT performer_users_relship.id_user FROM performer_users_relship
                WHERE performer_users_relship.id_user =
                (SELECT users.id_user FROM users WHERE users.username = '{username}');
                """
            )
            if cursor.fetchall() is not None:
                isPerformer = True
            else:
                isPerformer = False
            cursor.execute(
                f"""
                SELECT * FROM check_user('{username}', '{user_password}');
                """
            )
            res = dict()
            generate_token = secrets.token_hex(32)
            if username in ACTIVITY_USERS.values():
                del ACTIVITY_USERS[list(ACTIVITY_USERS.keys())[list(ACTIVITY_USERS.values()).index(username)]]
            ACTIVITY_USERS[generate_token] = username
            print(ACTIVITY_USERS)
            for data in cursor.fetchall():
                res = {
                    'token': generate_token,
                    'userId': data[0],
                    'username': data[1],
                    'avatarUrl': data[2],
                    'isPerformer': isPerformer
                }
            return res
    except Exception as ex:
        connection.rollback()
        print('[INFO]', ex)
        return dict({
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
        connection.rollback()
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
            return res
    except Exception as ex:
        connection.rollback()
        print('[INFO]', ex)
        return dict({
            'error': ex
        })


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
                    'songsCount': data[5],
                    'coverUrl': data[6]
                })
            return res
    except Exception as ex:
        connection.rollback()
        print('[INFO]', ex)
        return dict({
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
        connection.rollback()
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
                    'followers': data[2],
                    'avatarUrl': data[3]
                })
            return res
    except Exception as ex:
        connection.rollback()
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
                    'songId': data[0],
                    'songName': data[1],
                    'albumId': data[2],
                    'albumName': data[3],
                    'performerId': data[4],
                    'performerName': data[5],
                    'audioUrl': data[6],
                    'coverUrl': data[7]
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def change_avatar_user(username):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id_user FROM users WHERE users.username = f{username};
                """
            )
            id_user = cursor.fetchone()[0]
            cursor.execute(
                f"""
                UPDATE users SET users.avatarurl = 'data/{id_user}/img.png'
                """
            )
            return dict({
                'successfully': id_user
            })
    except Exception as ex:
        print(ex)
        return dict({
            'error': ex
        })


def add_playlist_in_db(playlist_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT (playlist_name) INTO playlist VALUES('{playlist_name}')
                """
            )
            connection.commit()
            res = cursor.fetchall()
            print(res)
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })
