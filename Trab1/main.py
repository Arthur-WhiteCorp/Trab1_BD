import subprocess
import sys
from configparser import ConfigParser

DATABASE_NAME = 'PRODUCTS'
DATABASE_INI = 'database.ini'

USER_NAME = 'professor'
PASSWORD = 'batatinha'

def extract_names(db_list):
    # Split the output into lines
    lines = db_list.stdout.splitlines()
    db_names = []

    # Flag to identify the start of the database list
    in_db_list = False

    for line in lines:
        line = line.strip()

        # Identify the start of the database list section
        if line.startswith('List of databases'):
            in_db_list = True
            continue
        
        # Identify the end of the database list section
        if in_db_list and line == '':
            break
        
        # Process lines within the database list section
        if in_db_list and line and not line.startswith('Name') and not line.startswith('---'):
            # Split the line by '|', which is used for formatting in psql output
            parts = line.split('|')
            # The database name is usually the first part
            db_name = parts[0].strip()
            if db_name and db_name != '(4 rows)':  # Add the name to the list if it's not empty or the row count
                db_names.append(db_name)

    return db_names


def error_handling(err):
    if err != '':
        print(err)
        sys.exit(1)
    return

def create_database_ini():
    file = DATABASE_INI.lower()
    with open(file, 'w') as config_file:
        config_file.write("[postgresql]\n")
        config_file.write("host=localhost\n")
        config_file.write("database=suppliers\n")
        config_file.write(f"user={USER_NAME}\n")
        config_file.write(f"password={PASSWORD}\n")


def create_database():
    result = subprocess.run(['sudo',"-u" , "postgres" , "psql",'-d' ,'postgres','-c' , 
                            f'CREATE DATABASE {DATABASE_NAME};'],capture_output=True,text=True)
    error_handling(result.stderr)
    create_database_ini()

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

def remove_access():
    USER_NAME_LOWER = USER_NAME.lower()
    DATABASE_NAME_LOWER = DATABASE_NAME.lower()

    db_list = subprocess.run(['sudo', '-u', "postgres", "psql",'-d', 'postgres', '-c', '\l'],
                         capture_output=True, text=True)
    error_handling(db_list.stderr)
    db_names = extract_names(db_list)
    for db_name in db_names:
        if db_name.lower() != DATABASE_NAME_LOWER:

            revoke_command = f"REVOKE CONNECT ON DATABASE {db_name} FROM {USER_NAME_LOWER};"
            revoke_user_access = subprocess.run(['sudo', "-u", "postgres", 'psql', '-d', "postgres", '-c', revoke_command],
                        capture_output=True, text=True)
            error_handling(revoke_user_access.stderr)

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config


if __name__ == '__main__':

    create_database()
    create_user()
    remove_access()
    config = load_config()
    print(config)