import sqlite3 as db
import logging
import uuid
from datetime import datetime

class SQL: 
    def __init__ (self):
        self.conn = db.connect("agent.db")
        self.cursor = self.conn.cursor()

    def ProcUpdate(self, name, status, process):
        inserts = (name, status, process)
        current = 0
        self.cursor.execute('UPDATE processes SET hostname=?, status=? WHERE uuid=?', inserts)
        self.cursor.execute('SELECT changes()')
        if self.cursor.fetchone()[0]== 0:
            self.cursor.execute('INSERT INTO processes VALUES  (?, ?, ?)', inserts)
        self.conn.commit()

    def GetProcStatus(self, uuid):
        self.cursor.execute('SELECT status FROM processes WHERE uuid = ?', (uuid,))
        data = self.cursor.fetchone()
        self.conn.commit()
        if (data):
            return data[0]
        return data

    def GetTasks(self, name):
        self.cursor.execute('SELECT * FROM tasks WHERE hostname = ?', (name,))
        data = self.cursor.fetchall()
        self.conn.commit()
        return data;

    def GetAllTasks(self):
        self.cursor.execute('SELECT * FROM tasks')
        data = self.cursor.fetchall()
        self.conn.commit()
        return data;

    def GetAllProc(self):
        self.cursor.execute('SELECT * FROM processes')
        data = self.cursor.fetchall()
        self.conn.commit()
        return data;

    def GetAllNodes(self):
        self.cursor.execute('SELECT * FROM nodes')
        data = self.cursor.fetchall()
        self.conn.commit()
        return data;

    def NodeUpdate(self, name):
        inserts = (name, str(datetime.now()))
        current = 0
        self.cursor.execute('UPDATE nodes SET last_visit=? WHERE hostname=?', (inserts[1], inserts[0]))
        self.cursor.execute('SELECT changes()')
        if self.cursor.fetchone()[0]== 0:
            self.cursor.execute('INSERT INTO nodes (hostname, last_visit) VALUES  (?, ?)', inserts)
        self.conn.commit()

    def AddTaskTableIntoDB(self, config_data):
        try:
            self.cursor.execute('''DROP TABLE IF EXISTS tasks''')
            self.cursor.execute('''CREATE TABLE tasks
            (hostname TEXT, task TEXT, uuid TEXT)''')
            self.conn.commit()
            self.conn.close()
        except db.OperationalError:
            logging.warning("Unable to self.connect to database")
        try:
            for i in config_data:
                inserts = (i.split()[0], ' '.join(i.split()[1:]), str(uuid.uuid4()))
                self.cursor.execute("""INSERT INTO tasks VALUES  (?, ?, ?)""", inserts)
            self.conn.commit()
        except db.OperationalError:
            logging.warning("Unable to change database")

    def Finish(self):
        self.conn.close()

    def CreateDB(self):

        try:
            self.cursor.execute('''CREATE TABLE nodes
            (hostname TEXT, last_visit TEXT)''')
            self.conn.commit()
        except db.OperationalError:
            logging.basicConfig(filename='master.log', level=logging.INFO)
            logging.info("Table nodes already existed")

        try:
            self.cursor.execute('''CREATE TABLE processes
            (hostname TEXT, status TEXT, uuid TEXT)''')
            self.conn.commit()
        except db.OperationalError:
            logging.basicConfig(filename='master.log', level=logging.INFO)
            logging.info("Table processes already existed")

