import sqlite3

class DB(object):
    """docstring for DB"""
    def __init__(self):
        super().__init__()


    def connectBD():
        BookkeepingDB = sqlite3.connect('bookkeeping.db')

        cursor = BookkeepingDB.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS Expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deleteFlag BOOLEAN NOT NULL,
            price INT NOT NULL,
            product TEXT(255) NOT NULL,
            ExDate DATETIME NOT NULL,
            type TEXT(255) NOT NULL
            )""")
        BookkeepingDB.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS Income(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deleteFlag BOOLEAN NOT NULL,
            price INT NOT NULL,
            product TEXT(255) NOT NULL,
            IncDate DATETIME NOT NULL,
            type TEXT(255) NOT NULL
            )""")
        BookkeepingDB.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS Took(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deleteFlag BOOLEAN NOT NULL,
            price INT NOT NULL,
            fromWhom TEXT(255) NOT NULL,
            tookDate DATETIME NOT NULL
            )""")
        BookkeepingDB.commit()

        cursor.execute("""CREATE TABLE IF NOT EXISTS Gave(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deleteFlag BOOLEAN NOT NULL,
            price INT NOT NULL,
            whom TEXT(255) NOT NULL,
            gaveDate DATETIME NOT NULL
            )""")
        BookkeepingDB.commit()

        return BookkeepingDB

    def AddData(data, bd_i):
        db = DB.connectBD()
        cursor = db.cursor()
        if bd_i == 0:
            cursor.execute("INSERT INTO Expenses(deleteFlag, price, product, Exdate, type) VALUES(?,?,?,?,?)", (False, data['price'], data['product'], data['date'], data['type']))
        elif bd_i == 1:
            cursor.execute("INSERT INTO Income(deleteFlag, price, product, Incdate, type) VALUES(?,?,?,?,?)", (False, data['price'], data['product'], data['date'], data['type']))
        elif bd_i == 2:
            cursor.execute("INSERT INTO Took(deleteFlag, price, fromWhom, tookDate) VALUES(?,?,?,?)", (False, data['price'], data['fromWhom'], data['date']))
        elif bd_i == 3:
            cursor.execute("INSERT INTO Gave(deleteFlag, price, whom, gaveDate) VALUES(?,?,?,?)", (False, data['price'], data['whom'], data['date']))
        db.commit()


    def SelectData(data='ALL',number=0, bd_i=0):
        bd = DB.connectBD()
        cursor = bd.cursor()
        dataOutput = []
        if bd_i == 0:
            for i in cursor.execute(f"SELECT * FROM Expenses WHERE deleteFlag = {0}"):
                item = {}
                item['id'] = i[0]
                item['price'] = i[2]
                item['product'] = i[3]
                item['date'] = datetime.strptime(i[4], '%Y-%m-%d').date()
                item['type'] = i[5]
                dataOutput.append(item)
        elif bd_i == 1:
            for i in cursor.execute(f"SELECT * FROM Income WHERE deleteFlag = {0}"):
                item = {}
                item['id'] = i[0]
                item['price'] = i[2]
                item['product'] = i[3]
                item['date'] = datetime.strptime(i[4], '%Y-%m-%d').date()
                item['type'] = i[5]
                dataOutput.append(item)
        elif bd_i == 2:
            for i in cursor.execute(f"SELECT * FROM Took WHERE deleteFlag = {0}"):
                item = {}
                item['id'] = i[0]
                item['price'] = i[2]
                item['fromWhom'] = i[3]
                item['tookDate'] = datetime.strptime(i[4], '%Y-%m-%d').date()
                dataOutput.append(item)
        elif bd_i == 3:
            for i in cursor.execute(f"SELECT * FROM Gave WHERE deleteFlag = {0}"):
                item = {}
                item['id'] = i[0]
                item['price'] = i[2]
                item['Whom'] = i[3]
                item['gaveDate'] = datetime.strptime(i[4], '%Y-%m-%d').date()
                dataOutput.append(item)
        bd.commit()
        return dataOutput


    def DeleteData(id_row,bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        if bd_i == 0:
            cursor.execute(f"UPDATE Expenses SET deleteFlag = {True} WHERE id = {id_row}")
        elif bd_i == 1:
            cursor.execute(f"UPDATE Income SET deleteFlag = {True} WHERE id = {id_row}")
        bd.commit()

    def UpdateData(id_start, id_new, bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        if bd_i == 0:
            cursor.execute(f"UPDATE Expenses SET id = {id_new} WHERE id = {id_start}")
        elif bd_i == 1:
            pass
        bd.commit()


    def ClearAll(bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        if bd_i == 0:
            cursor.execute(f"DELETE FROM Expenses")
        elif bd_i == 1:
            cursor.execute(f"DELETE FROM Income")
        bd.commit()