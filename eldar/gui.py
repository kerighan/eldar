
from PyQt6 import QtGui
from PyQt6.QtWidgets import (QAbstractScrollArea, QApplication, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QPushButton,
                             QSizePolicy, QSpacerItem, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)


class SearchWidget(QWidget):
    def __init__(self, search):
        super().__init__()

        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(search)
        self.search_button.setFixedHeight(40)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.search_input)
        self.hbox.addWidget(self.search_button)
        self.setLayout(self.hbox)


class Results(QWidget):
    def __init__(self):
        super().__init__()
        self.hbox = QVBoxLayout()

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        # self.tableWidget.setItem(0, 0, QTableWidgetItem(
        #     "Test " * 60))
        self.tableWidget.setRowCount(0)
        header = self.tableWidget.horizontalHeader()
        header.hide()
        header.setStretchLastSection(True)
        # header.setResizeMode(0, QtGui.QHeaderView.Stretch)

        self.counter = QLabel("0 result")
        self.hbox.addWidget(self.counter)
        self.hbox.addWidget(self.tableWidget)

        self.tableWidget.resizeColumnsToContents()
        self.setLayout(self.hbox)

    def update(self, data):
        count = len(data)
        self.counter.setText(f"{count} results")

        self.tableWidget.setRowCount(count)
        for i, val in enumerate(data):
            self.tableWidget.setItem(i, 0,
                                     QTableWidgetItem(val))

        self.tableWidget.resizeColumnsToContents()


class Window(QWidget):
    def __init__(self, index):
        super().__init__()

        self.index = index
        self.setGeometry(200, 200, 800, 800)
        layout = QVBoxLayout()

        self.search_widget = SearchWidget(self.search)
        self.results_widget = Results()

        layout.addWidget(self.search_widget)
        layout.addWidget(self.results_widget)
        self.setLayout(layout)

    def search(self):
        query = self.search_widget.search_input.text()
        data = self.index.search(query)
        self.results_widget.update(data)


def create_app(index):
    app = QApplication([])
    window = Window(index)
    window.show()
    app.exec()
