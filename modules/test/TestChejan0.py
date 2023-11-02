import sys, os, pprint;

from PyQt5               import uic, QtWidgets, QtCore, QtGui;

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class TestChejan0(QtWidgets.QDialog, uic.loadUiType(resource_path("modules/test/TestChejan0.ui"))[0]):

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self);
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint);
        self.parent = parent;

        self.btnSend.clicked.connect(self.sendSlot);
        self.btnCancel.clicked.connect(self.close);
    
    def sendSlot(self):
        obj = {
            "gubun": "0"                    , #체잔구분
            "f9203": self.f9203.text()      , #주문번호
            "f9001": self.f9001.text()      , #종목코드,업종코드
            "f913" : self.f913.currentText(), #주문상태(접수,확인,체결)
            "f302" : self.f302.text()       , #종목명
            "f900" : self.f900.text()       , #주문수량
            "f901" : self.f901.text()       , #주문가격
            "f902" : self.f902.text()       , #미체결수량
            "f903" : self.f903.text()       , #체결누계금액
            "f904" : self.f904.text()       , #원주문번호
            "f905" : self.f905.currentText(), #주문구분(+매수,-매도,매수취소,매도취소,매수정정,매도정정)
            "f906" : self.f906.text()       , #매매구분
            "f908" : self.f908.text()       , #주문/체결시간
            "f909" : self.f909.text()       , #체결번호
            "f910" : self.f910.text()       , #체결가
            "f911" : self.f911.text()       , #체결량
            "f10"  : self.f10.text()        , #현재가
            "f914" : self.f914.text()       , #단위체결가
            "f915" : self.f915.text()       , #단위체결량
            "f919" : self.f919.text()       , #거부사유
            "f920" : self.f920.text()       , #화면번호
        };

        self.parent.addChejanSlot(obj);
    
    #모달창 Show 이벤트
    def showEvent(self, event):
        pass;