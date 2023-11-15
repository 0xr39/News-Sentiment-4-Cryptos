
from dotenv import dotenv_values
env_vars = dotenv_values("../.env")

import pymysql
import warnings

def connectNewTokenSQL():
    sql_username = env_vars['sql_username']
    sql_password = env_vars['sql_password']
    sql_main_database = env_vars['sql_main_database']
    sql_hostname = env_vars['sql_hostname']
    sql_port = int(env_vars['sql_port'])
    conn = pymysql.connect(host=sql_hostname, user=sql_username,
                           passwd=sql_password, db=sql_main_database,
                           port=sql_port, connect_timeout=10)
    return conn

def insertAddrToDb(df ,sql, dataInList):
    warnings.filterwarnings("ignore")
    print("- [DATABASE] INSERT TO SQL")
    try_time = 0
    while True:
        try:
            conn = connectNewTokenSQL()
            c = conn.cursor()
            c.executemany(sql, dataInList)
            conn.commit()
            conn.close()
            print("- [DATABASE] FINISHED INSERT")
            warnings.resetwarnings()
            break
        except Exception as e:
            try_time += 1
            if try_time == 3:
                print(e)
                print("- [WARNING] Failed to insert token into db")
                warnings.resetwarnings()
                break
    

def queryDB(query):
    warnings.filterwarnings("ignore")
    print("- [DATABASE] QUERY TO SQL")
    import pandas as pd
    try_time = 0
    while True:
        try:
            conn = connectNewTokenSQL()
            results = pd.read_sql_query(query, conn)
            conn.commit()
            conn.close()
            print("- [DATABASE] FINISHED QUERY")
            warnings.resetwarnings()
            return results
        except Exception as e:
            try_time += 1
            if try_time == 3:
                print(e)
                print("- [WARNING] Failed to query db")
                warnings.resetwarnings()
                break

