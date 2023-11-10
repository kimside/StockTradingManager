import sys, os, pprint;

from PyQt5               import uic, QtWidgets, QtCore, QtGui;

def resource_path(relative_path):
    try:# PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.abspath(".");
    return os.path.join(base_path, relative_path);

class ModalInformation(QtWidgets.QDialog, uic.loadUiType(resource_path("modules/setting/ModalInformation.ui"))[0]):
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self);
        self.parent = parent;
        self.appSettings = self.parent.appSettings;
        self.setWindowFlags(QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint);

        self.tableWidgetClear();
        self.initTableWidget();

        self.btnClear.clicked.connect(self.btnClearSlot);
        self.btnClose.clicked.connect(self.close);
    
    def initTableWidget(self):
        self.twReOrderStocks.initWidget([
            {"id": "stockCode", "name": "종목코드", "type": str, "isKey" : True},
            {"id": "stockName", "name": "종목명"  , "type": str},
            {"id": "btnDel"   , "name": "삭제"    , "type": QtWidgets.QPushButton, "slot": self.delReOrder},
        ]);
        
        #현재가, TrailingStop 보존가, 다음분할매도가, 다음분할매수가
        self.twMyStrategyStocks.initWidget([
            {"id": "stockCode"     , "name": "종목코드"        , "type": str, "isKey" : True},
            {"id": "stockName"     , "name": "종목명"          , "type": str},
            {"id": "nowPrice"      , "name": "현재가"          , "type": int},
            {"id": "averagePrice"  , "name": "매입단가"        , "type": int},
            {"id": "tsActive"      , "name": "[TS]활성여부"    , "type": bool, "align": QtCore.Qt.AlignCenter},
            {"id": "tsHighPrice"   , "name": "[TS]최고가"      , "type": int},
            {"id": "tsServePrice"  , "name": "[TS]이익보존가"  , "type": int},
            {"id": "tsDivSell"     , "name": "[TS]분할매도(회)", "type": int},
            {"id": "tsDivSellPrice", "name": "[TS]다음매도가"  , "type": int},
            {"id": "tsAddBuy"      , "name": "[TS]분할매수(회)", "type": int},
            {"id": "tsAddBuyPrice" , "name": "[TS]다음매수가"  , "type": int},
            {"id": "slAddBuy"      , "name": "[SL]분할매수(회)", "type": int},
            {"id": "slAddBuyPrice" , "name": "[SL]다음매수가"  , "type": int},
            {"id": "bgCol"         , "name": "배경색"          , "type": int, "isBg": True, "isVisible": False},
        ]);

    #재매수금지 삭제버튼 슬롯
    def delReOrder(self, key):
        datas = self.twReOrderStocks.getRowDatas(key);
        for data in datas:
            self.appSettings.orderList.remove((data["stockCode"], data["stockName"]));
        self.twReOrderStocks.delRows(key);
    
    #모달창 Show 이벤트
    def showEvent(self, event):
        self.tableWidgetClear();
        
        for (stockCode, stockName) in self.appSettings.orderList:
            self.twReOrderStocks.addRows({
                "stockCode": stockCode,
                "stockName": stockName,
            });
        
        currentTab     = self.appSettings.currentTab;
        tsProfit       = self.appSettings.vtsTargetProfit;
        tsLoss         = self.appSettings.vtsTargetLoss;
        tsDivBuyActive = self.appSettings.vtsTouchDivideBuyActive;
        tsDivProfit    = self.appSettings.vtsTouchDivideProfit;
        tsServeRate    = self.appSettings.vtsTouchDivideServeRate;

        slDivBuyActive = self.appSettings.vslTouchDivideBuyActive;
        slLoss         = self.appSettings.vslTargetLoss;

        for key, myStrategy in list(self.appSettings.myStrategy.items()):
            tsAddBuy       = myStrategy["tsAddBuy" ] + 1;
            tsDivSell      = myStrategy["tsDivSell"] + 1;
            slAddBuy       = myStrategy["slAddBuy" ] + 1;

            tsServePrice   = 0;
            tsDivSellPrice = 0;
            tsAddBuyPrice  = 0;
            slAddBuyPrice  = 0;
            bgCol          = 0;

            if currentTab == 0:
                if myStrategy["tsActive"]:
                    bgCol = 1;
                    tsServePrice   = myStrategy["averagePrice"] + (myStrategy["tsHighPrice"] - myStrategy["averagePrice"]) * tsServeRate / 100;
                    tsDivSellPrice = myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (tsProfit + (tsDivSell * tsDivProfit)) / 100);
                
                if tsDivBuyActive and not myStrategy["tsActive"]:
                    tsAddBuyPrice = myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (tsLoss + (tsAddBuy * tsLoss)) / 100);

                    if myStrategy["tsAddBuy"] > 0 and bgCol == 0:
                        bgCol = -1
            else:
                if slDivBuyActive:
                    slAddBuyPrice = myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (slLoss * (slAddBuy + 1)) / 100);

                    if myStrategy["slAddBuy"] > 0 and bgCol == 0:
                        bgCol = -1
            
            myStrategy["bgCol"         ] = bgCol;
            myStrategy["tsServePrice"  ] = tsServePrice;
            myStrategy["tsAddBuyPrice" ] = tsAddBuyPrice;
            myStrategy["tsDivSellPrice"] = tsDivSellPrice;
            myStrategy["slAddBuyPrice" ] = slAddBuyPrice ;
            self.twMyStrategyStocks.addRows(myStrategy);

        if currentTab == 0:
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsActive"      ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsHighPrice"   ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsServePrice"  ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsDivSell"     ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsDivSellPrice"), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsAddBuy"      ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsAddBuyPrice" ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("slAddBuy"      ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("slAddBuyPrice" ),  True);
        else:
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsActive"      ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsHighPrice"   ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsServePrice"  ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsDivSell"     ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsDivSellPrice"),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsAddBuy"      ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("tsAddBuyPrice" ),  True);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("slAddBuy"      ), False);
            self.twMyStrategyStocks.setColumnHidden(self.twMyStrategyStocks.getColumnIdx("slAddBuyPrice" ), False);

        #self.resizeEvent();
    
    def updateNowPrice(self, stock):
        for row in self.twMyStrategyStocks.getRowDatas(stock["stockCode"]):
            row["nowPrice"    ] = stock["nowPrice"    ];
            row["averagePrice"] = stock["averagePrice"];
            self.twMyStrategyStocks.addRows(row);
    
    #재매수금지목록 초기화 이벤트 슬롯
    def btnClearSlot(self):
        reply = QtWidgets.QMessageBox.question(self, "재매수금지 목록 초기화", "재매수금지 목록은 즉시 반영됩니다,\r\n재매수금지 항목을 초기화 하시겠습니까?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No);

        if reply == QtWidgets.QMessageBox.Yes:
            self.twReOrderStocks.setRowCount(0);
            self.appSettings.orderList.clear();
            QtWidgets.QMessageBox.about(self, "재매수금지 목록 초기화", "재매수금지 목록이 초기화 되었습니다");
    
    #전체 그리드 초기화
    def tableWidgetClear(self):
        self.twReOrderStocks.setRowCount(0);
        self.twMyStrategyStocks.setRowCount(0);
    
    #Gird Column 재조정을 위한 이벤트(scroll 표시여부에 따라.. 40px차이가 발생함)
    def resizeEvent(self, event=None):
        tableWidgets = [self.twReOrderStocks, self.twMyStrategyStocks];

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