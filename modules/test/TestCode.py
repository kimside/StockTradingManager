import sys, os, pprint;

from PyQt5 import uic, QtWidgets, QtCore, QtGui;

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class TestCode(QtWidgets.QDialog, uic.loadUiType(resource_path("modules/test/TestCode.ui"))[0]):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self);
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint);
        self.parent = parent;

        self.btnRun.clicked.connect(self.btnRunSlot);
        self.btnClose.clicked.connect(self.close);
        
    def btnRunSlot(self):
        try:
            output = eval(self.input.toPlainText());
            self.output.clear();
            self.output.setPlainText("{0}".format(output));
        except Exception as e:
            self.output.setPlainText("{0}".format(e));
    
    #모달창 Show 이벤트
    def showEvent(self, event):
        pass;