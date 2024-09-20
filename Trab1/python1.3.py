from configparser import ConfigParser
import psycopg2
import os

def resolve_path(file_name):
    current_dir_path = os.path.dirname(__file__)
    file_path = f"{current_dir_path}/{file_name}"
    return file_path


def load_config(file_name='database.ini', section='postgresql'):
    parser = ConfigParser()
    file_path = resolve_path(file_name)
    
    parser.read(file_path)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, file_path))

    return config



def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        my_connection = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

    return my_connection

def close_connection(my_connection):
    try:
        my_connection.close()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def create_cursor(my_connection):
    try:
        my_cursor = my_connection.cursor()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    
    return my_cursor

def query_1(cursor):
    product_id = 3  # Substitua pelo ID do produto desejado

    # Query para obter os 5 comentários mais úteis e com maior avaliação
    query_high_rating = """
        SELECT REVIEW_ID, CUSTOMER_ID, REVIEW_RATING, HELPFUL, VOTE
        FROM REVIEW
        WHERE PRODUCT_ID = %s
        ORDER BY REVIEW_RATING DESC, HELPFUL DESC
        LIMIT 5;
    """

    # Query para obter os 5 comentários mais úteis e com menor avaliação
    query_low_rating = """
        SELECT REVIEW_ID, CUSTOMER_ID, REVIEW_RATING, HELPFUL, VOTE
        FROM REVIEW
        WHERE PRODUCT_ID = %s
        ORDER BY REVIEW_RATING ASC, HELPFUL DESC
        LIMIT 5;
    """

    # Executar a query para comentários com maior avaliação
    cursor.execute(query_high_rating, (product_id,))
    high_rating_reviews = cursor.fetchall()

    # Executar a query para comentários com menor avaliação
    cursor.execute(query_low_rating, (product_id,))
    low_rating_reviews = cursor.fetchall()

    # Exibir os resultados
    print("5 Comentários mais úteis com maior avaliação:")
    for review in high_rating_reviews:
        print(review)

    print("\n5 Comentários mais úteis com menor avaliação:")
    for review in low_rating_reviews:
        print(review)

if __name__ == '__main__':

    config = load_config()
    my_connection = connect(config)
    my_cursor = create_cursor(my_connection)
    query_1(my_cursor)
    close_connection(my_connection)