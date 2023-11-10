import sys, os, pprint;

from PyQt5               import uic, QtWidgets, QtCore, QtGui;

#프로그램 기본 설정
    #당일 거래한 종목 조건식에서 다시 나와도 재매수금지
    #당일청산설정(15:10분에 전량 시장가 매도)
    #계좌 익절 수익율(계좌 목표이익에 도달하면 전체 매도 후 프로그램 종료)
    #계좌 손절 수익율(계좌 목표손해에 도달하면 전체 매도 후 프로그램 종료)
    #매수금액비율(지정금액, %지정) 기준으로 매수주문 처리함

#손익설정
    #손실율(%) 손절(추매 설정시 N회 설정에 따른 이전 보유량의 x%만큼 주식 추가 매수)
    #스탑트레일링(발동조건 수익율, 발동후 분할매도 비율/수익율, 발동후 손실매도율)
    #스탑로스 (목표수익율, 손절율)
    #횡보설정 N분간 매수금액 대비 상하 % 박스권일경우.. 전량 매도(보류..)

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class ModalSetting(QtWidgets.QDialog, uic.loadUiType(resource_path("modules/setting/ModalSettings.ui"))[0]):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self);
        self.parent = parent;
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint);
        self.settings = QtCore.QSettings("settings/config.ini", QtCore.QSettings.IniFormat);
        self.getSetting();
        
        self.isChanged = False;

        self.btnSave.clicked.connect(self.saveSlot);
        self.btnClose.clicked.connect(self.close);
        self.vBuyRate.toggled.connect(self.changeValue);
        self.vBuyAmount.toggled.connect(self.changeValue);
        self.vAccountPlusEndActive.stateChanged.connect(self.changeValue);
        self.vAccountMinusEndActive.stateChanged.connect(self.changeValue)
        self.vOrderCancelSecActive.stateChanged.connect(self.changeValue)
        self.vtsTouchDivideBuyActive.stateChanged.connect(self.changeValue);
        self.vslTouchDivideBuyActive.stateChanged.connect(self.changeValue);
        self.tabWidget.currentChanged.connect(self.currentChanged);
    
    def getSetting(self):
        runStartTime = self.settings.value("PROGRAM/vRunStartTime", "0900");
        runEndTime   = self.settings.value("PROGRAM/vRunEndTime"  , "1515");
        runStartTime = QtCore.QTime(int(runStartTime[:2]), int(runStartTime[2:]));
        runEndTime   = QtCore.QTime(int(runEndTime[:2]), int(runEndTime[2:]));
        
        #GENERAL 설정
        self.currentTab  = self.settings.value("currentTab",  0, int);
        self.parent.appSettings.__setattr__("currentTab", self.currentTab);
        self.lastRunDate = self.settings.value("lastRunDate", QtCore.QDateTime().currentDateTime().toString("yyyyMMdd"));
        self.parent.appSettings.__setattr__("lastRunDate", self.lastRunDate);
        self.orderList   = self.settings.value("orderList", set(), set);
        self.parent.appSettings.__setattr__("orderList", self.orderList);
        
        self.vAutoLogin.setChecked(self.settings.value("vAutoLogin", True, bool));
        self.parent.appSettings.__setattr__("vAutoLogin", self.vAutoLogin.isChecked());
        
        self.tabWidget.setCurrentIndex(self.currentTab);
        
        self.myStrategy  =  self.settings.value("myStrategy", dict(), dict);
        self.parent.appSettings.__setattr__("myStrategy", self.myStrategy);

        #프로그램 설정
        self.vRunStartTime.setTime(runStartTime);                                                                   #자동매매 시작시간(HHMM)
        self.parent.appSettings.__setattr__("vRunStartTime", runStartTime);
        self.vRunEndTime.setTime(runEndTime);                                                                       #자동매매 종료시간(HHMM)
        self.parent.appSettings.__setattr__("vRunEndTime", runEndTime);
        self.vAccountPlusEndActive.setChecked(self.settings.value("PROGRAM/vAccountPlusEndActive", False, bool));   #계좌 수익종료(check)
        self.parent.appSettings.__setattr__("vAccountPlusEndActive", self.vAccountPlusEndActive.isChecked());
        self.vAccountPlusEnd.setValue(self.settings.value("PROGRAM/vAccountPlusEnd", 5.00, float));                 #계좌 수익종료(%)
        self.parent.appSettings.__setattr__("vAccountPlusEnd", self.vAccountPlusEnd.value());
        self.vAccountMinusEndActive.setChecked(self.settings.value("PROGRAM/vAccountMinusEndActive", False, bool)); #계좌 손실종료(check)
        self.parent.appSettings.__setattr__("vAccountMinusEndActive", self.vAccountMinusEndActive.isChecked());
        self.vAccountMinusEnd.setValue(self.settings.value("PROGRAM/vAccountMinusEnd", -5.00, float));              #계좌 손실종료(%)
        self.parent.appSettings.__setattr__("vAccountMinusEnd", self.vAccountMinusEnd.value());
        self.vTradeMaxCount.setValue(self.settings.value("PROGRAM/vTradeMaxCount", 10, int));                       #최대 거래 종목 갯수(개)
        self.parent.appSettings.__setattr__("vTradeMaxCount", self.vTradeMaxCount.value());

        self.vOrderCancelSecActive.setChecked(self.settings.value("PROGRAM/vOrderCancelSecActive", False, bool));   #미체결자동취소(check)
        self.parent.appSettings.__setattr__("vOrderCancelSecActive", self.vOrderCancelSecActive.isChecked());
        self.vOrderCancelSec.setValue(self.settings.value("PROGRAM/vOrderCancelSec", 10, int));                     #미체결자동취소(초)
        self.parent.appSettings.__setattr__("vOrderCancelSec", self.vOrderCancelSec.value());

        self.vReOrderActive.setChecked(self.settings.value("PROGRAM/vReOrderActive", True, bool));                  #재매수금지(check)
        self.parent.appSettings.__setattr__("vReOrderActive", self.vReOrderActive.isChecked());
        self.vDayClearActive.setChecked(self.settings.value("PROGRAM/vDayClearActive", False, bool));               #당일청산(check)
        self.parent.appSettings.__setattr__("vDayClearActive", self.vDayClearActive.isChecked());
        self.vBuyRate.setChecked(self.settings.value("PROGRAM/vBuyRate", True, bool));                              #매수금액비율(비율지정)(radio)
        self.parent.appSettings.__setattr__("vBuyRate", self.vBuyRate.isChecked());
        self.vBuyRateValue.setValue(self.settings.value("PROGRAM/vBuyRateValue", 10, int));                         #매수금액비율(비율지정 값)(%)
        self.parent.appSettings.__setattr__("vBuyRateValue", self.vBuyRateValue.value());
        self.vBuyAmount.setChecked(self.settings.value("PROGRAM/vBuyAmount", False, bool));                         #매수금액비율(금액지정)(radio)
        self.parent.appSettings.__setattr__("vBuyAmount", self.vBuyAmount.isChecked());
        self.vBuyAmountValue.setValue(self.settings.value("PROGRAM/vBuyAmountValue", 100000, int));                 #매수금액비율(금액지정 값)(원)
        self.parent.appSettings.__setattr__("vBuyAmountValue", self.vBuyAmountValue.value());

        #텔레그램 설정
        self.vBotId.setText(self.settings.value("TELEGRAM/vBotId", "", str));                                       #텔레그램 봇ID
        self.parent.appSettings.__setattr__("vBotId", self.vBotId.text());
        self.vChatId.setText(self.settings.value("TELEGRAM/vChatId", "", str));                                     #텔레그램 채팅ID
        self.parent.appSettings.__setattr__("vChatId", self.vChatId.text());

        #트레일링 스탑
        self.vtsTargetProfit.setValue(self.settings.value("TRAILING_STOP/vtsTargetProfit",  5.00, float));                  #목표 수익율(%)
        self.parent.appSettings.__setattr__("vtsTargetProfit", self.vtsTargetProfit.value());
        self.vtsTouchDivideProfit.setValue(self.settings.value("TRAILING_STOP/vtsTouchDivideProfit",  2.00, float));        #수익달성 후 분할매도 추가수익율(%)
        self.parent.appSettings.__setattr__("vtsTouchDivideProfit", self.vtsTouchDivideProfit.value());
        self.vtsTouchDivideRate.setValue(self.settings.value("TRAILING_STOP/vtsTouchDivideRate",  30, float));              #수익도달 후 분할매도 비율(%)
        self.parent.appSettings.__setattr__("vtsTouchDivideRate", self.vtsTouchDivideRate.value());
        self.vtsTouchDivideServeRate.setValue(self.settings.value("TRAILING_STOP/vtsTouchDivideServeRate",  50, float));    #수익도달 후 이익보존(%)
        self.parent.appSettings.__setattr__("vtsTouchDivideServeRate", self.vtsTouchDivideServeRate.value());
        self.vtsTargetLoss.setValue(self.settings.value("TRAILING_STOP/vtsTargetLoss", -3.00, float));                      #목표 손실율(%)
        self.parent.appSettings.__setattr__("vtsTargetLoss", self.vtsTargetLoss.value());
        self.vtsTouchDivideBuyActive.setChecked(self.settings.value("TRAILING_STOP/vtsTouchDivideBuyActive", False, bool)); #손실발생 분할매수 활성화
        self.parent.appSettings.__setattr__("vtsTouchDivideBuyActive", self.vtsTouchDivideBuyActive.isChecked());
        self.vtsTouchDivideBuy.setValue(self.settings.value("TRAILING_STOP/vtsTouchDivideBuy", 3, int));                    #손실발생 후 분할매수 횟수(회)
        self.parent.appSettings.__setattr__("vtsTouchDivideBuy", self.vtsTouchDivideBuy.value());
                
        #스탑로스
        self.vslTargetProfit.setValue(self.settings.value("STOP_LOSS/vslTargetProfit", 5.00, float));                   #목표 수익율(%)
        self.parent.appSettings.__setattr__("vslTargetProfit", self.vslTargetProfit.value());
        self.vslTargetLoss.setValue(self.settings.value("STOP_LOSS/vslTargetLoss", -3.00, float));                      #목표 손실율(%)
        self.parent.appSettings.__setattr__("vslTargetLoss", self.vslTargetLoss.value());
        self.vslTouchDivideBuyActive.setChecked(self.settings.value("STOP_LOSS/vslTouchDivideBuyActive", False, bool)); #손실발생 분할매수 활성화
        self.parent.appSettings.__setattr__("vslTouchDivideBuyActive", self.vslTouchDivideBuyActive.isChecked());
        self.vslTouchDivideBuy.setValue(self.settings.value("STOP_LOSS/vslTouchDivideBuy", 3, int));                    #손실발생 후 분할매수 횟수(회)
        self.parent.appSettings.__setattr__("vslTouchDivideBuy", self.vslTouchDivideBuy.value());
        
        today = QtCore.QDateTime().currentDateTime().toString("yyyyMMdd");
        if self.lastRunDate != today:
            self.lastRunDate = today;
            self.settings.setValue("lastRunDate", self.lastRunDate);
            self.orderList = set([]);
            self.settings.setValue("orderList", self.orderList);
            #for key in self.myStrategy:
            #    self.myStrategy[key]["tsActive"   ] = False;
            #    self.myStrategy[key]["tsHighPrice"] = 0;
            #    self.myStrategy[key]["tsDivSell"  ] = 0;
            #self.settings.setValue("myStrategy", self.myStrategy);

        
        self.vAccountPlusEnd.setEnabled(self.vAccountPlusEndActive.isChecked());
        self.vAccountMinusEnd.setEnabled(self.vAccountMinusEndActive.isChecked());
        self.vOrderCancelSec.setEnabled(self.vOrderCancelSecActive.isChecked());
        self.vtsTouchDivideBuy.setEnabled(self.vtsTouchDivideBuyActive.isChecked());
        self.vslTouchDivideBuy.setEnabled(self.vslTouchDivideBuyActive.isChecked());

        if self.vBuyRate.isChecked():
            self.vBuyRateValue.setEnabled(True);
            self.vBuyAmountValue.setEnabled(False);
        else:
            self.vBuyRateValue.setEnabled(False);
            self.vBuyAmountValue.setEnabled(True);
    
    def setSetting(self):
        #GENERAL 설정
        self.settings.setValue("currentTab"                           , self.currentTab);
        self.settings.setValue("lastRunDate"                          , self.lastRunDate);
        self.settings.setValue("orderList"                            , self.orderList);
        self.settings.setValue("myStrategy"                           , self.myStrategy);
        self.settings.setValue("vAutoLogin"                           , self.vAutoLogin.isChecked());
        
        #프로그램 설정
        self.settings.setValue("PROGRAM/vRunStartTime"                , self.vRunStartTime.time().toString("hhmm"));
        self.settings.setValue("PROGRAM/vRunEndTime"                  , self.vRunEndTime.time().toString("hhmm"));
        self.settings.setValue("PROGRAM/vAccountPlusEndActive"        , self.vAccountPlusEndActive.isChecked());
        self.settings.setValue("PROGRAM/vAccountPlusEnd"              , self.vAccountPlusEnd.value());
        self.settings.setValue("PROGRAM/vAccountMinusEndActive"       , self.vAccountMinusEndActive.isChecked());
        self.settings.setValue("PROGRAM/vAccountMinusEnd"             , self.vAccountMinusEnd.value());
        self.settings.setValue("PROGRAM/vTradeMaxCount"               , self.vTradeMaxCount.value());

        self.settings.setValue("PROGRAM/vOrderCancelSecActive"        , self.vOrderCancelSecActive.isChecked());
        self.settings.setValue("PROGRAM/vOrderCancelSec"              , self.vOrderCancelSec.value());

        self.settings.setValue("PROGRAM/vReOrderActive"               , self.vReOrderActive.isChecked());
        self.settings.setValue("PROGRAM/vDayClearActive"              , self.vDayClearActive.isChecked());
        self.settings.setValue("PROGRAM/vBuyRate"                     , self.vBuyRate.isChecked());
        self.settings.setValue("PROGRAM/vBuyRateValue"                , self.vBuyRateValue.value());
        self.settings.setValue("PROGRAM/vBuyAmount"                   , self.vBuyAmount.isChecked());
        self.settings.setValue("PROGRAM/vBuyAmountValue"              , self.vBuyAmountValue.value());
        #텔레그램 설정
        self.settings.setValue("TELEGRAM/vBotId"                      , self.vBotId.text());
        self.settings.setValue("TELEGRAM/vChatId"                     , self.vChatId.text());
        #트레일링 스탑
        self.settings.setValue("TRAILING_STOP/vtsTargetProfit"        , self.vtsTargetProfit.value());
        self.settings.setValue("TRAILING_STOP/vtsTouchDivideProfit"   , self.vtsTouchDivideProfit.value());
        self.settings.setValue("TRAILING_STOP/vtsTouchDivideRate"     , self.vtsTouchDivideRate.value());
        self.settings.setValue("TRAILING_STOP/vtsTouchDivideServeRate", self.vtsTouchDivideServeRate.value());
        self.settings.setValue("TRAILING_STOP/vtsTargetLoss"          , self.vtsTargetLoss.value());
        self.settings.setValue("TRAILING_STOP/vtsTouchDivideBuyActive", self.vtsTouchDivideBuyActive.isChecked());
        self.settings.setValue("TRAILING_STOP/vtsTouchDivideBuy"      , self.vtsTouchDivideBuy.value());
        #스탑로스
        self.settings.setValue("STOP_LOSS/vslTargetProfit"            , self.vslTargetProfit.value());
        self.settings.setValue("STOP_LOSS/vslTargetLoss"              , self.vslTargetLoss.value());
        self.settings.setValue("STOP_LOSS/vslTouchDivideBuyActive"    , self.vslTouchDivideBuyActive.isChecked());
        self.settings.setValue("STOP_LOSS/vslTouchDivideBuy"          , self.vslTouchDivideBuy.value());
    
    #설정값 변경
    def changeValue(self):
        self.vAccountPlusEnd.setEnabled(self.vAccountPlusEndActive.isChecked());
        self.vAccountMinusEnd.setEnabled(self.vAccountMinusEndActive.isChecked());
        self.vOrderCancelSec.setEnabled(self.vOrderCancelSecActive.isChecked());
        self.vtsTouchDivideBuy.setEnabled(self.vtsTouchDivideBuyActive.isChecked());
        self.vslTouchDivideBuy.setEnabled(self.vslTouchDivideBuyActive.isChecked());

        if self.vBuyRate.isChecked():
            self.vBuyRateValue.setEnabled(True);
            self.vBuyAmountValue.setEnabled(False);
        else:
            self.vBuyRateValue.setEnabled(False);
            self.vBuyAmountValue.setEnabled(True);
    
    #모달창 Show 이벤트
    def showEvent(self, event):
        self.getSetting();

    #손익설정 Tab Active 변경 이벤트
    def currentChanged(self, index):
        self.currentTab = index;

    #기본 함수(Window창의 [X]버튼을 클릭하여 창이 닫히는 경우)
    def closeEvent(self, event):
        #창 닫을때 수정된 내용이 있으면 확인..
        if self.isChangeSetting():
            reply = QtWidgets.QMessageBox.question(self, "확인", "변경된 내용이 있습니다. 저장하시겠습니까?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No);

            if reply == QtWidgets.QMessageBox.Yes:
                self.setSetting();
            event.accept();

        if type(event) == bool:
            #self.close();
            pass;
    
    #변경된 내용이 있는지 체크하는 함수
    def isChangeSetting(self):
        result = False;

        if self.currentTab != self.parent.appSettings.__getattribute__("currentTab"):
            result = True;
        else:
            for key in self.parent.appSettings.__dict__:
                if key.startswith("v"):
                    target = self.__getattribute__(key);
                    diff = "";

                    if [QtWidgets.QCheckBox, QtWidgets.QRadioButton].count(type(target)) != 0:
                        diff = target.isChecked();
                    elif [QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox].count(type(target)) != 0:
                        diff = target.value();
                    elif [QtWidgets.QTimeEdit].count(type(target)) != 0:
                        diff = target.time();
                    elif [QtWidgets.QLineEdit].count(type(target)) != 0:
                        diff = target.text();
                    
                    if diff != self.parent.appSettings.__getattribute__(key):
                        result = True;
                        if result:
                            break;
        
        return result;

    #창 종료 이벤트 슬롯
    def saveSlot(self):
        self.setSetting();
        self.getSetting();
        self.close();
