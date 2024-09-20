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
        
def query_2(cursor):
    product_id = 2  # Substitua pelo ID do produto desejado

    # Query para listar os produtos similares com maiores vendas
    query_similar_products = """
        SELECT p_sim.SIMILAR_ASIN, p2.TITLE, p2.SALES_RANK
        FROM PRODUCT p
        JOIN PRODUCT_SIMILAR p_sim ON p.PRODUCT_ID = p_sim.PRODUCT_ID
        JOIN PRODUCT p2 ON p_sim.SIMILAR_ASIN = p2.ASIN
        WHERE p.PRODUCT_ID = %s
        AND p2.SALES_RANK < p.SALES_RANK;
    """

    # Executar a query
    cursor.execute(query_similar_products, (product_id,))
    similar_products = cursor.fetchall()

    # Exibir os resultados
    print("Produtos similares com maiores vendas:")
    for product in similar_products:
        print(f"ASIN: {product[0]}, Título: {product[1]}, Ranking de Vendas: {product[2]}")

def query_3(cursor):
    product_id = 2 
    query_avg_rating = """ SELECT REVIEW_1.REVIEW_DATE, avg(REVIEW_2.REVIEW_RATING)
                           FROM REVIEW AS REVIEW_1 ,REVIEW AS REVIEW_2
                           WHERE REVIEW_1.REVIEW_DATE >= REVIEW_2.REVIEW_DATE
                           and REVIEW_1.PRODUCT_ID = %s
                           and REVIEW_2.PRODUCT_ID = REVIEW_1.PRODUCT_ID
                           GROUP BY REVIEW_1.REVIEW_DATE
                           ORDER BY REVIEW_1.REVIEW_DATE"""

    cursor.execute(query_avg_rating, (product_id,))
    ratings = cursor.fetchall()


    print("EVOLUÇÃO DAS MÉDIAS:")
    for rating in ratings:
        print(f"DATE: {rating[0]}, RATING_AVG: {rating[1]}")
        
def query_4(cursor):
    my_query = """  
              WITH RankedProducts AS (
              SELECT 
                  ASIN,
                  TITLE,
                  PRODUCT_GROUP,
                  SALES_RANK,
                  ROW_NUMBER() OVER (PARTITION BY PRODUCT_GROUP ORDER BY SALES_RANK) AS rank
              FROM 
                  PRODUCT
      )
      SELECT 
          ASIN,
          TITLE,
          PRODUCT_GROUP,
          SALES_RANK
      FROM 
          RankedProducts
      WHERE 
          rank <= 10
      ORDER BY 
          PRODUCT_GROUP, SALES_RANK"""

    cursor.execute(my_query)
    answers = cursor.fetchall()

    print("Resposta:")
    for answer in answers:
        if answer[1] and answer[2] and answer[3]:
            print(answer)
        


if __name__ == '__main__':

    config = load_config()
    my_connection = connect(config)
    my_cursor = create_cursor(my_connection)
    # query_1(my_cursor)
    query_4(my_cursor)
    close_connection(my_connection)
