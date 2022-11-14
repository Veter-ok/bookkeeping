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
		self.db_controller = DB_Controller('lrd_yandex')
		uic.loadUi("MainWindow.ui", self)
		self.nowDate = date.today()

		self.paymentDate.setMaximumDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.paymentDate.setDate(QDate(self.nowDate.year, self.nowDate.month, self.nowDate.day))
		self.btnImportPayments.clicked.connect(self.importPayments)
		self.btnExportPayments.clicked.connect(self.exportPayments)
		self.btnChart.clicked.connect(self.showChart)
		self.btnAddData.clicked.connect(self.addData)
		self.btnAddType.clicked.connect(self.addType)
		self.btnDeletePayment.clicked.connect(self.deletePayment)
		self.radioBtnIncome1.toggled.connect(self.changePaymentTypes)
		self.radioBtnExpense1.toggled.connect(self.changePaymentTypes)
		self.sortBy.currentIndexChanged.connect(self.sortPaymnets)
		self.radioBtnIncome1.setChecked(True)

		self.user_data = self.db_controller.getUser()
		self.payments = []
		self.total = 0
		self.setPayments()
		self.setTypes()

	def setPayments(self):
		new_payments = self.db_controller.getPayments()
		for index, payment in enumerate(new_payments):
			self.addPaymentInTable(index, payment)
			self.updateTotal(payment['price'])
			self.payments.append(payment)
		self.labelTotal.setText(f"Капитал: {self.total}$")

	def updatePayments(self, payments):
		for _ in range(self.tablePayments.rowCount()):
			self.tablePayments.removeRow(0)
		for index, payment in enumerate(payments):
			self.addPaymentInTable(index, payment)
	
	def addPaymentInTable(self, index, payment):
		self.tablePayments.insertRow(index)
		if payment['isIncome']:
			self.tablePayments.setItem(index, 0, QTableWidgetItem(f"+{str(payment['price'])}"))
		else:
			self.tablePayments.setItem(index, 0, QTableWidgetItem(str(payment['price'])))
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

	def updateTotal(self, price):
		self.total += price
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
		newPayment = {}
		newPayment['isIncome'] = self.radioBtnIncome1.isChecked()
		newPayment['price'] = int(self.paymentValue.text()) if newPayment['isIncome'] else -int(self.paymentValue.text())
		newPayment['type'] = self.paymentType.currentText()
		newPayment['date'] = str(self.paymentDate.date().toPyDate())
		newPayment['comment'] = str(self.paymentComment.text())
		self.payments.append({'price': newPayment['price'], 'isIncome': newPayment['isIncome'], 'type': newPayment['type'], 'comment': newPayment['comment'], 'date': newPayment['date']})
		self.updateTotal(newPayment['price'])
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
		name = self.typeName.text().lower()
		isIncome = True if self.radioBtnIncome2.isChecked() else False
		if isIncome == self.radioBtnIncome1.isChecked():
			self.paymentType.addItem(name)
		self.db_controller.addType(name, isIncome)
		self.typeName.clear()

	def errorMsg(self, title, error_msg):
		msg = QMessageBox()
		msg.setWindowTitle(title)
		msg.setText(error_msg)
		msg.setIcon(QMessageBox.Warning)
		msg.exec_()
	
	def showChart(self):
		months = ['январь','февраль','март','апрель','март','июнь','июль','август','сетябрь','октябрь','ноябрь','декабрь']
		incomes, expenses = self.collectionMonthsData()
		plt.style.use("fivethirtyeight")
		br = numpy.arange(len(months))
		plt.bar(br - 0.25, incomes, width=0.25, color="#84ED2D", label="Доходы")
		plt.bar(br, expenses, width=0.25, color="#F74056", label="Расходы")
		plt.legend()
		plt.gcf().autofmt_xdate()
		plt.xlabel("месяца")
		plt.ylabel("доходы и расходы")
		plt.xticks(ticks=br, labels=months)
		plt.tight_layout()
		plt.show()

	def collectionMonthsData(self):
		now_year = date.today().year
		incomes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		expenses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		for payment in self.payments:
			payment_data = date.fromisoformat(payment['date'])
			if payment_data.year == now_year:
				if payment['price'] > 0:
					incomes[payment_data.month - 1] += payment['price']
				else:
					expenses[payment_data.month - 1] += abs(payment['price'])
		return incomes, expenses

	def exportPayments(self):
		with open('payments.csv', 'w') as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			payments = self.payments
			payments = sorted(payments, key=lambda x: x['date'])[::-1]
			for payment in payments:
				writer.writerow([payment['type'], payment['price'], payment['date'], payment['comment']])
	
	def importPayments(self):
		fname = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
		with open(fname, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=';', quotechar='"')
			for index, row in enumerate(reader):
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
				self.updateTotal(newPayment['price'])
		self.payments = self.db_controller.getPayments()
		self.updatePayments(self.payments)


class DB_Controller():
	def __init__(self, login):
		self.connection = sqlite3.connect("bookkeppingDB.db")
		self.login = login
		self.cursor = self.connection.cursor()

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
		dbdata = self.cursor.execute("""SELECT id, price, isIncome, type, comment, date FROM payments WHERE user=?""", (self.login, )).fetchall()
		data = []
		for payment in dbdata:
			payment = list(payment)
			price = payment[1] if payment[2] else -payment[1]
			data.append({'id': payment[0], 'price': price, 'isIncome': payment[2], 'type': payment[3], 'comment': payment[4], 'date': payment[5]})
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