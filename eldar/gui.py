
from PyQt6.QtWidgets import (QAbstractScrollArea, QApplication, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QPushButton,
                             QSizePolicy, QSpacerItem, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.hbox = QHBoxLayout()
        # self.hbox.addWidget(QLabel())
        self.hbox.addWidget(QLineEdit())
        self.hbox.addWidget(QPushButton("Search"))
        self.setLayout(self.hbox)


class Results(QWidget):
    def __init__(self):
        super().__init__()
        self.hbox = QVBoxLayout()

        self.tableWidget = QTableWidget()

        self.tableWidget.setRowCount(50)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setItem(0, 0, QTableWidgetItem(
            "Test"))

        self.hbox.addWidget(QLabel("125 results"))
        self.hbox.addWidget(self.tableWidget)

        # self.tableWidget.setSizeAdjustPolicy(
        #     QAbstractScrollArea.AdjustToContents)
        self.tableWidget.addStretch()
        self.tableWidget.resizeColumnsToContents()

        self.setLayout(self.hbox)


def create_app(index):

    app = QApplication([])

    window = QWidget()
    window.setGeometry(200, 200, 800, 800)

    layout = QVBoxLayout()
    # spacer = QSpacerItem(1, 10)

    layout.addWidget(SearchWidget())
    layout.addWidget(Results())
    window.setLayout(layout)

    window.show()
    app.exec()
