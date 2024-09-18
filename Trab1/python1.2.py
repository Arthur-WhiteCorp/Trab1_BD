import subprocess
import psycopg2
import sys
from configparser import ConfigParser
import os
from datetime import datetime

from get_data import lista_produtos
from get_data import Similar
from get_data import CategoriesSub
from get_data import Review
from get_data import ReviewSub


DATABASE_NAME = 'PRODUCTS'
DATABASE_INI = 'database.ini'

USER_NAME = 'professor'
PASSWORD = 'batatinha'

def error_handling(err):
    if err != '':
        print(err)
        sys.exit(1)
    return

def create_database_ini(file_name):

    file_path = resolve_path(file_name)
    DATABASE_NAME_LOWER = DATABASE_NAME.lower()
    with open(file_path, 'w') as config_file:
        config_file.write("[postgresql]\n")
        config_file.write("host=localhost\n")
        config_file.write(f"database={DATABASE_NAME_LOWER}\n")
        config_file.write(f"user={USER_NAME}\n")
        config_file.write(f"password={PASSWORD}\n")


def create_database():
    result = subprocess.run(['sudo',"-u" , "postgres" , "psql",'-d' ,'postgres','-c' , 
                            f'CREATE DATABASE {DATABASE_NAME};'],capture_output=True,text=True)
    error_handling(result.stderr)

def create_user():
    USER_NAME_LOWER = USER_NAME.lower()
    DATABASE_NAME_LOWER = DATABASE_NAME.lower()


    create_user_command = f"CREATE USER {USER_NAME_LOWER} WITH PASSWORD '{PASSWORD}';"
    user_credentials = subprocess.run(['sudo',"-u" , "postgres", "psql", "-d",  "postgres",'-c' ,
                            create_user_command],capture_output=True,text=True)
    error_handling(user_credentials.stderr)

    grant_access_command = f"GRANT CONNECT ON DATABASE {DATABASE_NAME_LOWER} TO {USER_NAME_LOWER};"
    grant_user_access_to_db = subprocess.run(['sudo',"-u" , "postgres" ,'psql','-d' , "postgres",'-c' , 
                            grant_access_command],capture_output=True,text=True)
    error_handling(grant_user_access_to_db.stderr)


    permission_command = f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {USER_NAME_LOWER};"
    give_user_permissions = subprocess.run(['sudo',"-u" , "postgres" ,'psql','-d' ,DATABASE_NAME_LOWER,'-c' , 
                            permission_command],capture_output=True,text=True)
    error_handling(give_user_permissions.stderr)

def resolve_path(file_name):
    current_dir_path = os.getcwd()
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

def close_cursor(my_cursor):
    try:
        my_cursor.close()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def create_cursor(my_connection):
    try:
        my_cursor = my_connection.cursor()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    
    return my_cursor

def create_tables(my_connection,my_cursor):
    """ Create tables in the PostgreSQL database"""
    commands = (
        # TABLE PRODUCT OK
        """
        CREATE TABLE PRODUCT (
            PRODUCT_ID INT UNIQUE,
            ASIN CHAR(10) NOT NULL,
            TITLE VARCHAR,
            PRODUCT_GROUP VARCHAR,
            SALES_RANK INT,
            PRIMARY KEY (PRODUCT_ID,ASIN)
        )
        """,
        """ CREATE TABLE PRODUCT_SIMILAR (
                PRODUCT_ID INT,
                SIMILAR_ASIN CHAR(10),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID),
                PRIMARY KEY (PRODUCT_ID, SIMILAR_ASIN)
                )
        """,
        """
        CREATE TABLE CATEGORY (
                CATEGORY_NAME VARCHAR(100),
                CATEGORY_ID INT,
                PARENT_ID INT NULL,
                PRIMARY KEY (CATEGORY_ID),
                FOREIGN KEY (PARENT_ID) REFERENCES CATEGORY(CATEGORY_ID),
                UNIQUE (CATEGORY_NAME, CATEGORY_ID)
        )
        """,
        """
        CREATE TABLE PRODUCT_CATEGORY (
                PRODUCT_ID INT,
                CATEGORY_ID INT,
                PRIMARY KEY (PRODUCT_ID, CATEGORY_ID),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID),
                FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORY(CATEGORY_ID)
        )
        """,
        """
        CREATE DOMAIN RATING AS INT CHECK( VALUE > 0 AND VALUE<=5 )
        """,
        
        """
        CREATE TABLE REVIEW (
                REVIEW_ID INTEGER GENERATED ALWAYS AS IDENTITY,
                PRODUCT_ID INT,
                REVIEW_DATE DATE,
                CUSTOMER_ID CHAR(14),
                REVIEW_RATING RATING,
                VOTE INT,
                HELPFUL INT,
                PRIMARY KEY (PRODUCT_ID,CUSTOMER_ID, REVIEW_ID),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
                
        )
        """)
    try:
        for command in commands:
            my_cursor.execute(command)
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)



def insert_into_product(my_connection, my_cursor, PRODUCT_ID:int, ASIN:str, TITLE:str, PRODUCT_GROUP:str, SALES_RANK:int ):
    command = f"""INSERT INTO PRODUCT (PRODUCT_ID, ASIN, TITLE, PRODUCT_GROUP, SALES_RANK) 
                  VALUES (%s,%s,%s,%s,%s)"""
    try:
        my_cursor.execute(command, (PRODUCT_ID, ASIN, TITLE, PRODUCT_GROUP, SALES_RANK))
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)    


def insert_into_product_similar(my_connection, my_cursor, PRODUCT_ID:int, SIMILAR_ASIN:str):
    command = f"""INSERT INTO PRODUCT_SIMILAR (PRODUCT_ID, SIMILAR_ASIN) 
                  VALUES (%s,%s)"""
    try:
        my_cursor.execute(command, (PRODUCT_ID, SIMILAR_ASIN))
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def insert_into_category(my_connection, my_cursor, CATEGORY_NAME:str, CATEGORY_ID:int ,PARENT_ID:int):
    command = f"""INSERT INTO CATEGORY (CATEGORY_NAME, CATEGORY_ID, PARENT_ID) 
                  VALUES (%s,%s,%s) ON CONFLICT (CATEGORY_NAME, CATEGORY_ID) DO NOTHING"""
    try:
        my_cursor.execute(command, (CATEGORY_NAME, CATEGORY_ID, PARENT_ID))
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        my_connection.rollback()


def insert_into_product_category(my_connection, my_cursor, PRODUCT_ID:int , CATEGORY_ID:int):
    command = f"""INSERT INTO PRODUCT_CATEGORY (PRODUCT_ID, CATEGORY_ID) 
                  VALUES (%s,%s)"""
    try:
        my_cursor.execute(command, (PRODUCT_ID, CATEGORY_ID))
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)   

def insert_into_review(my_connection, my_cursor, PRODUCT_ID:int, REVIEW_DATE:str, CUSTOMER_ID:str, REVIEW_RATING:int, VOTE: int, HELPFUL: int):
    command = """INSERT INTO review (PRODUCT_ID, REVIEW_DATE, CUSTOMER_ID, REVIEW_RATING, VOTE, HELPFUL)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
    try:
        my_cursor.execute(command, (PRODUCT_ID, REVIEW_DATE, CUSTOMER_ID, REVIEW_RATING, VOTE, HELPFUL))
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        my_connection.rollback()
        print(error)
        
def map_product_list(my_connection, my_cursor):
    for product in lista_produtos:
        if product.title == '' and product.group == '' and product.salesrank == '':
            product.title = None
            product.group = None
            product.salesrank = None
        insert_into_product(my_connection, my_cursor, product.id, product.asin, product.title, product.group, product.salesrank)
        if isinstance(product.similar, Similar):
            similar_ids_list = product.similar.ids
            # map_similar_list(my_connection, my_cursor, product.id, similar_ids_list)
        # map_category_list(my_connection, my_cursor, product.categories_sub)
        map_review_list(my_connection, my_cursor, product.id, product.reviews_sub)
        
def map_similar_list(my_connection, my_cursor, product_id, similar_ids_list):
    if len(similar_ids_list) == 0:
        None
    else:    
        for similar_id in similar_ids_list:
            insert_into_product_similar(my_connection, my_cursor, product_id, similar_id)
        
def map_category_list(my_connection, my_cursor, categories):
    if len(categories) == 0:
        None
    else:
        for category_index in range(len(categories)):
            child_category = categories[category_index]
            while (child_category != None):
                if child_category.parent_id == "":
                    insert_into_category(my_connection, my_cursor, child_category.name, child_category.id, None)
                else:
                    insert_into_category(my_connection, my_cursor, child_category.name, child_category.id, child_category.parent_id)
                child_category = child_category.sub
                
def map_review_list(my_connection, my_cursor, product_id, review_list):
    if len(review_list) == 0:
        None
    else:
        for review in review_list:
            review_date = datetime.strptime(review.date, "%Y-%m-%d")
            insert_into_review(my_connection, my_cursor, product_id, review_date, review.customer, review.rating, review.votes, review.helpful)
    
if __name__ == '__main__':

    create_database()
    create_database_ini(DATABASE_INI)
    #create_user()
    config = load_config()
    my_connection = connect(config)
    my_cursor = create_cursor(my_connection)
    create_tables(my_connection,my_cursor)
    map_product_list(my_connection,my_cursor)
    close_cursor(my_cursor)
    close_connection(my_connection)