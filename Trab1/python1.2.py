import subprocess
import sys



DATABASE_NAME = 'PRODUCTS'
DATABASE_INI = 'database.ini'

USER_NAME = 'professor'
PASSWORD = 'batatinha'



def error_handling(err):
    if err != '':
        print(err)
        sys.exit(1)
    return

def create_database_ini():
    file = f"./Trab1/{DATABASE_INI.lower()}"
    DATABASE_NAME_LOWER = DATABASE_NAME.lower()
    with open(file, 'w') as config_file:
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



if __name__ == '__main__':

    create_database()
    create_database_ini()
    create_user()
    
