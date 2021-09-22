from app.exc.anime_exception import AnimeAlreadExistsError, AnimeNotFoundError
import psycopg2
from environs import Env

env = Env()
env.read_env()

configs = {
    'host': env('DB_HOST'),
    'database': env('DB_NAME'),
    'user': env('DB_USER'),
    'password': env('DB_PASSWORD')
}

class AnimeServices:
    conn = None
    cur = None
    FIELDNAMES = ['id', 'anime', 'released_date', 'seasons']


    @classmethod
    def connect_db(cls):
        cls.conn = psycopg2.connect(**configs)
        cls.cur = cls.conn.cursor()


    @classmethod
    def commit_close_db(cls):
        cls.conn.commit()
        cls.cur.close()
        cls.conn.close()

    
    @classmethod
    def create_table(cls):
        cls.connect_db()

        cls.cur.execute("""
            CREATE TABLE IF NOT EXISTS animes (
            id             BIGSERIAL PRIMARY KEY,
            anime          VARCHAR(100) NOT NULL UNIQUE,
            released_date  DATE NOT NULL,
            seasons        INTEGER NOT NULL
        );
        """)

        cls.commit_close_db()


    @classmethod
    def create(cls, anime: str, released_date: str, seasons: int):
        datas = cls.get_all()['data']

        for data in datas:
            if data['anime'] == anime:
                raise AnimeAlreadExistsError()

        cls.create_table()
        cls.connect_db()

        cls.cur.execute(f"""
            INSERT INTO
                animes
            VALUES
                (DEFAULT, '{anime.title()}', '{released_date}', {seasons})
            RETURNING *
        """)

        getting_data = cls.cur.fetchone()
        
        cls.commit_close_db()

        processed_data = dict(zip(cls.FIELDNAMES, getting_data))
        processed_data['released_date'] = released_date
        
        return processed_data


    @classmethod
    def get_all(cls):
        cls.create_table()
        cls.connect_db()

        cls.cur.execute("""
            SELECT * FROM animes;
        """)

        getting_data = cls.cur.fetchall()

        cls.commit_close_db()

        if len(getting_data) > 0:
            processed_data = [dict(zip(cls.FIELDNAMES, row)) for row in getting_data]
            
            for data in processed_data:
                data['released_date'] = data['released_date'].strftime('%d/%m/%Y')
        else:
            processed_data = []
        
        return {'data': processed_data}


    @classmethod
    def get_by_id(cls, id: int):
        cls.connect_db()

        cls.cur.execute("""
            SELECT * FROM animes WHERE id=(%s);
        """, (id, ))

        getting_data = cls.cur.fetchone()

        cls.commit_close_db()

        if not getting_data:
            raise AnimeNotFoundError()

        processed_data = dict(zip(cls.FIELDNAMES, getting_data))
        processed_data['released_date'] = processed_data['released_date'].strftime('%d/%m/%Y')
        
        return {'data': processed_data}


    @classmethod
    def update(cls, id: int, data):
        update_data = cls.get_by_id(id)['data']
        
        cls.connect_db()
        
        if not update_data:
            raise AnimeNotFoundError()

        update_data.update(data)

        cls.cur.execute(f"""
            UPDATE
                animes
            SET
                anime= '{update_data['anime']}', 
                released_date= '{update_data['released_date']}', 
                seasons= '{update_data['seasons']}'
            WHERE
                id=({id})
            RETURNING *
        """)

        getting_data = cls.cur.fetchone()

        cls.commit_close_db()

        processed_data = dict(zip(cls.FIELDNAMES, getting_data))
        processed_data['released_date'] = processed_data['released_date'].strftime('%d/%m/%Y')
        
        return processed_data



    @classmethod
    def delete(cls, id: int):
        cls.connect_db()

        cls.cur.execute("""
            DELETE FROM
                animes
            WHERE
                id=(%s)
            RETURNING *
        """, (id, ))

        getting_data = cls.cur.fetchone()

        cls.commit_close_db()

        if not getting_data:
            raise AnimeNotFoundError()

        return ''


    @classmethod
    def validate_keys(cls, data):
        error = None

        fields = cls.FIELDNAMES[1:]

        for key in data.keys():
            if key not in fields:
                if not error:
                    error = {
                        "available_keys": fields,
                        "wrong_keys_sended": [key]
                    }
                else:
                    error['wrong_keys_sended'].append(key)
        
        # if error:
        #     raise KeyError(error)

        return error