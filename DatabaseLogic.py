import sqlite3 as db
import logging
import uuid
from datetime import datetime

def ProcUpdate(name, status, process):
    inserts = (name, status, process)
    conn = db.connect("agent.db")
    current = 0
    cursor = conn.cursor()
    cursor.execute('UPDATE processes SET hostname=?, status=? WHERE uuid=?', inserts)
    cursor.execute('SELECT changes()')
    if cursor.fetchone()[0]== 0:
        cursor.execute('INSERT INTO processes VALUES  (?, ?, ?)', inserts)
    conn.commit()
    conn.close()

def GetProcStatus(uuid):
    conn = db.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM processes WHERE uuid = ?', (uuid,))
    data = cursor.fetchone()
    conn.commit()
    conn.close()
    if (data):
        return data[0]
    return data


def GetTasks(name):
    conn = db.connect("agent.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE hostname = ?', (name,))
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data;

def NodeUpdate(name):
    inserts = (name, str(datetime.now()))
    conn = db.connect("agent.db")
    current = 0
    cursor = conn.cursor()
    cursor.execute('UPDATE nodes SET last_visit=? WHERE hostname=?', (inserts[1], inserts[0]))
    cursor.execute('SELECT changes()')
    if cursor.fetchone()[0]== 0:
        cursor.execute('INSERT INTO nodes (hostname, last_visit) VALUES  (?, ?)', inserts)
    conn.commit()
    conn.close()

def AddTaskTableIntoDB(config_data):
    try:
        conn = db.connect("agent.db")
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS tasks''')
        cursor.execute('''CREATE TABLE tasks
        (hostname TEXT, task TEXT, uuid TEXT)''')
        conn.commit()
        conn.close()
    except db.OperationalError:
        logging.warning("Unable to connect to database")
    try:
        conn = db.connect("agent.db")
        cursor = conn.cursor()
        for i in config_data:
            inserts = (i.split()[0], ' '.join(i.split()[1:]), str(uuid.uuid4()))
            cursor.execute("""INSERT INTO tasks VALUES  (?, ?, ?)""", inserts)
        conn.commit()
        conn.close()
    except db.OperationalError:
        logging.warning("Unable to change database")


def CreateDB():

    try:
        conn = db.connect("agent.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE nodes
        (hostname TEXT, last_visit TEXT)''')
        conn.commit()
        conn.close()
    except db.OperationalError:
        logging.basicConfig(filename='master.log', level=logging.INFO)
        logging.info("Table nodes already existed")

    try:
        conn = db.connect("agent.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE processes
        (hostname TEXT, status TEXT, uuid TEXT)''')
        conn.commit()
        conn.close()
    except db.OperationalError:
        logging.basicConfig(filename='master.log', level=logging.INFO)
        logging.info("Table processes already existed")

