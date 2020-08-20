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
            type TEXT(255)
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

        return BookkeepingDB

    def AddData(data, idData, bd_i):
        db = DB.connectBD()
        cursor = db.cursor()
        if bd_i == 0:
            cursor.execute("INSERT INTO Expenses(deleteFlag, price, product, Exdate, type) VALUES(?,?,?,?,?)", (False, data['price'], data['product'], data['date'], data['type']))
        else:
            cursor.execute("INSERT INTO Income(deleteFlag, price, product, Incdate, type) VALUES(?,?,?,?,?)", (False, data['price'], data['product'], data['date'], data['type']))
        db.commit()

    def SelectData(data='ALL',number=0, bd_i=0):
        bd = DB.connectBD()
        cursor = bd.cursor()
        dataOutput = []
        if bd_i == 0:
            if data == 'ALL':
                for item in cursor.execute(f"SELECT * FROM Expenses WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'price':
                for item in cursor.execute(f"SELECT price FROM Expenses WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'product':
                for item in cursor.execute(f"SELECT product FROM Expenses WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'date':
                for item in cursor.execute(f"SELECT Exdate FROM Expenses WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'type':
                for item in cursor.execute(f"SELECT type FROM Expenses WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
        else:
            if data == 'ALL':
                for item in cursor.execute(f"SELECT * FROM Income WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'price':
                for item in cursor.execute(f"SELECT price FROM Income WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'product':
                for item in cursor.execute(f"SELECT product FROM Income WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'date':
                for item in cursor.execute(f"SELECT Incdate FROM Income WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
            elif data == 'type':
                for item in cursor.execute(f"SELECT type FROM Income WHERE deleteFlag = {0}"):
                    dataOutput.append(item)
        bd.commit()
        return dataOutput


    def DeleteData(row, bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        i = 1
        if bd_i == 0:
            for idItem in cursor.execute(f"SELECT id FROM Expenses WHERE deleteFlag = {0}"):
                if i == row:
                    id_delete = idItem[0]
                    break
                i += 1
            cursor.execute(f"UPDATE Expenses SET deleteFlag = {True} WHERE id = {id_delete}")
        else:
            for idItem in cursor.execute(f"SELECT id FROM Income WHERE deleteFlag = {0}"):
                if i == row:
                    id_delete = idItem[0]
                    break
                i += 1
            cursor.execute(f"UPDATE Income SET deleteFlag = {True} WHERE id = {id_delete}")
        bd.commit()

    def UpdateData(id_start, id_new, bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        if bd_i == 0:
            cursor.execute(f"UPDATE Expenses SET id = {id_new} WHERE id = {id_start}")
        bd.commit()


    def ClearAll(bd_i):
        bd = DB.connectBD()
        cursor = bd.cursor()
        if bd_i == 0:
            cursor.execute(f"DELETE FROM Expenses")
        else:
            cursor.execute(f"DELETE FROM Income")
        bd.commit()