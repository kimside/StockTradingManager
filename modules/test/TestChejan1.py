import sys, os, pprint;

from PyQt5               import uic, QtWidgets, QtCore, QtGui;

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class TestChejan1(QtWidgets.QDialog, uic.loadUiType(resource_path("modules/test/TestChejan1.ui"))[0]):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self);
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint);
        self.parent = parent;

        self.btnSend.clicked.connect(self.sendSlot);
        self.btnCancel.clicked.connect(self.close);
        self.f946.addItem("매수", "2");
        self.f946.addItem("매도", "1");
    def sendSlot(self):
        obj = {
            "gubun": "1",
            "f9001": self.f9001.text(),
            "f302" : self.f302.text(),
            "f10"  : self.f10.text(),
            "f930" : self.f930.text(),
            "f931" : self.f931.text(),
            "f933" : self.f933.text(),
            "f946" : self.f946.currentData(),
            "f307" : self.f307.text(),
            "f990" : self.f990.text(),
            "f991" : self.f991.text(),
        };
    
        print(obj);
        self.parent.addChejanSlot(obj);
    
    #모달창 Show 이벤트
    def showEvent(self, event):
        pass;