import subprocess
import psycopg2
import sys
from configparser import ConfigParser
import os



DATABASE_NAME = 'PRODUCTS'
DATABASE_INI = 'database.ini'

USER_NAME = 'professor'
PASSWORD = 'batatinha'





def error_handling(err):
    if err != '':
        print(err)
        sys.exit(1)
    return

def resolve_path(file_name):
    current_dir_path = os.path.dirname(__file__)
    file_path = f"{current_dir_path}/{file_name}"
    return file_path



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

def create_tables(my_cursor):
    """ Create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE PRODUCT (
            PRODUCT_ID INT UNIQUE,
            ASIN CHAR(10) NOT NULL,
            TITLE VARCHAR(100),
            PRODUCT_GROUP VARCHAR(100),
            SALES_RANK INT,
            PRIMARY KEY (PRODUCT_ID,ASIN)
        )
        """,
        """ CREATE TABLE PRODUCT_SIMILAR (
                PRODUCT_ID INT,
                SIMILAR_ASIN CHAR(10),
                PRIMARY KEY (PRODUCT_ID, SIMILAR_ASIN),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
                )
        """,
        """
        CREATE TABLE CATEGORY (
                CATEGORY_NAME VARCHAR(100),
                CATEGORY_ID INT,
                PARENT_ID INT NULL,
                PRIMARY KEY (CATEGORY_ID),
                FOREIGN KEY (PARENT_ID) REFERENCES CATEGORY(CATEGORY_ID)
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
                PRODUCT_ID INT,
                REVIEW_DATE DATE,
                CUSTOMER_ID CHAR(14),
                REVIEW_RATING RATING,
                PRIMARY KEY (PRODUCT_ID,CUSTOMER_ID),
                FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCT(PRODUCT_ID)
                
        )
        """)
    try:
        for command in commands:
            my_cursor.execute(command)
        my_connection.commit()
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)




if __name__ == '__main__':

    create_database()
    create_database_ini(DATABASE_INI)
    create_user()
    config = load_config()
    my_connection = connect(config)
    my_cursor = create_cursor(my_connection)
    create_tables(my_cursor)    
    close_connection(my_connection)