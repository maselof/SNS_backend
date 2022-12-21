import psycopg2
import config
import secrets
from hashing_password import hash_password

connection = psycopg2.connect(user=config.user,
                              password=config.password,
                              host=config.host,
                              port=config.port,
                              database=config.database)

ACTIVITY_USERS = dict()
FAVOURITE_PLAYLIST = dict()


def registration_users(data):
    try:
        with connection.cursor() as cursor:
            if data['isPerformer']:
                cursor.execute(
                    f"""
                    SELECT create_performer_user('{data['username']}', 
                    '{hash_password(data['username'], data['password'])}', 
                    '{data['email']}', '{data['phone']}');
                    """
                )
                res = cursor.fetchone()[0]
                connection.commit()
            else:
                cursor.execute(
                    f"""
                    SELECT create_user('{data['username']}', '{hash_password(data['username'], data['password'])}', 
                    '{data['email']}', '{data['phone']}');
                    """
                )
                connection.commit()
                res = cursor.fetchone()[0]
            cursor.execute(
                f"""
                SELECT playlist_id FROM playlist 
                WHERE creator_id = (SELECT user_id FROM users WHERE username = '{data['username']}');
                """
            )
            playlist_id = cursor.fetchone()[0]
            return dict(
                {
                    'successfully': f"{res}",
                    'playlist_id': playlist_id
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
                SELECT user_id FROM users WHERE username = '{username}';
                """
            )
            print(username)
            user_id = cursor.fetchone()[0]
            print('.')
            cursor.execute(
                f"""
                SELECT check_performer({user_id});
                """
            )
            if cursor.fetchone()[0] != 'Performers is not found':
                isPerformer = True
            else:
                isPerformer = False
            cursor.execute(
                f"""
                SELECT * FROM check_user('{username}', '{hash_password(username, user_password)}');
                """
            )
            dataset = cursor.fetchall()
            user_id = dataset[0][0]
            cursor.execute(
                f"""
                SELECT * FROM show_favourite_playlist({user_id});
                """
            )
            cursor.execute(
                f"""
                SELECT playlist_id FROM playlist 
                WHERE creator_id = (SELECT user_id FROM users WHERE username = '{username}')
                AND playlist_name = 'Favourite Songs';
                """
            )
            playlist_id = cursor.fetchone()[0]
            cursor.execute(
                f"""
                SELECT playlist_id, playlist_name FROM playlist WHERE creator_id = {user_id};
                """
            )
            playlists = cursor.fetchall()
            if username in ACTIVITY_USERS.values():
                del ACTIVITY_USERS[list(ACTIVITY_USERS.keys())[list(ACTIVITY_USERS.values()).index(username)]]
            generate_token = secrets.token_hex(32)
            ACTIVITY_USERS[generate_token] = user_id
            for data in dataset:
                res = {
                    'token': generate_token,
                    'userId': data[0],
                    'username': data[1],
                    'avatarUrl': data[2],
                    'isPerformer': isPerformer,
                    'playlists': list()
                }
            res['favouritePlaylistId'] = playlist_id
            for data in playlists:
                res['playlists'].append({
                    'playlistId': data[0],
                    'playlistName': data[1]
                })
            FAVOURITE_PLAYLIST[generate_token] = res['favouritePlaylistId']
            return res
    except Exception as ex:
        connection.rollback()
        print('[INFO]', ex)
        return dict({
            'error': f"{ex}"
        })


def show_user_playlist(user_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_user_playlists({user_id});
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'albumId': data[0],
                    'albumName': data[1],
                    'performerId': data[2],
                    'songsCount': data[3],
                    'coverUrl': data[4],
                    'performerName': data[5]
                })
            return res
    except Exception as ex:
        connection.rollback()
        print('[INFO]', ex)
        return dict({
            'error': f"{ex}"
        })


def finder_by_word_from_album(word):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_albums('{word}'); 
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


def show_performer_album(performer_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT check_performer({performer_id});
                """
            )
            check = cursor.fetchone()
            if check[0] == 'THE PERFORMER WAS NOT FOUND':
                return check[0]
            res = list()
            cursor.execute(
                f"""
                SELECT * FROM show_performer_albums({performer_id});
                """
            )
            for data in cursor.fetchall():
                res.append({
                    'albumId': data[0],
                    'albumName': data[1],
                    'performerId': data[2],
                    'songsCount': data[3],
                    'coverUrl': data[4],
                    'performerName': data[5],
                    'followers': data[6]
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def finder_by_word_from_performer(word, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_performers('{word}');
                """
            )
            dataset = cursor.fetchall()
            cursor.execute(
                f"""
                SELECT performer_id FROM users_liked_performer WHERE user_id = {ACTIVITY_USERS[user_token]};
                """
            )
            LIKED_PERFORMER = dict()
            for data in cursor.fetchall():
                LIKED_PERFORMER[data[0]] = user_token
            res = list()
            for data in dataset:
                if data[0] in LIKED_PERFORMER.keys():
                    flag = True
                else:
                    flag = False
                res.append({
                    'performerId': data[0],
                    'performerName': data[1],
                    'followers': data[2],
                    'avatarUrl': data[3],
                    'isLiked': flag
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def finder_by_word_from_song(word, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM search_songs('{word}');
                """
            )
            dataset = cursor.fetchall()
            res = list()
            LIKED_SONG = dict()
            cursor.execute(
                f"""
                SELECT song_id FROM song_playlist_relship WHERE playlist_id = {FAVOURITE_PLAYLIST[user_token]}
                """
            )
            for data in cursor.fetchall():
                LIKED_SONG[data[0]] = user_token
            for data in dataset:
                if data[0] in LIKED_SONG.keys():
                    flag = True
                else:
                    flag = False
                res.append({
                    'songId': data[0],
                    'songName': data[1],
                    'albumId': data[2],
                    'albumName': data[3],
                    'performerId': data[4],
                    'performerName': data[5],
                    'audioUrl': data[6],
                    'coverUrl': data[7],
                    'isLiked': flag
                    })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def change_avatar_user(user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CALL change_user_avatar({ACTIVITY_USERS[user_token]});
                """
            )
            connection.commit()
            return dict({
                'successfully': ACTIVITY_USERS[user_token]
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def show_songs_in_album(album_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_album_songs({album_id});
                """
            )
            dataset = cursor.fetchall()
            LIKED_SONG = dict()
            cursor.execute(
                f"""
                SELECT song_id FROM song_playlist_relship WHERE playlist_id = {FAVOURITE_PLAYLIST[user_token]}
                """
            )
            for data in cursor.fetchall():
                LIKED_SONG[data[0]] = user_token
            res = list()
            for data in dataset:
                if data[0] in LIKED_SONG.keys():
                    flag = True
                else:
                    flag = False
                res.append({
                    'songId': data[0],
                    'songName': data[1],
                    'albumId': data[2],
                    'albumName': data[3],
                    'performerId': data[4],
                    'performerName': data[5],
                    'audioUrl': data[6],
                    'coverUrl': data[7],
                    'isLiked': flag
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def add_album_in_db(album_name, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CALL add_album('{album_name}', {ACTIVITY_USERS[user_token]});
                """
            )
            connection.commit()
            cursor.execute(
                f"""
                SELECT album_id FROM album WHERE album_name = '{album_name}' AND creator_id = {ACTIVITY_USERS[user_token]}
                """
            )
            album_id = cursor.fetchone()[0]
            return dict({
                'successfully': album_id,
                'cover_url': f'data/{ACTIVITY_USERS[user_token]}/albums/{album_id}'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def add_song_in_album(album_id, song_name, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT creator_id FROM album WHERE album_id = {album_id}
                """
            )
            creator_id = cursor.fetchone()[0]
            if creator_id != ACTIVITY_USERS[user_token]:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                CALL add_song_in_album({ACTIVITY_USERS[user_token]}, {album_id}, '{song_name}');
                """
            )
            connection.commit()
            cursor.execute(
                f"""
                SELECT song_id FROM song WHERE song_name = '{song_name}' AND
                album_id = {album_id} AND creator_id = {ACTIVITY_USERS[user_token]};
                """
            )
            song_id = cursor.fetchone()[0]
            return dict({
                'successfully': song_id,
                'audio_url': f'data/{ACTIVITY_USERS[user_token]}/albums/{album_id}/{song_id}.mp3'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def delete_song_on_album(song_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT song_url, creator_id FROM song WHERE song_id = {song_id};
                """
            )
            data = cursor.fetchone()
            audio_url = data[0]
            creator_id = data[1]
            if creator_id != ACTIVITY_USERS[user_token]:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                CALL delete_song_in_album({song_id});
                """
            )
            connection.commit()
            return dict({
                'successfully': audio_url
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def delete_album(album_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT creator_id FROM album WHERE album_id = {album_id};
                """
            )
            creator_id = cursor.fetchone()[0]
            if ACTIVITY_USERS[user_token] != creator_id:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                SELECT song_id FROM song WHERE album_id = {album_id};
                """
            )
            for song in cursor.fetchall():
                cursor.execute(
                    f"""
                    CALL delete_song_in_album({song[0]});
                    """
                )
                connection.commit()
            cursor.execute(
                f"""
                CALL delete_album({album_id});
                """
            )
            connection.commit()
            return dict({
                'successfully': ACTIVITY_USERS[user_token]
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def add_playlist(playlist_name, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                CALL add_playlist('{playlist_name}', {ACTIVITY_USERS[user_token]});
                """
            )
            connection.commit()
            cursor.execute(
                f"""
                SELECT playlist_id FROM playlist WHERE creator_id = {ACTIVITY_USERS[user_token]} 
                AND playlist_name = '{playlist_name}'; 
                """
            )
            playlist_id = cursor.fetchone()[0]
            return dict({
                'successfully': playlist_id,
                'cover_url': f'data/{ACTIVITY_USERS[user_token]}/playlists/{playlist_id}'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def add_song_in_playlist(playlist_id, song_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT creator_id FROM playlist WHERE playlist_id = {playlist_id};
                """
            )
            creator_id = cursor.fetchone()[0]
            if creator_id != ACTIVITY_USERS[user_token]:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                CALL add_song_in_playlist({song_id}, {playlist_id})
                """
            )
            connection.commit()
            return dict({
                'successfully': 'OK'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def delete_song_from_playlist(song_id, playlist_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT creator_id FROM playlist WHERE playlist_id = {playlist_id};
                """
            )
            creator_id = cursor.fetchone()[0]
            if ACTIVITY_USERS[user_token] != creator_id:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                CALL delete_song_in_playlist({song_id}, {playlist_id})
                """
            )
            connection.commit()
            return dict({
                'successfully': 'OK'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def delete_playlist(playlist_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT creator_id FROM playlist WHERE playlist_id = {playlist_id};
                """
            )
            creator_id = cursor.fetchone()[0]
            if ACTIVITY_USERS[user_token] != creator_id:
                return dict({
                    'error': 403
                })
            cursor.execute(
                f"""
                CALL delete_playlist({playlist_id});
                """
            )
            connection.commit()
            return dict({
                'successfully': ACTIVITY_USERS[user_token]
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def show_songs_playlist(playlist_id, user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_playlist_songs({playlist_id});
                """
            )
            dataset = cursor.fetchall()
            res = list()
            LIKED_SONG = dict()
            cursor.execute(
                f"""
                SELECT song_id FROM song_playlist_relship WHERE playlist_id = {FAVOURITE_PLAYLIST[user_token]}
                """
            )
            for data in cursor.fetchall():
                LIKED_SONG[data[0]] = user_token
            for data in dataset:
                if data[0] in LIKED_SONG.keys():
                    flag = True
                else:
                    flag = False
                res.append({
                    'songId': data[0],
                    'songName': data[1],
                    'albumId': data[2],
                    'albumName': data[3],
                    'performerId': data[4],
                    'performerName': data[5],
                    'audioUrl': data[6],
                    'coverUrl': data[7],
                    'isLiked': flag
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def like_performer(performer_id, like, user_token):
    try:
        with connection.cursor() as cursor:
            print(like)
            if like == 'true':
                cursor.execute(
                    f"""
                    CALL like_performer({performer_id}, {ACTIVITY_USERS[user_token]});
                    """
                )
                connection.commit()
            else:
                cursor.execute(
                    f"""
                    CALL dislike_performer({performer_id}, {ACTIVITY_USERS[user_token]});
                    """
                )
                connection.commit()
            return dict({
                'successfully': 'OK'
            })
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })


def show_liked_performer(user_token):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT * FROM show_liked_performers({ACTIVITY_USERS[user_token]});
                """
            )
            res = list()
            for data in cursor.fetchall():
                res.append({
                    'performerId': data[0],
                    'performerName': data[1],
                    'followers': data[2],
                    'avatarUrl': data[3],
                    'isLiked': True
                })
            return res
    except Exception as ex:
        connection.rollback()
        print(ex)
        return dict({
            'error': ex
        })
