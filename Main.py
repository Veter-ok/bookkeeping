import sys
from datetime import date
import sqlite3
import csv
import numpy
import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtCore import QDate


class Bookkepping(QMainWindow):
	def __init__(self):
		super().__init__()
		self.db_controller = DB_Controller()
		self.currently_user = ""
		self.utils = Utils()
		uic.loadUi("MainWindow.ui", self)
		self.nowDate = date.today()
		self.payments = []
		self.total = 0

		self.userForm = UserFormWindow(self)
		self.radioBtnIncome1.setChecked(True)
		self.paymentDate.setMaximumDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.paymentDate.setDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.btnAddUser.clicked.connect(self.openUserFormWindow)
		self.btnImportPayments.clicked.connect(self.importPayments)
		self.btnExportPayments.clicked.connect(self.exportPayments)
		self.btnChart.clicked.connect(self.showChart)
		self.btnAddData.clicked.connect(self.addData)
		self.btnAddType.clicked.connect(self.addType)
		self.btnDeletePayment.clicked.connect(self.deletePayment)
		self.btnDeleteType.clicked.connect(self.deleteType)
		self.radioBtnIncome1.toggled.connect(self.changePaymentTypes)
		self.radioBtnExpense1.toggled.connect(self.changePaymentTypes)
		self.sortBy.currentIndexChanged.connect(self.sortPaymnets)
		self.selectAllUsers()
		self.selectUser()
		self.choseUsers.currentIndexChanged.connect(self.selectUser)

	def thereIsUser(self, msg=True):
		if self.choseUsers.currentText() == "":
			if msg:
				self.errorMsg("Ошибка", "Добавьте пользователя")
			return False
		return True

	def selectUser(self):
		if self.thereIsUser(msg=False):
			name, login = self.choseUsers.currentText().split()
			login = login[1:-1]
			self.db_controller.setUser(login)
			self.currently_user = login
			for _ in range(self.tablePayments.rowCount()):
				self.tablePayments.removeRow(0)
			self.total = 0
			self.labelTotal.setText(f"Капитал: 0$")
			self.setPayments()
			self.setTypes()

	def selectAllUsers(self):
		users = self.db_controller.getAllUsers()
		for user in users:
			self.choseUsers.addItem(f"{user[0]} ({user[1]})")

	def openUserFormWindow(self):
		self.userForm.show()

	def addUser(self, user, login):
		status = self.db_controller.addUser(login, user)
		if status != "error":
			self.choseUsers.addItem(f"{user} ({login})")

	def setPayments(self):
		new_payments = self.db_controller.getPayments()
		for index, payment in enumerate(new_payments):
			self.addPaymentInTable(index, payment)
			self.updateTotal(payment['price'], payment['isIncome'])
			self.payments.append(payment)
		self.labelTotal.setText(f"Капитал: {self.total}$")

	def updatePayments(self, payments):
		for _ in range(self.tablePayments.rowCount()):
			self.tablePayments.removeRow(0)
		for index, payment in enumerate(payments):
			self.addPaymentInTable(index, payment)
	
	def addPaymentInTable(self, index, payment):
		if self.thereIsUser():
			self.tablePayments.insertRow(index)
			if payment['isIncome']:
				self.tablePayments.setItem(index, 0, QTableWidgetItem(f"+{str(payment['price'])}"))
			else:
				self.tablePayments.setItem(index, 0, QTableWidgetItem(f"-{str(payment['price'])}"))
			self.tablePayments.setItem(index, 1, QTableWidgetItem(payment['type']))
			self.tablePayments.setItem(index, 2, QTableWidgetItem(payment['comment']))
			self.tablePayments.setItem(index, 3, QTableWidgetItem(payment['date']))
	
	def setTypes(self, income=True):
		types = self.db_controller.getTypes()
		key = 'incomeTypes' if income else 'expenseTypes'
		self.paymentType.clear()
		self.deleteTypes.clear()
		for name in types[key]:
			self.paymentType.addItem(name[0]) 
		for name in types['incomeTypes'] + types['expenseTypes']:
			self.deleteTypes.addItem(name[0])

	def deletePayment(self):
		if self.thereIsUser():
			msg = f"Вы уверены, что хотите удалить платёж "
			result = QMessageBox.question(self, 'MessageBox', msg, QMessageBox.Yes | QMessageBox.No)
			if result == QMessageBox.Yes:
				index = self.indexPayment.value() - 1
				payment = self.payments[index]
				self.payments.remove(payment)
				self.tablePayments.removeRow(index)
				self.db_controller.deletePayemnt(payment['id'])

	def changePaymentTypes(self):
		if self.radioBtnIncome1.isChecked():
			self.setTypes(True)
		elif self.radioBtnExpense1.isChecked():
			self.setTypes(False)

	def updateTotal(self, price, isIncome):
		if isIncome:
			self.total += price
		else:
			self.total -= price
		self.labelTotal.setText(f"Капитал: {self.total}$")

	def sortPaymnets(self):
		sortby = self.sortBy.currentText()
		if sortby == "дате":
			self.payments = sorted(self.payments, key=lambda x: x['date'])[::-1]
		elif sortby == 'сумме':
			self.payments = sorted(self.payments, key=lambda x: x['price'])[::-1]
		elif sortby == 'категории':
			self.payments = sorted(self.payments, key=lambda x: x['type'])
		self.updatePayments(self.payments)

	def addData(self):
		if self.thereIsUser():
			newPayment = {}
			newPayment['isIncome'] = self.radioBtnIncome1.isChecked()
			newPayment['price'] = int(self.paymentValue.text()) if newPayment['isIncome'] else -int(self.paymentValue.text())
			newPayment['type'] = self.paymentType.currentText()
			newPayment['date'] = str(self.paymentDate.date().toPyDate())
			newPayment['comment'] = str(self.paymentComment.text())
			self.payments.append({
				'price': newPayment['price'], 
				'isIncome': newPayment['isIncome'], 
				'type': newPayment['type'], 
				'comment': newPayment['comment'], 
				'date': newPayment['date']
			})
			self.updateTotal(newPayment['price'], newPayment['isIncome'])
			if self.paymentValidator(newPayment):
				self.db_controller.addPayment(newPayment)
				self.addPaymentInTable(0, newPayment)
				self.paymentValue.clear()
				self.paymentComment.clear()
	
	def paymentValidator(self, payment):
		if (not self.radioBtnIncome1.isChecked()) and (not self.radioBtnExpense1.isChecked()):
			self.errorMsg('Ошибка ввода', "Неверное значение")
			return False
		if payment['price'] == 0:
			self.errorMsg('Ошибка ввода', 'Неверное значение суммы')
			return False
		if date.fromisoformat(payment['date']) > date.today():
			self.errorMsg('Ошибка ввода', 'Неверное значение даты')
			return False
		if payment['type'] == '':
			self.errorMsg('Ошибка ввода', "Отсутствует поле 'тип'")
			return False
		return True

	def addType(self):
		if self.thereIsUser():
			name = self.typeName.text().lower()
			if (not self.radioBtnIncome2.isChecked()) and (not self.radioBtnExpense2.isChecked()):
				self.errorMsg("Ошибка ввода", "Не выбран доход | расход")
			elif name == "":
				self.errorMsg("Ошибка ввода", "Не заполнено поле названия")
			else:
				isIncome = True if self.radioBtnIncome2.isChecked() else False
				if isIncome == self.radioBtnIncome1.isChecked():
					self.paymentType.addItem(name)
				self.deleteTypes.addItem(name)
				self.db_controller.addType(name, isIncome)
				self.typeName.clear()
	
	def deleteType(self):
		if self.thereIsUser():
			msg = "Вы уверены, что хотите удалить эту категорию"
			result = QMessageBox.question(self, 'MessageBox', msg, QMessageBox.Yes | QMessageBox.No)
			if result == QMessageBox.Yes:
				name = self.deleteTypes.currentText()
				self.db_controller.deleteTypes(name)
				self.setTypes(self.radioBtnIncome1.isChecked())

	def errorMsg(self, title, error_msg):
		msg = QMessageBox()
		msg.setWindowTitle(title)
		msg.setText(error_msg)
		msg.setIcon(QMessageBox.Critical)
		msg.exec_()
	
	def askMsg(self, title, error_msg):
		msg = QMessageBox()
		msg.setWindowTitle(title)
		msg.setText(error_msg)
		msg.setIcon(QMessageBox.Warning)
		msg.exec_() 
	
	def showChart(self):
		chartType = self.chartsTypes.currentText()
		if chartType == "за год":
			MONTHS = ['январь','февраль','март','апрель','март','июнь','июль','август','сетябрь','октябрь','ноябрь','декабрь']
			incomes, expenses = self.utils.collectionMonthsData(self.payments)
			br = numpy.arange(len(MONTHS))
			chart = CreateChart()
			chart.addData(br, incomes, expenses)
			chart.addLabels("месяца", "доходы и расходы")
			chart.addXTicks(br, MONTHS)
		elif chartType == "за всё время":
			keys, incomes, expenses = self.utils.collectionYearsData(self.payments)
			br = numpy.arange(len(keys))
			chart = CreateChart()
			chart.addData(br, incomes, expenses)
			chart.addLabels("год", "доходы и расходы")
			chart.addXTicks(br, keys)
		else:
			chart = CreateChart()
			keys, incomes, expenses = self.utils.collectionMonthData(date.today().month, self.payments)
			br = numpy.arange(len(keys))
			chart.addData(br, incomes, expenses)
			chart.addLabels("дни", "доходы и расходы")
			chart.addXTicks(br, keys)
		chart.show()

	def exportPayments(self):
		with open('payments.csv', 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			payments = self.payments
			payments = sorted(payments, key=lambda x: x['date'])[::-1]
			for payment in payments:
				writer.writerow([payment['type'], payment['price'], payment['date'], payment['comment']])
	
	def importPayments(self):
		fname = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
		if str(fname[-3:]) == "csv":
			with open(fname, 'r') as csvfile:
				reader = csv.reader(csvfile, delimiter=';', quotechar='"')
				for row in reader:
					newPayment = {
						"isIncome": True if int(row[1]) > 0 else False,
						"price": int(row[1]),
						"type": row[0],
						"date": row[2],
						"comment": row[3]
					}
					if self.paymentValidator(newPayment):
						self.db_controller.addPayment(newPayment)
						self.addPaymentInTable(0, newPayment)
						self.paymentValue.clear()
						self.paymentComment.clear()
					self.updateTotal(newPayment['price'], newPayment['isIncome'])
			self.payments = self.db_controller.getPayments()
			self.updatePayments(self.payments)
		else:
			self.errorMsg("Неверный файл", "Дурочок, ты не тот файл открыл!")


class UserFormWindow(QMainWindow):
	def __init__(self, root):
		super().__init__(root)
		self.main = root
		uic.loadUi("UserForm.ui", self)
		self.btnAddUser.clicked.connect(self.addUser)

	def addUser(self):
		name = self.nameInput.text()
		login = self.loginInput.text()
		self.main.addUser(name, login)
		self.close()


class CreateChart():
	def __init__(self):
		plt.style.use("fivethirtyeight")

	def addData(self, br, data1, data2):
		plt.bar(br - 0.25, data1, width=0.25, color="#84ED2D", label="Доходы")
		plt.bar(br, data2, width=0.25, color="#F74056", label="Расходы")

	def addLabels(self, xlabel, ylabel):
		plt.legend()
		plt.gcf().autofmt_xdate()
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)

	def addXTicks(self, br, months):
		plt.xticks(ticks=br, labels=months)

	def show(self):
		plt.tight_layout()
		plt.show()


class Utils():
	def collectionMonthsData(self, payments):
		now_year = date.today().year
		incomes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		expenses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		for payment in payments:
			payment_date = date.fromisoformat(payment['date'])
			if payment_date.year == now_year:
				if payment['price'] > 0:
					incomes[payment_date.month - 1] += payment['price']
				else:
					expenses[payment_date.month - 1] += abs(payment['price'])
		return incomes, expenses

	def collectionYearsData(self, payments):
		payments = sorted(payments, key=lambda x: date.fromisoformat(x['date']))
		keys = []
		incomes = []
		expenses = []
		for payment in payments:
			payment_date = date.fromisoformat(payment['date'])
			if payment_date.year not in keys:
				keys.append(payment_date.year)
				incomes.append(0)
				expenses.append(0)
			index = keys.index(payment_date.year)
			if payment['price'] > 0:
				incomes[index] += payment['price']
			else:
				expenses[index] += abs(payment['price'])
		return keys, incomes, expenses

	def collectionMonthData(self, month, payments):
		payments = sorted(payments, key=lambda x: date.fromisoformat(x['date']))
		keys = []
		incomes = []
		expenses = []
		for payment in payments:
			payment_date = date.fromisoformat(payment['date'])
			if payment_date.day not in keys and payment_date.month == month:
				keys.append(payment_date.day)
				incomes.append(0)
				expenses.append(0)
			if payment_date.month == month:
				index = keys.index(payment_date.day)
				if payment['price'] > 0:
					incomes[index] += payment['price']
				else:
					expenses[index] += abs(payment['price'])
		return keys, incomes, expenses


class DB_Controller():
	def __init__(self):
		self.connection = sqlite3.connect("bookkeppingDB.db")
		self.cursor = self.connection.cursor()
		self.__createTables()
	
	def __createTables(self):
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
								"name"	TEXT,
								"login"	TEXT UNIQUE
							);""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS "payments" (
								"id"	INTEGER NOT NULL UNIQUE,
								"user"	INTEGER NOT NULL,
								"price"	INTEGER NOT NULL,
								"isIncome"	BLOB NOT NULL,
								"type"	INTEGER NOT NULL,
								"comment"	TEXT NOT NULL,
								"date"	TEXT NOT NULL,
								PRIMARY KEY("id" AUTOINCREMENT)
							);""")
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS "types" (
								"id"	INTEGER NOT NULL UNIQUE,
								"user"	TEXT NOT NULL,
								"name"	TEXT NOT NULL,
								"isIncome"	BLOB NOT NULL,
								PRIMARY KEY("id" AUTOINCREMENT)
							);""")
		self.connection.commit()

	def addUser(self, login, name):
		try:
			self.cursor.execute("INSERT INTO users(login, name) VALUES(?, ?)", (login, name, ))
			self.connection.commit()
		except sqlite3.IntegrityError:
			return "error"

	def setUser(self, login):
		self.login = login
	
	def getAllUsers(self):
		data = self.cursor.execute("""SELECT * from users""").fetchall()
		new_data = []
		for i in data:
			new_data.append([i[0], i[1]])
		return new_data

	def getUser(self):
		data = self.cursor.execute(f"SELECT DISTINCT * FROM users WHERE login=?", (self.login, )).fetchall()
		if len(data) == 0:
			return False
		return data[0]

	def getPayments(self):
		dbdata = self.cursor.execute("""SELECT id, price, isIncome, type, comment, date FROM payments WHERE user=?""", (self.login, )).fetchall()
		data = []
		for payment in dbdata:
			payment = list(payment)
			price = payment[1] if payment[2] else -payment[1]
			data.append({
				'id': payment[0], 
				'price': price, 
				'isIncome': payment[2], 
				'type': payment[3], 
				'comment': payment[4], 
				'date': payment[5]
			})
		return data

	def addPayment(self, payment):
		self.cursor.execute("""INSERT INTO payments(user, price, isIncome, type, comment, date) VALUES(?, ?, ?, ?, ?, ?)""", 
		(self.login, payment['price'], payment['isIncome'], payment['type'], payment['comment'], payment['date'],))
		self.connection.commit()
	
	def deletePayemnt(self, idPayment):
		self.cursor.execute("DELETE FROM payments WHERE id=?", (idPayment, ))
		self.connection.commit()

	def addType(self, name, isIncome):
		self.cursor.execute("""INSERT INTO types(user, isIncome, name) VALUES(?, ?, ?)""", (self.login, isIncome, name, ))
		self.connection.commit()

	def getTypes(self):
		incomes = self.cursor.execute("SELECT name FROM types WHERE user=? AND isIncome=1", (self.login, )).fetchall()
		expenses = self.cursor.execute("SELECT name FROM types WHERE user=? AND isIncome=0", (self.login, )).fetchall()
		return {"incomeTypes": incomes, "expenseTypes": expenses}

	def deleteTypes(self, name):
		self.cursor.execute("""DELETE FROM types WHERE name=?""", (name, ))
		self.connection.commit()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	bookkepping = Bookkepping()
	bookkepping.show()
	sys.exit(app.exec())