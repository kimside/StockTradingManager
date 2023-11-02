import sys, os, datetime, ctypes, traceback, logging, time, telegram, asyncio;

from telegram import Update;
from telegram.constants import ParseMode;
from telegram.ext import Application, CommandHandler, ContextTypes;

from PyQt5                              import uic, QtWidgets, QtCore, QtGui, QAxContainer;
from extends.QTableWidgetMyStocks       import *;

from modules.api.KiwoomAPI              import KiwoomAPI;
from modules.exception.NotInsallOpenAPI import NotInsallOpenAPI;
from modules.api.entity.Opt10001        import *;
from modules.api.entity.Opw00001        import *;
from modules.api.entity.Opw00004        import *;
from modules.api.entity.Opw00011        import *;
from modules.api.entity.Opw00014        import *;
from modules.api.entity.Opt10001        import *;
from modules.api.entity.Opt10075        import *;
from modules.api.entity.Opt10077        import *;
from modules.api.entity.Optkwfid        import *;

from modules.setting.ModalSettings      import ModalSetting;
from modules.setting.ModalInformation   import ModalInformation;
from modules.test.TestChejan0           import TestChejan0;
from modules.test.TestChejan1           import TestChejan1;
from modules.test.TestCode              import TestCode;
from modules.setting.entity.Settings    import Settings;
from modules.strategy.MyStrategy        import MyStrategy;

loggingDir = "logging/{0}/error/".format(datetime.datetime.now().strftime("%Y%m%d"));
os.makedirs(os.path.dirname(loggingDir), exist_ok=True);
logging.basicConfig(filename=loggingDir + "error.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s');
logger=logging.getLogger(__name__);
"""
화면번호 사용일람
--------------------------------------
1000: tr요청(기본값)
2000: 다건 tr요청(조건검색결과는 8000을 사용)
3000: 주문요청
4000: 내 계좌 실시간 시세요청
5000: 
6000:
7000: 미체결잔고 실시간 시세요청
8000: 조건검색 실시간 시세요청
9000: 기타 미지정
"""
def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class Main(QtWidgets.QMainWindow, KiwoomAPI, uic.loadUiType(resource_path("main.ui"))[0]):
    def __init__(self, *args, **kwargs):
        super().__init__();
        self.kwargs = kwargs;
        
        self.setupUi(self);
        self.menuTest.menuAction().setVisible(True if self.kwargs.get("mode", "stage") == "debug" else False);
        self.appSettings      = Settings();
        self.modalSetting     = ModalSetting(self);    #Setting       Dialog(Modal)
        self.modalInformation = ModalInformation(self);#Information   Dialog(Modal)
        self.testChejan0      = TestChejan0(self);     #Chejan0  Test Dialog(Modal)
        self.testChejan1      = TestChejan1(self);     #Chejan1  Test Dialog(Modal)
        self.testCode         = TestCode(self);        #TestCode Test Dialog(Modal)
        self.myStrategy       = MyStrategy(self);
        
        self.initTableWidget();
        self.tableWidgetClear();

        #print(self.appSettings.myStrategy);
        #self.appSettings.orderList.add(("001200", "유진투자증권"));
        #self.appSettings.orderList.add(("001360", "삼성제약"));
        #self.appSettings.setValue("orderList", self.appSettings.orderList);
        #self.appSettings.sync();

        self.btnRun.setEnabled(False);
        self.gbMyAccount.uValue1.setEnabled(False);
        self.cbConUp.setEnabled(False);
        self.btnReload.setEnabled(False);
        
        self.tabWidget.currentChanged.connect(self.resizeEvent);
        self.tabAccount.currentChanged.connect(self.resizeEvent);
        self.cbConUp.currentIndexChanged.connect(self.conditionChangeSlot);
        self.gbMyAccount.accountChanged.connect(self.accountChangedSlot);
        self.stockSignal.connect(self.stockSignalSlot);
        self.conInOutSignal.connect(self.conInOutSlot);
        self.apiMsgSignal.connect(self.addConsoleSlot);
        self.loginSignal.connect(self.isLoginSlot);
        self.chejanSignal.connect(self.addChejanSlot);

        self.btnConMax.clicked.connect(lambda: self.setSplitterSlot("con"));
        self.btnMiddle.clicked.connect(lambda: self.setSplitterSlot("mid"));
        self.btnMyMax.clicked.connect(lambda : self.setSplitterSlot("my"));

        self.actExit.triggered.connect(self.close);
        self.actLogin.triggered.connect(self.actLoginSlot);
        self.actInformation.triggered.connect(lambda: self.showModalSlot("modalInformation"));
        self.actSetting.triggered.connect(lambda: self.showModalSlot("modalSetting"));
        self.actChejan0.triggered.connect(lambda: self.showModalSlot("testChejan0"));
        self.actChejan1.triggered.connect(lambda: self.showModalSlot("testChejan1"));
        self.actTestCode.triggered.connect(lambda: self.showModalSlot("testCode"));

        self.btnReload.clicked.connect(self.loadConditionsSlot);
        self.btnRun.clicked.connect(self.btnRunSlot);

        self.tbConsole.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu);
        historyClear = QtWidgets.QAction("HistoryClear" , self.tbConsole);
        historyClear.setIcon(QtGui.QIcon(resource_path("resources/iconEraser.png")));
        historyClear.triggered.connect(self.tbConsole.clear);
        self.tbConsole.addAction(historyClear)

        self.pageNavigation.setVisible(False);

        #TrayIcon 설정
        #self.systray = QtWidgets.QSystemTrayIcon(self);
        #icon = self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon);
        #self.systray.setIcon(icon);
        #self.systray.show();

        if datetime.datetime.now().strftime("%H%M") < "1600":
            self.showDownTimer = QtCore.QTimer();
            self.showDownTimer.setInterval(1000);
            self.showDownTimer.timeout.connect(self.shutdown);
            self.showDownTimer.start();

        if self.appSettings.__getattribute__("vAutoLogin"):
            self.actLoginSlot();
    
    async def sendMessage(self, telegramMsg): #실행시킬 함수명 임의지정
        self.appSettings.vBotId;
        self.appSettings.vChatId;

        if self.kwargs.get("mode", "stage") != "debug":
            if self.appSettings.vBotId != "" and self.appSettings.vChatId != "":
                try:
                    bot = telegram.Bot(self.appSettings.vBotId);
                    await bot.send_message(self.appSettings.vChatId, telegramMsg, ParseMode.HTML);
                except Exception as e:
                    self.addConsoleSlot({
                        "sRQName": "Telegram",
                        "sMsg"   : "Telegram 메세지 발송 오류({0})".format(e),
                    });
            else:
                self.addConsoleSlot({
                    "sRQName": "Telegram",
                    "sMsg"   : "Telegram이 설정되어 있지 않습니다.",
                });

    #거래시간 이후 자동매매종료
    def shutdown(self):
        if datetime.datetime.now().strftime("%H%M") == "1600":
            self.myStrategy.isRun = False;
            self.showDownTimer.stop();
            self.close();
        
    #자식창 팝업 슬롯
    def showModalSlot(self, modalId):
        self.__getattribute__(modalId).exec_();
    
    #TableWdiget 컬럼 초기화
    def initTableWidget(self):
        self.twConStocks.initWidget([
            {"id": "stockCode"    , "name": "종목코드", "type": str  , "formatter": "{0:}"  , "align": QtCore.Qt.AlignRight, "isKey" : True},
            {"id": "stockName"    , "name": "종목명"  , "type": str  , "formatter": "{0:}"  , "align": QtCore.Qt.AlignLeft},
            {"id": "nowPrice"     , "name": "현재가"  , "type": int  , "formatter": "{0:,}" , "align": QtCore.Qt.AlignRight},
            {"id": "stdPrice"     , "name": "기준가"  , "type": int  , "formatter": "{0:,}" , "align": QtCore.Qt.AlignRight},
            {"id": "diffPrice"    , "name": "전일대비", "type": int  , "formatter": "{0:+,}", "align": QtCore.Qt.AlignRight},
            {"id": "changeRate"   , "name": "등락율"  , "type": float, "formatter": "{0:+}%", "align": QtCore.Qt.AlignRight, "isBg": True},
            {"id": "tradeCount"   , "name": "거래량"  , "type": int  , "formatter": "{0:,}" , "align": QtCore.Qt.AlignRight},
            {"id": "tradeStrength", "name": "체결강도", "type": float, "formatter": "{0:,}" , "align": QtCore.Qt.AlignRight},
        ]);
        
        self.twMyStocks.initWidget([
            {"id": "stockCode"     , "name": "종목코드"  , "type": str  , "formatter": "{0:}"     , "align": QtCore.Qt.AlignRight, "isKey" : True},
            {"id": "stockName"     , "name": "종목명"    , "type": str  , "formatter": "{0:}"     , "align": QtCore.Qt.AlignLeft},
            {"id": "averagePrice"  , "name": "평균단가"  , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "nowPrice"      , "name": "현재가"    , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "breakEvenPrice", "name": "손익분기가", "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "profit"        , "name": "손익금액"  , "type": int  , "formatter": "{0:+,}"   , "align": QtCore.Qt.AlignRight},
            {"id": "profitRate"    , "name": "손익율"    , "type": float, "formatter": "{0:+.2f}%", "align": QtCore.Qt.AlignRight, "isBg": True},
            {"id": "buyAmount"     , "name": "매입금액"  , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "nowAmount"     , "name": "평가금액"  , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "totalTax"      , "name": "세금합계"  , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "stockCount"    , "name": "보유량"    , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
            {"id": "reminingCount" , "name": "매도가능"  , "type": int  , "formatter": "{0:,}"    , "align": QtCore.Qt.AlignRight},
        ]);

        self.twChejanStocks.initWidget([
            {"id": "chejanTime"  , "name": "요청시간"  , "type": datetime.datetime, "formatter": "{0:%Y-%m-%d %H:%M:%S}" , "align": QtCore.Qt.AlignRight},
            {"id": "orderNo"     , "name": "주문번호"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight, "isKey": True},
            {"id": "hogaGb"      , "name": "주문구분"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "stockCode"   , "name": "종목코드"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight},
            {"id": "stockName"   , "name": "종목명"    , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignLeft},
            {"id": "orderStatus" , "name": "주문상태"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "nowPrice"    , "name": "현재가"    , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "orderPrice"  , "name": "주문가격"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "orderCount"  , "name": "주문수량"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "chejanCount" , "name": "체결수량"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "missCount"   , "name": "미체결수량", "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "chejanGb"    , "name": "매매구분"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "oriOrderNo"  , "name": "원주문번호", "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight},
            {"id": "bgCol"       , "name": "배경색"    , "type": int              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight, "isBg": True, "isVisible": False},
        ]);
        self.twChejanStocks.sortItems(0, QtCore.Qt.DescendingOrder);

        self.twChejanHisStocks.initWidget([
            {"id": "chejanTime"  , "name": "요청시간"  , "type": datetime.datetime, "formatter": "{0:%Y-%m-%d %H:%M:%S}" , "align": QtCore.Qt.AlignRight},
            {"id": "orderNo"     , "name": "주문번호"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight},
            {"id": "hogaGb"      , "name": "주문구분"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "stockCode"   , "name": "종목코드"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight},
            {"id": "stockName"   , "name": "종목명"    , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignLeft},
            {"id": "orderStatus" , "name": "주문상태"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "orderPrice"  , "name": "주문가격"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "orderCount"  , "name": "주문수량"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "chejanCount" , "name": "체결수량"  , "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "missCount"   , "name": "미체결수량", "type": int              , "formatter": "{0:,}"                 , "align": QtCore.Qt.AlignRight},
            {"id": "chejanGb"    , "name": "매매구분"  , "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignCenter},
            {"id": "oriOrderNo"  , "name": "원주문번호", "type": str              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight},
            {"id": "bgCol"       , "name": "배경색"    , "type": int              , "formatter": "{0:}"                  , "align": QtCore.Qt.AlignRight, "isBg": True, "isVisible": False},
        ]);
        self.twChejanHisStocks.sortItems(1, QtCore.Qt.DescendingOrder);    

    #로그인 변경 이벤트 슬롯
    def isLoginSlot(self, isLogin):
        self.isLogin = isLogin;
        
        self.actLogin.setText("Logout" if self.isLogin else "Login");
        self.actLogin.setShortcut("Ctrl+L");
        self.actLogin.setEnabled(False if self.isLogin else True);
        self.gbMyAccount.uValue1.setEnabled(True if self.isLogin else False);
        self.btnRun.setEnabled(True if self.isLogin else False);
        self.btnReload.setEnabled(True if self.isLogin else False);
        self.cbConUp.setEnabled(True if self.isLogin else False);

        if self.isLogin:
            self.gbMyAccount.setAccountInfo({
                "uValue1": self.userInfo.accountList,
                "uValue2": self.userInfo.userName,
                "uValue3": self.userInfo.getServerGubun,
            });

            self.loadConditionsSlot();
            self.gbMyAccount.uValue1.setFocus();
            self.btnRun.setStyleSheet("QPushButton {background-color: green; color: white;}");
            self.btnRun.setText("정지(&F8)" if self.myStrategy.isRun else "실행(&F8)");
            self.btnRun.setShortcut("F8");

            if self.kwargs.get("accountNo", "") != "":
                for idx in range(self.gbMyAccount.uValue1.count()):
                    if self.kwargs["accountNo"] == self.gbMyAccount.uValue1.itemData(idx):
                        self.gbMyAccount.uValue1.setCurrentIndex(idx);
                        break;
            
            if self.kwargs.get("condition", "") != "":
                for idx in range(self.cbConUp.count()):
                    if self.kwargs["condition"] == self.cbConUp.itemText(idx):
                        self.cbConUp.setCurrentIndex(idx);
                        break;
            
            if self.kwargs.get("accountNo", "") != "" and self.kwargs.get("condition", "") != "":
                self.btnRunSlot();
        
        else:
            self.cbConUp.clear();
            self.cbConUp.addItem("--조건식을 선택해주세요--", "");
            self.tableWidgetClear();

            self.myStrategy.isRun = False;
            self.gbMyAccount.clear();
            self.sendConditionStop("8000", self.cbConUp.currentText(), self.cbConUp.currentData());
            self.setRealClear("8000");
    
    #계좌번호 변경 이벤트 슬롯
    def accountChangedSlot(self, accountNo):
        self.gbMyAccount.clear("account");
        self.tableWidgetClear();
        
        if accountNo != "":
            accountInfo = self.reqCommRqData({
                "sRQName": "계좌평가현황요청",
                "sTrCode": "OPW00004",
                "sScrNo" : "1000",
                "input"  : {
                    "계좌번호"            : accountNo,
                    "비밀번호"            : "",
                    "상장폐지조회구분"    : "1",
                    "비밀번호입력매체구분": "00",
                },
                "output": Opw00004(),
            });
            
            if type(accountInfo) == Opw00004:
                opw00011 = self.reqCommRqData({
                    "sRQName": "증거금율별주문가능수량조회요청",
                    "sTrCode": "opw00011",
                    "sScrNo" : "1000",
                    "input"  : {
                        "계좌번호"            : accountNo,
                        "비밀번호"            : "",
                        "비밀번호입력매체구분": "00",
                        "종목번호"            : "005930",#없으면 오류가 발생하여 임의로 종목번호를 넣는다.
                        "매수가격"            : "",
                    },
                    "output": Opw00011(),
                });

                opt10075 = self.reqCommRqData({
                    "sRQName": "미체결요청",
                    "sTrCode": "opt10075",
                    "sScrNo": "1000",
                    "input" : {
                        "계좌번호"    : accountNo,
                        "전체종목구분": "0",
                        "매매구분"    : "0",
                        "종목코드"    : "",
                        "체결구분"    : "0",
                    },
                    "output": Opt10075(),
                });
                
                opt10077 = self.reqCommRqData({
                    "sRQName": "당일실현손익상세요청",
                    "sTrCode": "opt10077",
                    "sScrNo" : "1000",
                    "input"  : {
                        "계좌번호": accountNo,
                        "비밀번호": "",
                        "종목코드": "",
                    },
                    "output": Opt10077(),
                });
                
                #내계좌정보(기본값)
                accountValues = {
                    "vTotalBuyAmount" : 0,
                    "vTotalNowAmount" : 0,
                    "vOrderableAmount": opw00011.__getitem__("sField28"),#미수불가주문가능금액
                    "vTodayBuyAmount" : 0,
                    "vTodayNowAmount" : 0,
                };

                #테스트를 위한 로그기록
                testLogFile(opt10075);
                testLogFile(opt10077);

                for index, value in enumerate(opt10077.__getitem__("mField09")):
                    if value != "":
                        stockProfit = self.calcStock({
                            "stockCode"     : opt10077.__getitem__("mField09")[index][-6:],
                            "stockName"     : opt10077.__getitem__("mField01")[index],
                            "averagePrice"  : opt10077.__getitem__("mField03")[index],
                            "nowPrice"      : opt10077.__getitem__("mField04")[index],
                            "stockCount"    : opt10077.__getitem__("mField02")[index],
                            "reminingCount" : 0,
                        });
                        accountValues["vTodayBuyAmount"] += stockProfit["buyAmount"];
                        accountValues["vTodayNowAmount"] += stockProfit["nowAmount"];

                #내 계좌정보에 보유 주식 넣기
                for idx, value in enumerate(accountInfo.__getitem__("mField01")):
                    if value != "":
                        myStock = self.calcStock({
                            "stockCode"    : accountInfo.__getitem__("mField01")[idx],
                            "stockName"    : accountInfo.__getitem__("mField02")[idx],
                            "averagePrice" : accountInfo.__getitem__("mField04")[idx],
                            "nowPrice"     : accountInfo.__getitem__("mField05")[idx],
                            "stockCount"   : accountInfo.__getitem__("mField03")[idx],
                            "reminingCount": accountInfo.__getitem__("mField03")[idx],
                        });
                        accountValues["vTotalBuyAmount"] += int(myStock["buyAmount"]);
                        accountValues["vTotalNowAmount"] += int(myStock["nowAmount"]);
                        self.twMyStocks.addRows(myStock);

                #내계좌정보(반영)
                self.gbMyAccount.setAccountInfo(accountValues);

                #내 계좌정보 실시간 조회 등록
                sCodeList = ";".join(list(s[-6:] for s in accountInfo.__getitem__("mField01")));
                self.setRealReg("4000", sCodeList);
                
                #체결잔고에서 매도, 매수, 매수취소, 매도취소 접수 항목중 
                dt = datetime.datetime.now();
                cancelList = [];
                for index, value in enumerate(opt10075.__getitem__("mField02")):
                    if value != "":
                        chejanTime = opt10075.__getitem__("mField15")[index];
                        row = {
                            "chejanTime" : dt.replace(hour=int(chejanTime[:2]), minute=int(chejanTime[2:4]), second=int(chejanTime[-2:])),
                            "orderNo"    : opt10075.__getitem__("mField02")[index],
                            "hogaGb"     : opt10075.__getitem__("mField13")[index],
                            "stockCode"  : opt10075.__getitem__("mField04")[index][-6:],
                            "stockName"  : opt10075.__getitem__("mField07")[index],
                            "nowPrice"   : opt10075.__getitem__("mField19")[index].replace("-", ""),
                            "orderStatus": opt10075.__getitem__("mField06")[index],
                            "orderPrice" : opt10075.__getitem__("mField09")[index],
                            "orderCount" : opt10075.__getitem__("mField08")[index],
                            "chejanCount": opt10075.__getitem__("mField18")[index],
                            "missCount"  : opt10075.__getitem__("mField10")[index],
                            "chejanGb"   : opt10075.__getitem__("mField14")[index],
                            "oriOrderNo" : opt10075.__getitem__("mField12")[index],
                            "bgCol"      : 1 if opt10075.__getitem__("mField13")[index] == "+매수" else -1,
                        };

                        #미체결잔고 조회시 접수상태인것은 아직 처리가 되지 않은 항목으로 계좌에 반영해야한다.
                        #체결의 경우 부분 체결된 항목은 chejanStatus가 체결로 표시되어.. 해당 항목도 목록에 추가해야 한다.(미체결이 0이 아닌것들)
                        #취소주문의 경우 orderStatus가 '확인'으로 수신된다.
                        if row["orderStatus"] == "확인":
                            cancelList.append(row);
                        
                        if row["orderStatus"] == "접수" or (row["orderStatus"] == "체결" and row["missCount"] != "0"):
                            myStocks = self.twMyStocks.getRowDatas(row["stockCode"]);
                            
                            #[-매도]로 남아있는 미체결 주문의 경우 해당 주문수량을 보유주식의 주문가능수량에서 뺀다.
                            if row["hogaGb"] == "-매도":#+매수, -매도 매수취소, 매도취소, 매수정정, 매도정정
                                for myStock in myStocks:
                                    myStock["reminingCount"] = myStock["reminingCount"] - int(row["missCount"]);
                                    self.twMyStocks.addRows([myStock]);
                        
                            self.twChejanStocks.addRows(row);                    
                        self.twChejanHisStocks.addRows(row);
                
                #매도취소, 매수취소, 매수정정, 매도정정는 미체결 잔고 QTableWidget에서 삭제
                removeList = list(x["oriOrderNo"] for x in cancelList);
                self.twChejanStocks.delRows(removeList);
                
                #미체결 항목은 실시간 데이터 수신하도록 추가함(화면번호: 7000)
                chejanStocks = self.twChejanStocks.getRowDatas();
                for chejan in chejanStocks:
                    self.setRealReg("7000", chejan["stockCode"]);

                myStrategys = list(self.appSettings.myStrategy.items());
                if len(myStrategys) != 0:
                    for key, strategy in myStrategys:
                        if self.twMyStocks.isExist(key) == None:
                            del(self.appSettings.myStrategy[key]);
                        else:
                            for row in self.twMyStocks.getRowDatas(key):
                                strategy["nowPrice"]     = row["nowPrice"];
                                strategy["averagePrice"] = row["averagePrice"];
                        self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
                else:
                    for myStocks in self.twMyStocks.getRowDatas():
                        thisStock = myStocks.copy();
                        self.appSettings.myStrategy[thisStock["stockCode"]] = {
                            "stockCode"   : thisStock["stockCode"   ],
                            "stockName"   : thisStock["stockName"   ],
                            "nowPrice"    : thisStock["nowPrice"    ],
                            "averagePrice": thisStock["averagePrice"],
                            "tsActive"    : False,
                            "tsHighPrice" : 0,
                            "tsDivSell"   : 0,
                            "tsAddBuy"    : 0,
                            "slAddBuy"    : 0,
                        };
                    self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
                self.appSettings.sync();
            else:
                if type(accountInfo) == int:
                    QtWidgets.QMessageBox.warning(self, "경고", self.getErrMsg(-10003 if accountInfo == -202 else accountInfo));
                else:
                    QtWidgets.QMessageBox.warning(self, "경고", self.getErrMsg(-99999));
                self.gbMyAccount.uValue1.setCurrentIndex(0);
        self.resizeEvent();
    
    #실시간 수신 데이터 Grid에 반영
    def stockSignalSlot(self, obj):
        sScrNoList = obj["f920"].split(";") if "f920" in obj else [];

        if obj["sRealType"] in ["주식체결"] :
            #계좌 보유주식 정보 업데이트
            if "4000" in sScrNoList:
                for myStock in self.twMyStocks.getRowDatas(obj["f9001"]):
                    myStock["nowPrice"] = obj["f10"];
                    self.twMyStocks.addRows(self.calcStock(myStock));
                    self.modalInformation.updateNowPrice(myStock);
                    self.updateSummary();
            
            #미체결 잔고 현재가 업데이트
            if "7000" in sScrNoList:
                chejanStocks = self.twChejanStocks.getRowDatas(obj["f9001"]);
                for chejanStock in chejanStocks:
                    chejanStock["nowPrice"] = obj["f10"];
                    self.twChejanStocks.addRows(chejanStock);
                
                #미체결 대기시간 초과 항목 취소 주문
                for chejanStock in self.twChejanStocks.getRowDatas():
                    if self.appSettings.vOrderCancelSecActive:
                        diff = datetime.datetime.now() - chejanStock["chejanTime"];
                        if diff.seconds > self.appSettings.vOrderCancelSec and chejanStock["hogaGb"] in ["+매수", "-매도"]:
                            self.myStrategy.orderCancel(chejanStock);
            
            #조건검색결과 정보 업데이트
            if "8000" in sScrNoList:
                conStock = {
                    "stockCode"    : obj["f9001"],
                    "stockName"    : obj["f302" ],
                    "nowPrice"     : obj["f10"  ],
                    "stdPrice"     : obj["f307" ],
                    "diffPrice"    : obj["f11"  ],
                    "changeRate"   : obj["f12"  ],
                    "tradeCount"   : obj["f13"  ],
                    "tradeStrength": obj["f228" ],
                };
                self.twConStocks.addRows([conStock]);

            #매수/매도 전략 실행
            if self.myStrategy.isRun:
                self.myStrategy.dataAnalysis(obj);
                self.myStrategy.buyStrategy(obj);
                self.myStrategy.sellStrategy(obj);
        
        elif obj["sRealType"] == "장시작시간":
            #f215( 8, 9 같은 경우 시간이 888888, 999999 이런식으로 오기도 한다.. datetime못쓰것네.. )
            f215 = {
                "0": "장시작전",
                "2": "장마감전 동시호가",
                "3": "장시작",
                "4": "장종료 예상지수종료",
                "8": "장마감",
                "9": "장종료 - 시간외종료",
                "a": "시간외 종가매매 시작",
                "b": "시간외 종가매매 종료",
                "c": "시간외 단일가 매매시작",
                "d": "시간외 단일가 매매종료",
                "s": "선옵 장마감전 동시호가 시작",
                "e": "선옵 장마감전 동시호가 종료",
            };

            marketNow = "{0}:{1}:{2}".format(obj["f20" ][:2], obj["f20" ][2:4], obj["f20" ][-2:]);
            countDown = "{0}:{1}:{2}".format(obj["f214"][:2], obj["f214"][2:4], obj["f214"][-2:]);
            self.addConsoleSlot({
                "sRQName": f215.get(obj["f215"], "기타"),
                "sTrCode": "",
                "sScrNo" : "9999",
                "sMsg"   : "서버시간: {0}, 남은시간: {1}".format(marketNow, countDown),
            });
            self.statusbar.showMessage("[{0}] 서버시간: {1}, 남은시간: {2}".format(f215.get(obj["f215"], "기타"), marketNow, countDown), 5000);

    #체결잔고 이벤트 슬롯
    def addChejanSlot(self, obj):
        if obj["gubun"] == "0" and obj["f919"] == "0":#접수갱신/체결갱신, 거부사유가 0일경우
            self.setRealReg("7000", obj["f9001"]);
            dt = datetime.datetime.now();
            chejan = {
                "chejanTime" : dt.replace(hour=int(obj["f908"][:2]), minute=int(obj["f908"][2:4]), second=int(obj["f908"][-2:])),
                "orderNo"    : obj["f9203"], #주문번호
                "hogaGb"     : obj["f905" ], #주문구분(-매도, +매수, 매수취소, 매도취소, 매도정정, 매수정정)
                "stockCode"  : obj["f9001"], #종목코드
                "stockName"  : obj["f302" ], #종목명
                "nowPrice"   : obj["f10"  ], #현재가
                "orderStatus": obj["f913" ], #주문상태(접수, 체결)
                "orderPrice" : obj["f901" ], #주문가격
                "orderCount" : obj["f900" ], #주문수량
                "chejanCount": obj["f911" ], #체결수량
                "unitPrice"  : obj["f914" ], #단위체결가
                "unitCount"  : obj["f915" ], #단위체결량
                "missCount"  : obj["f902" ], #미체결수량
                "chejanGb"   : obj["f906" ], #매매구분(보통)
                "oriOrderNo" : obj["f904" ], #원주문번호
                "bgCol"      : 1 if obj["f905"] == "+매수" else -1, #매수/매도 배경색 구분
            };
            
            tradeStock = self.calcStock({
                "stockCode"     : chejan["stockCode" ],
                "stockName"     : chejan["stockName" ],
                "averagePrice"  : chejan["unitPrice" ] if chejan["unitPrice"] != "" else chejan["nowPrice"  ],
                "nowPrice"      : chejan["unitPrice" ] if chejan["unitPrice"] != "" else chejan["nowPrice"  ],
                "stockCount"    : chejan["unitCount" ] if chejan["unitCount"] != "" else chejan["orderCount"],
                "reminingCount" : chejan["orderCount"],
            });

            #우선 체결잔고/체결잔고이력 QTableWidget에 넣는다.(단 취소, 정정건은 체결잔고에 넣지 않는다.)
            if not chejan["hogaGb"] in ["매수취소", "매도취소", "매수정정", "매도정정"]:
                #에코 데이터.. 주문정정, 주문취소시.. +매수, -매도 마지막 데이터를 에코형식으로 다시 전송해준다..
                #(현재 주문번호가 chejanHis에 원주문번호에 존재한다면 무시해야함)
                delayEcho = False;#지연된 [-매도, +매수] 수신정보여부
                for chejanHis in self.twChejanHisStocks.getRowDatas():
                    if chejanHis["oriOrderNo"] == chejan["orderNo"]:
                        delayEcho = True;
                        break;
                
                if not delayEcho:
                    chejan["sender"] = "addChejanSlot";
                    self.twChejanStocks.addRows(chejan);
            
            self.twChejanHisStocks.addRows(chejan);

            #매수/매도 처리 후, 수신 데이터에 미체결 수량이 없다면.. 미체결 잔고 QTableWidget에서 해당 행 삭제
            #미체결수량이 없을 경우 매수/매도에 대한 세금을 매수가능금에서 차감
            #나누어서 매도 체결되면.. 각각 매도체결에 대한 수수료와 세금의 금약이 차이난다(수수료 10원 미만 절삭, 수수로 1원 미만 절삭)
            #그래서 분할로 매수될경우에 우선 체결가만 매수가능금          액(-)에 반영 후.. 전량 체결되면..그때 수수료 및 세금을 매수가능금액(-)에 반영한다
            #(분할로 매수될 경우 단위체결가가 다르기 때문에.. 매수 접수된 금액기준으로 계산하여 세금 반영, 때문에 오차가 발생할 수 있다.)
            #ex) 1700원을 10주 매도하는데 1개씩 매도체결될 경우 각각의 수수료와 세금은 없지만.. 매도주문건 전체로 보면.. 17000원에 대한.. 수수료와 세금이 존재한다.
            #    단 매도주문을 1주씩 따로따로 하면.. 수수료와 세금도 각각 개별 주문별로 따로 처리해서 상관없다.. (초당 sendOrder 5건 제한으로... 아쉽...)
            if chejan["hogaGb"] == "매수정정":
                #[+매수] 주문의 수량을 정정한다...(부분체결 진행중이면???)
                chejanStocks = self.twChejanStocks.getRowDatas(chejan["oriOrderNo"]);
                for chejanStock in chejanStocks:
                    chejanStock["orderCount"] = int(chejan["orderCount"]);
                    self.twChejanStocks.addRows(chejanStock);
                
            elif chejan["hogaGb"] == "매도정정":
                #[-매도] 주문의 수량을 정정한다...(부분체결 진행중이면???)
                #보유주식의 현재 주문가능수량을 넘지않게.... 그리고 기존 주문보다 적게 변경한다면 주문가능수량은 보유주식의 주문가능수량에 반영
                chejanStocks = self.twChejanStocks.getRowDatas(chejan["oriOrderNo"]);
                for chejanStock in chejanStocks:
                    myStocks = self.twMyStocks.getRowDatas(chejan["stockCode"]);
                    
                    for myStock in myStocks:
                        myStock["reminingCount"] = myStock["reminingCount"] + (chejanStock["orderCount"] - int(chejan["orderCount"]));
                        self.twMyStocks.addRows(myStock);
                    
                    chejanStock["orderCount"] = int(chejan["orderCount"]);
                    self.twChejanStocks.addRows(chejanStock);
                
            elif chejan["hogaGb"] == "매수취소":
                #원주문번호를 찾아 해당 주문건을 삭제한다.
                self.twChejanStocks.delRows(chejan["oriOrderNo"]);
                isFound = False;
                for c in self.twChejanStocks.getRowDatas():
                    if c["stockCode"] == chejan["stockCode"] and c["orderNo"] != chejan["oriOrderNo"]:
                        isFound = True;
                        break;
                
                if not isFound:
                    self.setRealRemove("7000", chejan["stockCode"]);
            
            elif chejan["hogaGb"] == "매도취소":
                #계좌 보유주식 주문가능수량 업데이트
                #부분 체결이 되었을수도 있기에..  확인해야한다.
                myStocks = self.twMyStocks.getRowDatas(chejan["stockCode"]);

                for myStock in myStocks:
                    #취소주문시 수량을 미체결 수량으로 입력해서 여기에선 주문수량으로 받는다.
                    myStock["reminingCount"] += int(chejan["orderCount"]);

                self.twMyStocks.addRows(myStock);
                
                #원주문번호를 찾아 해당 주문건을 삭제한다.
                self.twChejanStocks.delRows(chejan["oriOrderNo"]);
                isFound = False;
                for c in self.twChejanStocks.getRowDatas():
                    if c["stockCode"] == chejan["stockCode"] and c["orderNo"] != chejan["oriOrderNo"]:
                        isFound = True;
                        break;
                
                if not isFound:
                    self.setRealRemove("7000", chejan["stockCode"]);
        
            elif chejan["orderStatus"] == "체결":
                accountInfo = self.gbMyAccount.getAccountInfo();

                if chejan["hogaGb"] == "+매수":#매수(체결)가 이상없이 체결되었다면 매수가능금액(-) 업데이트
                    self.gbMyAccount.setAccountInfo({
                        "vOrderableAmount": accountInfo["vOrderableAmount"] - tradeStock["buyAmount"],#매수수수료를 더한 매수금액을 매수가능금액에서 차감
                    });

                    if chejan["missCount"] == "0":#미체결수량
                        self.twChejanStocks.delRows(chejan["orderNo"]);

                        isFound = False;
                        for c in self.twChejanStocks.getRowDatas():
                            if c["stockCode"] == chejan["stockCode"] and c["orderNo"] != chejan["orderNo"]:
                                isFound = True;
                                break;
                        
                        if not isFound:
                            self.setRealRemove("7000", chejan["stockCode"]);
                
                elif chejan["hogaGb"] == "-매도":
                    self.gbMyAccount.setAccountInfo({
                        "vTodayBuyAmount" : accountInfo["vTodayBuyAmount" ] + tradeStock["buyAmount"],#매도가 발생할경우에만 당일수익율을 계산한다.
                        "vTodayNowAmount" : accountInfo["vTodayNowAmount" ] + tradeStock["nowAmount"],#매도가 발생할경우에만 당일수익율을 계산한다.
                        "vOrderableAmount": accountInfo["vOrderableAmount"] + tradeStock["nowAmount"],#매도수수료, 세금을 제한 금액을 매수가능금액에서 증감
                    });

                    myStocks = self.twMyStocks.getRowDatas(chejan["stockCode"]);
                    for myStock in myStocks:
                        if chejan["missCount"] != "0":
                            #미체결수량이 있다면
                            myStock["stockCount"] = myStock["stockCount"] - int(chejan["unitCount"]);#현재수량 - 단위체결량
                            myStock["nowPrice"  ] =  chejan["nowPrice"  ];#현재가
                            myStock = self.calcStock(myStock);
                            self.twMyStocks.addRows(myStock);
                        else:
                            #잔고수량 - 체결수량 == 0이라면.. 계좌 삭제 아니라면 업데이트 
                            reminingCount = myStock["stockCount"] - int(chejan["unitCount"]);
                            if reminingCount == 0:
                                self.twMyStocks.delRows(chejan["stockCode"]);
                                self.setRealRemove("4000", chejan["stockCode"]);

                                #계좌잔고가 남아 있지 않다면 전략에서도 삭제
                                if chejan["stockCode"] in self.appSettings.myStrategy:
                                    del(self.appSettings.myStrategy[chejan["stockCode"]]);
                                    self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
                                    #self.appSettings.sync();
                            else:
                                myStock["stockCount"] = reminingCount;
                                self.twMyStocks.addRows(self.calcStock(myStock));
                    
                    if chejan["missCount"] == "0":#미체결수량
                        self.twChejanStocks.delRows(chejan["orderNo"]);
                        
                        isFound = False;
                        for c in self.twChejanStocks.getRowDatas():
                            if c["stockCode"] == chejan["stockCode"] and c["orderNo"] != chejan["orderNo"]:
                                isFound = True;
                                break;
                        
                        if not isFound:
                            self.setRealRemove("7000", chejan["stockCode"]);
                
            #테스트를 위한 로그기록
            testLogFile(chejan, tradeStock, self.gbMyAccount.vOrderableAmount.text());
        
        elif obj["gubun"] == "1":#잔고갱신
            #gubun=0 접수만 되었는데도.. 왜 잔고가 현재정보로 날라옴
            #[매수]에 대한 잔고정보는 여기서 처리함.(체결에서는 단위체결량, 단위체결가가있어 세금&수수료 계산 및 매수가능금액만 업데이트)
            #[매도]에 대한 잔고정보가 와도.. 단위체결량, 단위체결가가 존재하지 않아.. 처리하기 어려움.. 차라리 체결정보에서 처리
            if obj["f946"] == "2":#매수
                myStock = self.calcStock({
                    "stockCode"     : obj["f9001"],#종목코드
                    "stockName"     : obj["f302" ],#종목명
                    "averagePrice"  : obj["f931" ],#매입단가
                    "nowPrice"      : obj["f10"  ],#현재가
                    "stockCount"    : obj["f930" ],#보유수량
                    "reminingCount" : obj["f933" ],#주문가능수량
                });

                if self.twMyStocks.isExist(obj["f9001"]) == None:
                    #신규매수항목임
                    self.appSettings.orderList.add((myStock["stockCode"], myStock["stockName"]));
                    self.appSettings.setValue("orderList", self.appSettings.orderList);
                    #속도가 너무느리다
                    #self.appSettings.sync();
                
                self.twMyStocks.addRows([myStock]);
                self.setRealReg("4000", myStock["stockCode"]);
    
    #매매주식 세금계산
    def calcStock(self, stockInfo):
        buyAmount      = float(stockInfo["averagePrice"]) * float(stockInfo["stockCount"]);
        nowAmount      = float(stockInfo["nowPrice"])     * float(stockInfo["stockCount"]);
        #매입수수료 = int(averagePrice[평균단가] * stockCount[mField03] * 0.0035 / 10, 1) * 10, 단 실서버는 0.00015
        #매도수수료 = int(nowPrice[현재가]       * stockCount[mField03] * 0.0035 / 10, 1) * 10, 단 실서버는 0.00015
        #세금       = int(nowPrice[현재가]       * stockCount[mField03] * 0.002 , 1)
        buyTax         = int(buyAmount * self.buyTaxRate / 10) * 10;
        sellTax        = int(nowAmount * self.sellTaxRate / 10) * 10;
        tax            = int(nowAmount * self.taxRate);

        #매입금액     = 평균단가[averagePrice] * 보유량[stockCount] + 매수수수료
        #매도평가금액 = 현재가[nowPrice]       * 보유량[stockCount] - (매도수수료 + 세금)
        #손익분기가   = 평균단가[averagePrice] + (세금합계 / 보유량[stockCount])
        #손익금액     = 평가금액[nowAmount] - 매입금액[buyAmount]
        #손익율       = (평가금액[nowAmount] - 매입금액[buyAmount]) / 매입금액[buyAmount] * 100
        buyAmount      = buyAmount + buyTax;
        nowAmount      = nowAmount - sellTax - tax;
        breakEvenPrice = float(stockInfo["averagePrice"]) + int((buyTax + sellTax + tax) / int(stockInfo["stockCount"]));
        profit         = nowAmount - buyAmount;
        profitRate     = round((nowAmount - buyAmount) / buyAmount * 100, 2);
        
        return {
            "stockCode"     : stockInfo["stockCode"][-6:],
            "stockName"     : stockInfo["stockName"],
            "averagePrice"  : int(float(stockInfo["averagePrice"])),
            "nowPrice"      : stockInfo["nowPrice" ],
            "breakEvenPrice": int(breakEvenPrice),
            "profit"        : profit,
            "profitRate"    : profitRate,
            "buyAmount"     : buyAmount,
            "nowAmount"     : nowAmount,
            "totalTax"      : (buyTax + sellTax + tax),
            "buyTax"        : buyTax,
            "sellTax"       : sellTax,
            "tax"           : tax,
            "stockCount"    : stockInfo["stockCount"   ],
            "reminingCount" : stockInfo["reminingCount"],
        };

    #배치 실행버튼 슬롯
    def btnRunSlot(self):
        if self.myStrategy.isRun:
            #자동매매가 실행중일 경우
            reply = QtWidgets.QMessageBox.question(self, "확인", "자동매매가 진행중입니다 정지하시겠습니까?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No);

            if reply == QtWidgets.QMessageBox.Yes:
                self.gbMyAccount.uValue1.setEnabled(True);
                self.cbConUp.setEnabled(True);
                self.btnReload.setEnabled(True);

                self.myStrategy.isRun = False;
                self.btnRun.setStyleSheet("QPushButton {background-color: green; color: white;}");
                self.btnRun.setText("정지(&F8)" if self.myStrategy.isRun else "실행(&F8)");
                self.btnRun.setShortcut("F8");

                self.sendConditionStop("8000", self.cbConUp.currentText(), self.cbConUp.currentData());
                self.setRealClear("8000");
                self.myStrategy.conStrategy.clear();
                asyncio.run(self.sendMessage("#{0}\r\n<strong>자동매매</strong>가 중지되었습니다.".format(datetime.datetime.now())));
        else:
            #자동매매가 정지중일 경우
            if self.gbMyAccount.uValue1.currentData() == "":
                QtWidgets.QMessageBox.warning(self, "경고", self.getErrMsg(-10000));
            elif self.cbConUp.currentData() == "":
                QtWidgets.QMessageBox.warning(self, "경고", self.getErrMsg(-10001));
            else:
                #조건 검색 항목은 자동으로 요청 화면번호에 실시간 수신에 등록된다.
                conList = self.sendCondition("8000", self.cbConUp.currentText(), self.cbConUp.currentData());
                
                if conList != None:#Condition 1분이내 연속 조회시 응답 오류가 발생한다.(1분내 1회 호출 규칙)
                    self.gbMyAccount.uValue1.setEnabled(False);
                    self.cbConUp.setEnabled(False);
                    self.btnReload.setEnabled(False);

                    self.myStrategy.isRun = True;
                    self.btnRun.setText("정지(&F8)" if self.myStrategy.isRun else "실행(&F8)");
                    self.btnRun.setStyleSheet("QPushButton {background-color: red; color: white;}");
                    self.btnRun.setShortcut("F8");
                    
                    if len(conList) > 0:
                        conResult = self.reqCommKwRqData({
                            "codeList": ";".join(conList),
                            "codeCnt" : len(conList),
                            "sRQName" : "조건검색결과",
                            "sScrNo"  : "8000",
                            "output"  : Optkwfid(),
                        });

                        addRows = [];
                        for row in conResult:
                            addRows.append({
                                "stockCode"    : row["sField01"],
                                "stockName"    : row["sField02"],
                                "nowPrice"     : row["sField03"],
                                "stdPrice"     : row["sField04"],
                                "diffPrice"    : row["sField05"],
                                "changeRate"   : row["sField07"],
                                "tradeCount"   : row["sField08"],
                                "tradeStrength": row["sField11"],
                            });
                    
                        self.twConStocks.addRows(addRows);
                    asyncio.run(self.sendMessage("#{0}\r\n<strong>자동매매</strong>가 시작되었습니다.".format(datetime.datetime.now())));
                else:
                    QtWidgets.QMessageBox.warning(self, "경고", self.getErrMsg(-10002));
        
        self.resizeEvent();

    #로그인 버튼 처리 이벤트 슬롯
    def actLoginSlot(self, event=None):
        self.actLogin.setEnabled(False);
        self.login();

    #조건검색 재조회 이벤트 슬롯
    def loadConditionsSlot(self):
        conditions = self.getConditionLoad();
        self.twConStocks.setRowCount(0);
        self.setRealClear("8000");

        self.cbConUp.clear();
        self.cbConUp.addItem("--조건식을 선택해주세요--", "");
        for key, value in conditions:
            self.cbConUp.addItem(value, key);
    
    #계좌요약정보 업데이트
    def updateSummary(self):
        totalBuyAmount = 0;
        totalNowAmount = 0;

        myStockDataList = self.twMyStocks.getRowDatas();
        for myStockData in myStockDataList:
            totalBuyAmount += myStockData.get("buyAmount", 0);
            totalNowAmount += myStockData.get("nowAmount", 0);
        
        self.gbMyAccount.setAccountInfo({
            "vTotalBuyAmount" : totalBuyAmount,
            "vTotalNowAmount" : totalNowAmount,
        });

        vTotalProfit     = totalNowAmount - totalBuyAmount;
        vTotalProfitRate = vTotalProfit / totalBuyAmount * 100;

        #계좌 당일 손실/수익종료, 당일청산 설정에 따른 자동매매 종료
        if (self.appSettings.vAccountPlusEndActive  and self.gbMyAccount.vTodayProfitRate >= self.appSettings.vAccountPlusEnd ) or \
            (self.appSettings.vAccountMinusEndActive and self.gbMyAccount.vTodayProfitRate <= self.appSettings.vAccountMinusEnd) or \
            (self.appSettings.vDayClearActive        and self.appSettings.vRunEndTime.toString("hhmm") < datetime.datetime.now().strftime("%H%M")):
            
            self.gbMyAccount.uValue1.setEnabled(True);
            self.cbConUp.setEnabled(True);
            self.btnReload.setEnabled(True);

            self.myStrategy.isRun = False;
            self.btnRun.setStyleSheet("QPushButton {background-color: green; color: white;}");
            self.btnRun.setText("정지(&F8)" if self.myStrategy.isRun else "실행(&F8)");
            self.btnRun.setShortcut("F8");

            self.sendConditionStop("8000", self.cbConUp.currentText(), self.cbConUp.currentData());
            self.setRealClear("8000");
            self.myStrategy.conStrategy.clear();

            #계좌를 전부 매도 후 종료할지는.. 고민...
            self.myStrategy.stockSellAll();

            if vTotalProfitRate >= self.appSettings.vAccountPlusEnd:
                QtWidgets.QMessageBox.about(self, "계좌", "계좌 수익율에 도달하여 자동매매를 종료합니다.");
            elif vTotalProfitRate <= self.appSettings.vAccountMinusEnd:
                QtWidgets.QMitemsessageBox.about(self, "계좌", "계좌 손실율에 도달하여 자동매매를 종료합니다.");
            else:
                QtWidgets.QMessageBox.about(self, "계좌", "당일 청산 자동매매를 종료합니다.");
    
    #조건검색 항목 편입/탈락 처리
    def conInOutSlot(self, obj):
        if obj["type"] == "D":#종목이탈
            #분석을 위해 계속 검색된 항목은 계속 수신받기 때문에 삭제할 필요가 없음
            #self.twConStocks.delRows(obj["stockCode"]);#실시간 수신 해지는 KiwoomAPI에서 처리함
            pass;
    
    #처리내역 & 상태바에 프로그램 메세지를 출력
    def addConsoleSlot(self, obj):
        if obj.get("sScrNo", "") == "":
            obj["sScrNo"] = "0000";
        
        if obj.get("sRQName", "") == "":
            obj["sRQName"] = "기타";
        
        msg  = "{0}:" .format(datetime.datetime.now());
        msg += ", {0}".format(self.preFormat(obj["sRQName"] if obj["sRQName"] != "" else obj["sTrCode"], 30, "<"));
        msg += ", {0}".format(obj["sMsg"]);
        
        self.tbConsole.append(msg);
        self.statusbar.showMessage(msg, 5000);
    
    #Splitter 크기 조절 이벤트 슬롯
    def setSplitterSlot(self, mode):
        self.splitter.setSizes([0 if mode == "my" else 1, 0 if mode == "con" else 1]);
        
    #조건검색 변경시 발생 이벤트 슬롯
    def conditionChangeSlot(self, index):
        self.setRealClear("8000");
        self.twConStocks.setRowCount(0);
    
    #전체 그리드 초기화
    def tableWidgetClear(self):
        self.twConStocks.setRowCount(0);
        self.twMyStocks.setRowCount(0);
        self.twChejanStocks.setRowCount(0);
        self.twChejanHisStocks.setRowCount(0);
    
    #QWidget 기본 함수(Window창의 [X]버튼을 클릭하여 창이 닫히는 경우)
    def closeEvent(self, event):
        try:
            if self.myStrategy.isRun:
                reply = QtWidgets.QMessageBox.question(self, "확인", "자동매매가 진행중입니다 종료하시겠습니까?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No);

                if reply == QtWidgets.QMessageBox.Yes:
                    #속도가 너무 느려.. 종료시에만 저장하도록 수정
                    self.appSettings.sync();
                    telegramMsg  = "#{0}\r\n".format(datetime.datetime.now());
                    telegramMsg += "<strong>자동매매</strong>가 종료되었습니다.\r\n".format(datetime.datetime.now());
                    telegramMsg += "<strong>수익보고</strong>\r\n";
                    telegramMsg += "-계좌:{0}\r\n".format(self.gbMyAccount.vTotalProfit.text());
                    telegramMsg += "-당일:{0}".format(self.gbMyAccount.vTodayProfit.text());
                    asyncio.run(self.sendMessage(telegramMsg));
                    self.close();
                else:
                    event.ignore();
            else:
                #속도가 너무 느려.. 종료시에만 저장하도록 수정
                self.appSettings.sync();
                telegramMsg  = "#{0}\r\n".format(datetime.datetime.now());
                telegramMsg += "<strong>자동매매</strong>가 종료되었습니다.\r\n".format(datetime.datetime.now());
                telegramMsg += "<strong>수익보고</strong>\r\n";
                telegramMsg += "-계좌:{0}\r\n".format(self.gbMyAccount.vTotalProfit.text());
                telegramMsg += "-당일:{0}".format(self.gbMyAccount.vTodayProfit.text());
                asyncio.run(self.sendMessage(telegramMsg));
                self.close();
        except Exception as e:
            print(e);
    
    #Gird Column 재조정을 위한 이벤트(scroll 표시여부에 따라.. 40px차이가 발생함)
    def resizeEvent(self, event=None):
        tableWidgets = [self.twConStocks, self.twMyStocks, self.twChejanStocks, self.twChejanHisStocks];
        for idx, tbWidget in enumerate(tableWidgets):
            header     = tbWidget.horizontalHeader();
            headerSize = header.width() - (40 if tbWidget.verticalScrollBar().width() == 100 else 0);
            hideCols   = [x for x in range(header.count()) if tbWidget.isColumnHidden(x) == True];
            allColSize = 0;

            for column in range(header.count()):
                if tbWidget.isColumnHidden(column) != True:
                    allColSize += header.sectionSize(column);
            
            if allColSize < headerSize:
                colSize = max(header.defaultSectionSize(), headerSize / (header.count() - len(hideCols)));
                for column in range(header.count()):
                    header.resizeSection(column, int(colSize));
            
            tbWidget.horizontalScrollBar().setValue(0);
            
#오류처리 로그 기록
def catch_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("myLogging");
    logger.error("Unexpected exception.", exc_info=(exc_type, exc_value, exc_traceback));
    sys.__excepthook__(exc_type, exc_value, exc_traceback);
    sys.exit(-1);

sys.excepthook = catch_exception;# sys.excepthook을 대체합니다.

#테스트를 위한 로그기록
def testLogFile(obj, ext={}, vOrderableAmount=""):
    if type(obj) == Opt10075:
        with open("logging/" + datetime.datetime.now().strftime("%Y%m%d") + "/chejanHis_" + datetime.datetime.now().strftime("%Y%m%d") + ".log", "w", encoding="UTF-8", ) as fileData:
            for index, value in enumerate(obj.__getitem__("mField15")):
                writeText  = "계좌번호({0})"        .format(Main.preFormat("", obj.__getitem__("mField01")[index], 10, ">"));#계좌번호
                writeText += ", 주문번호({0})"      .format(Main.preFormat("", obj.__getitem__("mField02")[index],  7, ">"));#주문번호
                writeText += ", 관리사번({0})"      .format(Main.preFormat("", obj.__getitem__("mField03")[index],  7, ">"));#관리사번
                writeText += ", 종목코드({0})"      .format(Main.preFormat("", obj.__getitem__("mField04")[index],  6, ">"));#종목코드
                writeText += ", 업무구분({0})"      .format(Main.preFormat("", obj.__getitem__("mField05")[index],  7, ">"));#업무구분
                writeText += ", 주문상태({0})"      .format(Main.preFormat("", obj.__getitem__("mField06")[index],  7, ">"));#주문상태
                writeText += ", 종목명({0})"        .format(Main.preFormat("", obj.__getitem__("mField07")[index], 30, "<"));#종목명
                writeText += ", 주문수량({0})"      .format(Main.preFormat("", obj.__getitem__("mField08")[index],  7, ">"));#주문수량
                writeText += ", 주문가격({0})"      .format(Main.preFormat("", obj.__getitem__("mField09")[index],  7, ">"));#주문가격
                writeText += ", 미체결수량({0})"    .format(Main.preFormat("", obj.__getitem__("mField10")[index],  7, ">"));#미체결수량
                writeText += ", 체결누계금액({0})"  .format(Main.preFormat("", obj.__getitem__("mField11")[index],  7, ">"));#체결누계금액
                writeText += ", 원주문번호({0})"    .format(Main.preFormat("", obj.__getitem__("mField12")[index],  7, ">"));#원주문번호
                writeText += ", 주문구분({0})"      .format(Main.preFormat("", obj.__getitem__("mField13")[index],  8, ">"));#주문구분
                writeText += ", 매매구분({0})"      .format(Main.preFormat("", obj.__getitem__("mField14")[index],  7, ">"));#매매구분
                writeText += ", 시간({0})"          .format(Main.preFormat("", obj.__getitem__("mField15")[index],  7, ">"));#시간
                writeText += ", 체결번호({0})"      .format(Main.preFormat("", obj.__getitem__("mField16")[index],  7, ">"));#체결번호
                writeText += ", 체결가({0})"        .format(Main.preFormat("", obj.__getitem__("mField17")[index],  7, ">"));#체결가
                writeText += ", 체결량({0})"        .format(Main.preFormat("", obj.__getitem__("mField18")[index],  7, ">"));#체결량
                writeText += ", 현재가({0})"        .format(Main.preFormat("", obj.__getitem__("mField19")[index],  7, ">"));#현재가
                writeText += ", 매도호가({0})"      .format(Main.preFormat("", obj.__getitem__("mField20")[index],  7, ">"));#매도호가
                writeText += ", 매수호가({0})"      .format(Main.preFormat("", obj.__getitem__("mField21")[index],  7, ">"));#매수호가
                writeText += ", 단위체결가({0})"    .format(Main.preFormat("", obj.__getitem__("mField22")[index],  7, ">"));#단위체결가
                writeText += ", 단위체결량({0})"    .format(Main.preFormat("", obj.__getitem__("mField23")[index],  7, ">"));#단위체결량
                writeText += ", 당일매매수수료({0})".format(Main.preFormat("", obj.__getitem__("mField24")[index],  7, ">"));#당일매매수수료
                writeText += ", 당일매매세금({0})"  .format(Main.preFormat("", obj.__getitem__("mField25")[index],  7, ">"));#당일매매세금
                writeText += ", 개인투자자({0})"    .format(Main.preFormat("", obj.__getitem__("mField26")[index],  7, ">"));#개인투자자
                fileData.writelines(writeText + "\n");
    elif type(obj) == Opt10077:
        with open("logging/" + datetime.datetime.now().strftime("%Y%m%d") + "/trade_" + datetime.datetime.now().strftime("%Y%m%d") + ".log", "w", encoding="UTF-8", ) as fileData:
            for index, value in enumerate(obj.__getitem__("mField05")):
                writeText  = "종목코드({0})"        .format(Main.preFormat("", obj.__getitem__("mField09")[index][-6:],  6, ">"));#종목코드
                writeText += ", 종목명({0})"        .format(Main.preFormat("", obj.__getitem__("mField01")[index]     , 30, "<"));#종목명
                writeText += ", 매입단가({0})"      .format(Main.preFormat("", obj.__getitem__("mField03")[index]     ,  7, ">"));#매입단가
                writeText += ", 체결가({0})"        .format(Main.preFormat("", obj.__getitem__("mField04")[index]     ,  7, ">"));#체결가
                writeText += ", 체결량({0})"        .format(Main.preFormat("", obj.__getitem__("mField02")[index]     ,  7, ">"));#체결량
                writeText += ", 당일매도손익({0})"  .format(Main.preFormat("", value                                  ,  7, ">"));#당일매도손익
                writeText += ", 당일매매수수료({0})".format(Main.preFormat("", obj.__getitem__("mField07")[index]     ,  7, ">"));#당일매매수수료
                writeText += ", 당일매매세금({0})"  .format(Main.preFormat("", obj.__getitem__("mField08")[index]     ,  7, ">"));#당일매매세금
                fileData.writelines(writeText + "\n");
    else:
        with open("logging/" + datetime.datetime.now().strftime("%Y%m%d") + "/order/buySellPrice.log", "a", encoding="UTF-8", ) as fileData:
            writeText =  "[{0}:{1}]"          .format(datetime.datetime.now(), "buySellPrice");
            writeText += ", 주문번호({0})"    .format(Main.preFormat("", obj["orderNo"    ],  7, "<"));
            writeText += ", 종목명({0})"      .format(Main.preFormat("", obj["stockName"  ], 20, "<"));
            writeText += ", 종목코드({0})"    .format(Main.preFormat("", obj["stockCode"  ],  6, ">"));
            writeText += ", 매매구분({0})"    .format(Main.preFormat("", obj["hogaGb"     ],  3, ">"));
            writeText += ", 주문가격({0})"    .format(Main.preFormat("", obj["orderPrice" ],  7, ">"));
            writeText += ", 주문수량({0})"    .format(Main.preFormat("", obj["orderCount" ],  7, ">"));
            writeText += ", 체결수량({0})"    .format(Main.preFormat("", obj["chejanCount"],  3, ">"));
            writeText += ", 단위체결가({0})"  .format(Main.preFormat("", obj["unitPrice"  ],  7, ">"));
            writeText += ", 단위체결량({0})"  .format(Main.preFormat("", obj["unitCount"  ],  7, ">"));
            
            if obj["hogaGb"] == "+매수":
                writeText += ", 수수료({0})"      .format(Main.preFormat("", ext["buyTax" ]  , 7, ">"));
                writeText += ", 세금({0})"        .format(Main.preFormat("", ""              , 3, ">"));
                writeText += ", 총금액({0})"      .format(Main.preFormat("", ext["buyAmount"], 7, ">"));
                writeText += ", 매수가능금액({0})".format(Main.preFormat("", vOrderableAmount, 7, ">"));
            elif obj["hogaGb"] == "-매도":
                writeText += ", 수수료({0})"      .format(Main.preFormat("", ext["sellTax"]  , 7, ">"));
                writeText += ", 세금({0})"        .format(Main.preFormat("", ext["tax"    ]  , 3, ">"));
                writeText += ", 총금액({0})"      .format(Main.preFormat("", ext["nowAmount"], 7, ">"));
                writeText += ", 매수가능금액({0})".format(Main.preFormat("", vOrderableAmount, 7, ">"));
            else:
                writeText += ", 매수가능금액({0})".format(Main.preFormat("", vOrderableAmount, 7, ">"));
            
            fileData.writelines(writeText + "\n");

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.myproduct.subproduct.version");#임의의 명칭을 사용해도 됨
    os.environ["QT_FONT_DPI"] = "97";
    app = QtWidgets.QApplication(sys.argv);
    app.setWindowIcon(QtGui.QIcon(resource_path("resources/iconTrading.png")));

    argv   = sys.argv[1:];
    kwargs = {kw[0] : kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=') > 0]};
    args   = [arg for arg in argv if arg.find('=') < 0];

    try:
        main = Main(*args, **kwargs);
        main.show();
        sys.exit(app.exec_());
            
    except NotInsallOpenAPI as notIns:
        QtWidgets.QMessageBox.warning(None, "경고", notIns.message);
    except Exception as e:
        traceback.print_exc();