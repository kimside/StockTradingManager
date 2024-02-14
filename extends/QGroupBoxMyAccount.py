import sys, os;

from PyQt5 import uic, QtWidgets, QtCore, QtGui;

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

#Grid에서 선택된 Row에 배경,텍스트 색 지정
#(Draw시에 처리하는 함수라.. 속도 문제가 있을 수 있음)
#(또 Scroll 변경이 및 화면에 새로 그려질때마다 처리해서 성능 이슈가 있을 수 있음)
#(단 현재 사용중인 데이터 등록시 사용하는 FontColor를 Delegate로 이관하면.. 괜찮을 수 있음)
class QGroupBoxMyAccount(QtWidgets.QGroupBox, uic.loadUiType(resource_path("extends/QGroupBoxMyAccount.ui"))[0]):
    accountChanged = QtCore.pyqtSignal(object);

    def __init__(self, parent=None):
        super(QGroupBoxMyAccount, self).__init__(parent);
        self.setupUi(self);
        self.uValue1.currentIndexChanged.connect(self.accountChangeEvent);
        self.vTodayBuyAmount = 0;
        self.vTodayNowAmount = 0;

    #계좌 현황/ 사용자정보를 업데이트하는 함수
    def setAccountInfo(self, accountInfo):
        #계좌내역
        vTotalBuyAmount   = accountInfo.get("vTotalBuyAmount" , self.vTotalBuyAmount.text());
        vTotalNowAmount   = accountInfo.get("vTotalNowAmount" , self.vTotalNowAmount.text());
        vOrderableAmount  = accountInfo.get("vOrderableAmount", self.vOrderableAmount.text());
        vTodayBuyAmount   = accountInfo.get("vTodayBuyAmount" , self.vTodayBuyAmount);
        vTodayNowAmount   = accountInfo.get("vTodayNowAmount" , self.vTodayNowAmount);

        vTotalBuyAmount  = int(vTotalBuyAmount.replace(",", "")  if     type(vTotalBuyAmount)  != int          else vTotalBuyAmount);
        vTotalNowAmount  = int(vTotalNowAmount.replace(",", "")  if     type(vTotalNowAmount)  != int          else vTotalNowAmount);
        vOrderableAmount = int(vOrderableAmount.replace(",", "") if not type(vOrderableAmount) in [int, float] else vOrderableAmount);
        vTodayBuyAmount  = vTodayBuyAmount if type(vTodayBuyAmount)  != int else int(vTodayBuyAmount);
        vTodayNowAmount  = vTodayNowAmount if type(vTodayNowAmount)  != int else int(vTodayNowAmount);
        vTotalProfit     = 0;
        vTotalProfitRate = 0.00;
        vTodayProfit     = 0;
        vTodayProfitRate = 0.00;

        if vTotalBuyAmount != 0:
            vTotalProfit     = vTotalNowAmount - vTotalBuyAmount;
            vTotalProfitRate = vTotalProfit / vTotalBuyAmount * 100;
        
        if vTodayBuyAmount != 0:
            vTodayProfit     = vTodayNowAmount - vTodayBuyAmount;
            vTodayProfitRate = vTodayProfit / vTodayBuyAmount * 100;
        
        self.vTotalBuyAmount.setText("{0:,}".format(vTotalBuyAmount));
        self.vTotalNowAmount.setText("{0:,}".format(vTotalNowAmount));
        self.vTodayBuyAmount = vTodayBuyAmount;
        self.vTodayNowAmount = vTodayNowAmount;
        self.vOrderableAmount.setText("{0:,}".format(int(vOrderableAmount)));
        self.vTotalProfit.setText("{0:+,}".format(int(vTotalProfit)));
        self.vTotalProfitRate.setText("{0:+,.2f}".format(vTotalProfitRate));
        self.vTodayProfit.setText("{0:+,}".format(int(vTodayProfit)));
        self.vTodayProfitRate.setText("{0:+,.2f}".format(vTodayProfitRate));
        
        color = "red"   if vTotalProfit >  0 else "blue";
        color = "black" if vTotalProfit == 0 else color;

        self.vTotalProfit.setStyleSheet("QLabel {color: %s}" % color);
        self.vTotalProfitRate.setStyleSheet("QLabel {color: %s}" % color);
        
        color = "red"   if vTodayProfit >  0 else "blue";
        color = "black" if vTodayProfit == 0 else color;

        self.vTodayProfit.setStyleSheet("QLabel {color: %s}" % color);
        self.vTodayProfitRate.setStyleSheet("QLabel {color: %s}" % color);

        #사용자 정보
        if "uValue1" in accountInfo:
            self.uValue1.clear();
            self.uValue1.addItem("--선택해주세요--", "");

            for value in accountInfo["uValue1"]:
                key = value;
                value = value[:4] + "-" + value[4:8]
                self.uValue1.addItem(value, key);
        
        if "uValue3" in accountInfo:
            (sGubun, sColor) = ("모의투자", "blue") if accountInfo["uValue3"] == "1" else ("실전투자", "red");
            self.uValue3.setText(sGubun);
            self.uValue3.setStyleSheet("QLabel {color: %s}" % sColor);
            
        self.uValue2.setText(accountInfo.get("uValue2", self.uValue2.text())),
    
    #계좌 현황 사용자정보를 가져오는 함수
    def getAccountInfo(self):
        uValue1 = [];
        for idx in range(self.uValue1.count()):
            if idx != 0:
                uValue1.append(self.uValue1.itemData(idx));
        
        return {
            "vTotalBuyAmount" : int(self.vTotalBuyAmount.text().replace(",", "")),
            "vTotalNowAmount" : int(self.vTotalNowAmount.text().replace(",", "")),
            "vOrderableAmount": int(self.vOrderableAmount.text().replace(",", "")),
            "vTodayBuyAmount" : self.vTodayBuyAmount,
            "vTodayNowAmount" : self.vTodayNowAmount,
            "uValue1"         : uValue1,
            "uValue2"         : self.uValue2.text(),
            "uValue3"         : "1" if self.uValue3.text() == "모의투자" else "0",
        };

    #사용자계좌, 계정 정보 초기화
    def clear(self, area=None):
        clearObj = {};
        if area == None or area == "account":
            clearObj["vTotalBuyAmount" ] = 0;
            clearObj["vTotalNowAmount" ] = 0;
            clearObj["vOrderableAmount"] = 0;
            clearObj["vTodayBuyAmount" ] = 0;
            clearObj["vTodayNowAmount" ] = 0;
            
        if area == None or area == "userInfo":
            clearObj["uValue1"] = [];
            clearObj["uValue2"] = "";
            clearObj["uValue3"] = "1";

        self.setAccountInfo(clearObj);
            
    #계좌정보 변경 이벤트 시그널
    def accountChangeEvent(self, index):
        if index != -1:
            self.accountChanged.emit(self.uValue1.currentData());
    
    def updateOrderableAmount(self, amount):
        vOrderableAmount = int(self.vOrderableAmount.text().replace(",","")) + amount;
        self.vOrderableAmount.setText("{0:,}".format(vOrderableAmount));
        return vOrderableAmount;

if __name__ == "__main__":
    a = {"sHoga" : "00"};
    print(a.get("sHoga", "TEST") == "00");

