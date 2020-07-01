from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,QPixmap, QRadialGradient)
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QGroupBox, QComboBox, QDateEdit, QLineEdit, QTabWidget, QSpinBox, QVBoxLayout
from MainWindow import Ui_Form


class MainLogic(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.StartCapital = 0 # стартовый капитал
        self.NowCapital = 0 # капитал сейчас
        self.Expenses = [] # все расходы их виды, даты и т.д.
        self.totalExpenses = 0 # сумарный расход
        self.Income = [] # все доходы их виды, даты и т.д.
        self.totalIncome = 0 # сумарнный доход
        self.percentCapital = 0

        self.setupUi(self)
        self.DataCollection() # сбор данных из файлов и бызы данных
        self.FillTable()

        # Шапки таблиц
        self.tableExpenses.setItem(0,0, QTableWidgetItem("Сумма"))
        self.tableExpenses.setItem(0,1, QTableWidgetItem("Продукт"))
        self.tableExpenses.setItem(0,2, QTableWidgetItem("Дата"))
        self.tableExpenses.setItem(0,3, QTableWidgetItem("Тип"))

        self.tableIncome.setItem(0,0, QTableWidgetItem("Сумма"))
        self.tableIncome.setItem(0,1, QTableWidgetItem("Продукт"))
        self.tableIncome.setItem(0,2, QTableWidgetItem("Дата"))
        self.tableIncome.setItem(0,3, QTableWidgetItem("Тип"))

        # команды для кнопок
        self.Add.clicked.connect(self.AddExpensesIncome)
        self.MainTab.currentChanged.connect(self.ChangeTab)
        self.chartBtn.clicked.connect(self.Charts)
        self.DeletBtn.clicked.connect(self.DeleteExpensesIncome)

    def DataCollection(self): # сбор данных из файлов и бызы данных
        data = DB.SelectData(bd_i=0)
        if len(data) != 0:
            for item in data:
                items = {}
                items['price'] = int(item[2])
                items['product'] = item[3]
                items['date'] = datetime.strptime(item[4], '%Y-%m-%d').date()
                items['type'] = item[5]
                self.Expenses.append(items)

        data = DB.SelectData(bd_i=1)
        if len(data) != 0:
            for item in data:
                items = {}
                items['price'] = int(item[2])
                items['product'] = item[3]
                items['date'] = datetime.strptime(item[4], '%Y-%m-%d').date()
                items['type'] = item[5]
                self.Income.append(items)

        file = open('inform/TotalExpenses.txt')
        self.totalExpenses = int(file.readline())
        file.close()

        file = open('inform/TotalIncome.txt')
        self.totalIncome = int(file.readline())
        file.close()

        file = open('inform/StartCapital.txt')
        self.StartCapital = int(file.readline())
        self.NowCapital = self.StartCapital - self.totalExpenses + self.totalIncome
        file.close()

        self.percentCapital = round((self.NowCapital * 100 / self.StartCapital - 100), 2)
        if self.percentCapital < 0:
            self.percentCapital = str(self.percentCapital) + "%"
            self.percentTotalLabel.setStyleSheet(u"font-size: 39px;\n""color: red;")
        else:
            self.percentCapital = "+" + str(self.percentCapital) + "%"
            self.percentTotalLabel.setStyleSheet(u"font-size: 39px;\n""color: green;")


    def FillTable(self):
        self.TotalLabel.setText("Итоговй расход: "+str(self.totalExpenses))
        self.TotalLabel_2.setText("Итог:  "+str(self.NowCapital))
        self.percentTotalLabel.setText(str(self.percentCapital))

        for i in range(len(self.Expenses)):
            price = str(self.Expenses[i]['price'])
            self.tableExpenses.setItem(i+1, 0, QTableWidgetItem(price))
            self.tableExpenses.setItem(i+1, 1, QTableWidgetItem(self.Expenses[i]['product']))
            self.tableExpenses.setItem(i+1, 2, QTableWidgetItem(str(self.Expenses[i]['date'])))
            self.tableExpenses.setItem(i+1, 3, QTableWidgetItem(self.Expenses[i]['type']))

        for i in range(len(self.Income)):
            price = str(self.Income[i]['price'])
            self.tableIncome.setItem(i+1, 0, QTableWidgetItem(price))
            self.tableIncome.setItem(i+1, 1, QTableWidgetItem(self.Income[i]['product']))
            self.tableIncome.setItem(i+1, 2, QTableWidgetItem(str(self.Income[i]['date'])))
            self.tableIncome.setItem(i+1, 3, QTableWidgetItem(self.Income[i]['type']))

    def AddExpensesIncome(self):
        if self.MainTab.currentIndex() == 0:
            price = self.PriceEntery.text()
            if price.isdigit():
                date = self.ConvertQdateToDatetime(self.DateEntery.date())
                self.totalExpenses += int(price)
                self.NowCapital -= int(price)

                self.TotalLabel.setText("Итоговый расход: " + str(self.totalExpenses))
                self.TotalLabel_2.setText("Итог: " + str(self.NowCapital))

                self.tableExpenses.setItem((len(self.Expenses)+1), 0, QTableWidgetItem(price))
                self.tableExpenses.setItem((len(self.Expenses)+1), 1, QTableWidgetItem(self.ProductEntery.text()))
                self.tableExpenses.setItem((len(self.Expenses)+1), 2, QTableWidgetItem(str(date)))
                self.tableExpenses.setItem((len(self.Expenses)+1), 3, QTableWidgetItem(self.TypeEntery.currentText()))

                items = {}
                items['price'] = int(price)
                items['product'] = self.ProductEntery.text()
                items['date'] = date
                items['type'] = self.TypeEntery.currentText()
                self.Expenses.append(items)

                DB.AddData(self.Expenses[-1], len(self.Expenses), 0)

                file = open('inform/TotalExpenses.txt','w')
                file.write(str(self.totalExpenses))
                file.close()
        else:
            price = self.PriceEntery.text()
            if price.isdigit():
                date = self.ConvertQdateToDatetime(self.DateEntery.date())
                self.totalIncome += int(price)
                self.NowCapital += int(price)

                self.TotalLabel.setText("Итоговый доход: " + str(self.totalIncome))
                self.TotalLabel_2.setText("Итог: " + str(self.NowCapital))

                self.tableIncome.setItem((len(self.Income)+1), 0, QTableWidgetItem(price))
                self.tableIncome.setItem((len(self.Income)+1), 1, QTableWidgetItem(self.ProductEntery.text()))
                self.tableIncome.setItem((len(self.Income)+1), 2, QTableWidgetItem(str(date)))
                self.tableIncome.setItem((len(self.Income)+1), 3, QTableWidgetItem(self.TypeEntery.currentText()))

                items = {}
                items['price'] = price
                items['product'] = self.ProductEntery.text()
                items['date'] = date
                items['type'] = self.TypeEntery.currentText()
                self.Income.append(items)

                DB.AddData(self.Income[-1], len(self.Income), 1)

                file = open('inform/TotalIncome.txt','w')
                file.write(str(self.totalIncome))
                file.close()

        self.percentCapital = round((self.NowCapital * 100 / self.StartCapital - 100), 2)
        if self.percentCapital < 0:
            self.percentCapital = str(self.percentCapital) + "%"
            self.percentTotalLabel.setStyleSheet(u"font-size: 39px;\n""color: red;")
        else:
            self.percentCapital = "+" + str(self.percentCapital) + "%"
            self.percentTotalLabel.setStyleSheet(u"font-size: 39px;\n""color: green;")
        self.percentTotalLabel.setText(str(self.percentCapital))



    def DeleteExpensesIncome(self):
        if self.MainTab.currentIndex() == 0:
            self.tableExpenses.removeRow(self.RowDelet.value()-1)
            self.totalExpenses -= self.Expenses[self.RowDelet.value()-2]['price']
            self.NowCapital += self.Expenses[self.RowDelet.value()-2]['price']
            self.TotalLabel.setText("Итоговый расход: " + str(self.totalExpenses))
            self.TotalLabel_2.setText("Итог: " + str(self.NowCapital))

            DB.DeleteData(self.RowDelet.value()-1, 0)

            file = open('inform/TotalExpenses.txt', 'w')
            file.write(str(self.totalExpenses))
            file.close()

            informDelet = self.ConvertInformToString(self.Expenses[self.RowDelet.value()-2])
            self.Expenses.pop(self.RowDelet.value()-2)
        else:
            self.tableExpenses.removeRow(self.RowDelet.value()-1)
            self.totalExpenses -= self.Income[self.RowDelet.value()-2]['price']
            self.NowCapital -= self.Income[self.RowDelet.value()-2]['price']
            self.TotalLabel.setText("Итоговый доходов: "+str(self.totalIncome))
            self.TotalLabel_2.setText("Итог: " + str(self.NowCapital))

            DB.DeleteData(self.RowDelet.value()-1, 1)

            file = open('inform/TotalIncome.txt', 'w')
            file.write(str(self.totalIncome))
            file.close()

            informDelet = self.ConvertInformToString(self.Income[self.RowDelet.value()-2])
            self.Income.pop(self.RowDelet.value()-2)


    def Charts(self):
        price = []
        product = []
        date = []
        types = []
        if self.MainTab.currentIndex() == 0:
            for item in self.Expenses:
                price.append(item['price'])
                if self.TypesCharts.currentText() == "по времени":
                    date.append(item['date'])
                elif self.TypesCharts.currentText() == "по типам":
                    types.append(item['type'])
                else:
                    product.append(item['product'])

            if self.TypesCharts.currentText() == "по времени":
                plt.style.use("seaborn")
                plt.plot_date(date, price, linestyle='solid')
                plt.gcf().autofmt_xdate()
                plt.xlabel("Дата")
                plt.ylabel("Расходы")
                plt.show()
            elif self.TypesCharts.currentText() == "по типам":
                plt.style.use("fivethirtyeight")
                plt.bar(types, price)
                plt.xlabel("Типы расходов")
                plt.ylabel("Расходы")
                plt.tight_layout()
                plt.show()
            elif self.TypesCharts.currentText() == "по продуктам":
                plt.style.use("fivethirtyeight")
                plt.bar(product, price)
                plt.xlabel("продукты")
                plt.ylabel("Расходы")
                plt.tight_layout()
                plt.show()
        else:
            for item in self.Income:
                price.append(item['price'])
                if self.TypesCharts.currentText() == "по времени":
                    date.append(item['date'])
                elif self.TypesCharts.currentText() == "по типам":
                    types.append(item['type'])
                else:
                    product.append(item['product'])

            if self.TypesCharts.currentText() == "по времени":
                plt.style.use("seaborn")
                plt.plot_date(date, price, linestyle='solid')
                plt.gcf().autofmt_xdate()
                plt.xlabel("Дата")
                plt.ylabel("Доход")
                plt.show()
            elif self.TypesCharts.currentText() == "по типам":
                plt.style.use("fivethirtyeight")
                plt.bar(types, price)
                plt.xlabel("Типы расходов")
                plt.ylabel("Доход")
                plt.tight_layout()
                plt.show()
            elif self.TypesCharts.currentText() == "по продуктам":
                plt.style.use("fivethirtyeight")
                plt.bar(product, price)
                plt.xlabel("продукты")
                plt.ylabel("Доход")
                plt.tight_layout()
                plt.show()
        if self.TypesCharts.currentText() == "общая":
            months = ['январь','февраль','март','апрель','март','июнь','июль','август','сетябрь','октябрь','ноябрь','декабрь']
            months_y = np.arange(len(months))
            MonthsExpeneses = self.CollectionMonthsData(self.Expenses)
            MonthsIncome = self.CollectionMonthsData(self.Income)

            plt.style.use("fivethirtyeight")
            plt.bar(months_y - 0.25, MonthsExpeneses, width=0.25, color="#F74056", label="Расходы")
            plt.bar(months_y, MonthsIncome, width=0.25, color="#84ED2D", label="Доходы")
            plt.legend()
            plt.gcf().autofmt_xdate()
            plt.xticks(ticks=months_y, labels=months)
            plt.xlabel("месяца")
            plt.ylabel("доходы и расходы")
            plt.tight_layout()
            plt.show()



    def ChangeTab(self):
        if self.MainTab.currentIndex() == 0:
            self.TypeEntery.clear()
            self.TypeEntery.addItem("продукты")
            self.TypeEntery.addItem("транспорт")
            self.TypeEntery.addItem("развлечения")
            self.TypeEntery.addItem("техника")
            self.TypeEntery.addItem("одежда")
            self.TypeEntery.addItem("учёба")
            self.TypeEntery.addItem("книги")
            self.TypeEntery.addItem("другое")
            self.TotalLabel.setText("Итоговый расход: "+str(self.totalExpenses))
            self.groupBox.setTitle("Добавить Расход")
            self.groupBoxType.setTitle("Удалить Расход")
        else:
            self.TypeEntery.clear()
            self.TypeEntery.addItem("работа")
            self.TypeEntery.addItem("проценты")
            self.TypeEntery.addItem("кэшбэки")
            self.TypeEntery.addItem("папа и мама")
            self.TypeEntery.addItem("бабушка")
            self.TypeEntery.addItem("давяни")
            self.TotalLabel.setText("Итоговый доход: "+str(self.totalIncome))
            self.groupBox.setTitle("Добавить Доход")
            self.groupBoxType.setTitle("Удалить Доход")


    def ConvertQdateToDatetime(self, QdateArg):
        date_input = str(QdateArg)
        date_input = date_input[19:-1].split(',')
        year = date_input[0]
        mouth = date_input[1][1:]
        day = date_input[2][1:]
        date_row = date(int(year), int(mouth), int(day))
        return date_row


    def ConvertInformToString(self, informArg):
        informStr = str(informArg['price']) + "." + informArg['product'] + "." + str(informArg['date']) + "." + informArg['type']
        return informStr

    def CollectionMonthsData(self,data):
        now_year = datetime.now().year
        prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for item in data:
            if item['date'].year == now_year:
                prices[item['date'].month-1] += int(item['price'])
        return prices


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainLogic()
    window.show()
    sys.exit(app.exec_())