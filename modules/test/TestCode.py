import sys, os, random, datetime, time;

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
        self.btnStressStart.clicked.connect(self.stressStart);
        self.btnStressStop.clicked.connect(self.stressStop);
        self.btnClose.clicked.connect(self.close);

        self.btnStressStart.setEnabled(True);
        self.btnStressStop.setEnabled(False);
        
    def btnRunSlot(self):
        try:
            output = eval(self.input.toPlainText());
            self.output.clear();
            self.output.setPlainText("{0}".format(output));
        except Exception as e:
            self.output.setPlainText("{0}".format(e));
    
    def stressStart(self):
        stocks = set([]);
        for myStock in self.parent.twMyStocks.getRowDatas():
            stocks.add((myStock["stockCode"], myStock["stockName"]));
        
        self.parent.myThread.stocks = stocks;
        self.parent.myThread.sleepTime = self.sleepTime.value();
        self.parent.myThread.isRun = True;
        
        self.btnStressStart.setEnabled(False);
        self.btnStressStop.setEnabled(True);
    
    def stressStop(self):
        self.parent.myThread.isRun = False;
        self.btnStressStart.setEnabled(True);
        self.btnStressStop.setEnabled(False);
        
    #모달창 Show 이벤트
    def showEvent(self, event):
        pass;

class MyThread(QtCore.QThread):
    tSignal = QtCore.pyqtSignal(object);
    
    def __init__(self, parent):
        super().__init__();
        self.parent = parent;
        self.isRun = False;
        self.sleepTime = 0.003;
        self.stocks = set([]);
        
    def run(self):
        while True:
            while self.isRun:
                #newPrice = random.randrange(1000,10000);
                #stockLength = random.randrange(0, len(self.stocks) -1);

                obj = {
                    "sRealType": "주식체결",
                    #"f9001": list(self.stocks)[stockLength][0],
                    #"f302" : list(self.stocks)[stockLength][1],
                    "f9001": "123456",
                    "f302" : "테스트",
                    "f307" : "10000",
                    "f920" : "4000;7000;8000",
                    #"f920" : "4000",
                    "f20" : "083739",
                    "f10" : "10000",
                    "f11" : "+400",
                    "f12" : "+2.21",
                    "f27" : "-0",
                    "f28" : "-0",
                    "f15" : "+250",
                    "f13" : "905",
                    "f14" : "53",
                    "f16" : "+4870",
                    "f17" : "+4870",
                    "f18" : "+4870",
                    "f25" : "2",
                    "f26" : "-1514234",
                    "f29" : "-7225224200",
                    "f30" : "-2.00",
                    "f31" : "0.04",
                    "f32" : "5",
                    "f228": "101.90",
                    "f311": "791",
                    "f290": "2",
                    "f691": "0",
                    "f567": "000000",
                    "f568": "000000",
                    "f851": "6477",
                };

                time.sleep(self.sleepTime);
                self.tSignal.emit(obj);
            time.sleep(0.0001);
    def stop(self):
        self.isRun = False;