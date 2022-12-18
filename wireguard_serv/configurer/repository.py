import psycopg2


# todo change to env variable
conn = psycopg2.connect(dbname='friends_vpn', user='postgres',
                        password='2846', host='postgres')
cursor = conn.cursor()

cursor.execute(


def example1():
    cursor.execute(
        'SELECT * FROM engine_airport WHERE city_code = %(city_code)s',
        {'city_code': 'ALA'}
    )