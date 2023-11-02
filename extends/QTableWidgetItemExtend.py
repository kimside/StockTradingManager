from PyQt5 import QtWidgets, QtCore, QtGui;

class QTableWidgetItemExtend(QtWidgets.QTableWidgetItem):
    def __lt__(self, other):
        return (self.data(QtCore.Qt.UserRole) < other.data(QtCore.Qt.UserRole))