import sys
from datetime import date, datetime
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QDate


class Bookkepping(QMainWindow):
	def __init__(self):
		super().__init__()
		self.db_controller = DB_Controller('lrd_yandex')
		uic.loadUi("MainWindow.ui", self)
		self.nowDate = date.today()

		self.paymentDate.setMaximumDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.paymentDate.setDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.btnAddData.clicked.connect(self.addData)
		self.btnAddType.clicked.connect(self.addType)
		self.btnDeletePayment.clicked.connect(self.deletePayment)
		self.radioBtnIncome1.toggled.connect(self.changePaymentTypes)
		self.radioBtnExpense1.toggled.connect(self.changePaymentTypes)
		self.sortBy.currentIndexChanged.connect(self.sortPaymnets)

		self.user_data = self.db_controller.getUser()
		self.payments = []
		self.total = 0
		self.setPayments()
		self.setTypes()

	def setPayments(self):
		new_payments = self.db_controller.getPayments()
		for index, payment in enumerate(new_payments[::-1]):
			payment = list(payment)
			self.tablePayments.insertRow(index)
			if payment[2]:
				self.tablePayments.setItem(index, 0, QTableWidgetItem(f"+{str(payment[1])}"))
				self.total += payment[1]
			else:
				self.tablePayments.setItem(index, 0, QTableWidgetItem(f"-{str(payment[1])}"))
				self.total -= payment[1]
			self.tablePayments.setItem(index, 1, QTableWidgetItem(payment[3]))
			self.tablePayments.setItem(index, 2, QTableWidgetItem(payment[4]))
			self.tablePayments.setItem(index, 3, QTableWidgetItem(payment[5]))
			self.payments.append({'id': payment[0], 'price': payment[1], 'isIncome': payment[2], 'type': payment[3], 'comment': payment[4], 'date': payment[5]})
		self.labelTotal.setText(f"Капитал: {self.total}$")

	def updatePayments(self):
		for _ in range(self.tablePayments.rowCount()):
			self.tablePayments.removeRow(0)
		for index, payment in enumerate(self.payments):
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
		for name in types[key]:
			self.paymentType.addItem(name[0]) 

	def deletePayment(self):
		index = self.indexPayment.value()
		payment = self.payments[index]
		self.tablePayments.removeRow(index)
		self.db_controller.deletePayemnt(payment['id'])

	def changePaymentTypes(self):
		if self.radioBtnIncome1.isChecked():
			self.setTypes(True)
		elif self.radioBtnExpense1.isChecked():
			self.setTypes(False)

	def updateTotal(self, isIncome, price):
		if isIncome:
			self.total += price
		else:
			self.total -= price
		self.labelTotal.setText(f"Капитал: {self.total}$")

	def sortPaymnets(self):
		sortby = self.sortBy.currentText()
		if sortby == "дате":
			self.payments = sorted(self.payments, key=lambda x: x['date'])
		elif sortby == 'сумме':
			self.payments = sorted(self.payments, key=lambda x: x['price'])
		elif sortby == 'категории':
			self.payments = sorted(self.payments, key=lambda x: x['type'])
		self.updatePayments()

	def addData(self):
		newPayment = {}
		newPayment['price'] = int(self.paymentValue.text())
		newPayment['isIncome'] = self.radioBtnIncome1.isChecked()
		newPayment['type'] = self.paymentType.currentText()
		newPayment['date'] = str(self.paymentDate.date().toPyDate())
		newPayment['comment'] = str(self.paymentComment.text())
		self.payments.append({'price': newPayment['price'], 'type': newPayment['type'], 'comment': newPayment['comment'], 'date': newPayment['date']})
		self.updateTotal(newPayment['isIncome'], newPayment['price'])
		if self.paymentValidator(newPayment):
			self.db_controller.addPayment(newPayment)
			self.tablePayments.insertRow(0)
			if newPayment['isIncome']:
				self.tablePayments.setItem(0, 0, QTableWidgetItem(f"+{str(newPayment['price'])}"))
			else:
				self.tablePayments.setItem(0, 0, QTableWidgetItem(f"-{str(newPayment['price'])}"))
			self.tablePayments.setItem(0, 1, QTableWidgetItem(newPayment['type']))
			self.tablePayments.setItem(0, 2, QTableWidgetItem(newPayment['comment']))
			self.tablePayments.setItem(0, 3, QTableWidgetItem(newPayment['date']))
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
		if self.paymentType.currentText() == '':
			self.errorMsg('Ошибка ввода', "Отсутствует поле 'тип'")
			return False
		return True

	def addType(self):
		self.paymentType.addItem(self.typeName.text())
		self.db_controller.addType(self.typeName.text(), True)
		self.typeName.clear()

	def errorMsg(self, title, error_msg):
		msg = QMessageBox()
		msg.setWindowTitle(title)
		msg.setText(error_msg)
		msg.setIcon(QMessageBox.Warning)
		msg.exec_()


class DB_Controller():
	def __init__(self, login):
		self.connection = sqlite3.connect("bookkeppingDB.db")
		self.login = login
		self.cursor = self.connection.cursor()
		#self._addUser()

	def _addUser(self):
		self.cursor.execute("""INSERT INTO users(login, name) VALUES("lrd_yandex", "Родион")""")
		self.connection.commit()

	def getUser(self):
		data = self.cursor.execute(f"SELECT DISTINCT * FROM users WHERE login=?", (self.login, )).fetchall()
		return data[0]
	
	def getTypes(self):
		incomes = self.cursor.execute("""SELECT name FROM types WHERE isIncome=1""").fetchall()
		expenses = self.cursor.execute("""SELECT name FROM types WHERE isIncome=0""").fetchall()
		return {"incomeTypes": incomes, "expenseTypes": expenses}

	def getPayments(self):
		data = self.cursor.execute("""SELECT id, price, isIncome, type, comment, date FROM payments WHERE user=?""", (self.login, )).fetchall()
		return data

	def addPayment(self, payment):
		self.cursor.execute("""INSERT INTO payments(user, price, isIncome, type, comment, date) VALUES(?, ?, ?, ?, ?, ?)""", 
		(self.login, payment['price'], payment['isIncome'], payment['type'], payment['comment'], payment['date'],))
		self.connection.commit()
	
	def deletePayemnt(self, idPayment):
		self.cursor.execute("DELETE FROM payments WHERE id=?", (idPayment, ))
		self.connection.commit()

	def addType(self, name, isIncome):
		self.cursor.execute("""INSERT INTO types(isIncome, name) VALUES(?, ?)""", (isIncome, name, ))
		self.connection.commit()


if __name__ == "__main__":
	app = QApplication(sys.argv)
	bookkepping = Bookkepping()
	bookkepping.show()
	sys.exit(app.exec())