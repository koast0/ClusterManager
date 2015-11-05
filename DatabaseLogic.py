import sqlite3 as db
from datetime import datetime

def AddTaskDb(name, status, process):

def UpdateDB(name):
    inserts = (str(datetime.now()), name)
    conn = db.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute('UPDATE nodes SET last_visit=? WHERE hostname=?;', inserts)
    conn.commit()
    conn.close()


def CreateDB():

    try:
        conn = db.connect("agent.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE nodes
        (hostname TEXT, last_visit TEXT)'''
        cursor.execute('''CREATE TABLE processes
        (hostname TEXT, uuid TEXT, status TEXT)'''
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        logging.basicConfig(filename='master.log', level=logging.INFO)
        logging.info("Database already existed")
