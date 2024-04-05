import datetime, time;

from PyQt5 import QtCore;
from modules.strategy.AbstractStrategy import AbstractStrategy;

#1. 조건검색으로 검색된 항목을 이탈시키지 않고.. 계속 모니터링하면서..
#   내부적 로직의 특정 조건에 만족되면.. 매수신청
#2. 손익율이 -10%되면.. 지정금액 or 비율로 추가매수 실행
#3. 시장의 상황에 따라 실행하는 조건식을 선택(매수/투자비율 조정? 현금확보?)

class InfiniteStrategy(AbstractStrategy):
    def __init__(self, parent=None):
        self.isRun = False;
        self.parent = parent;
        self.appSettings = self.parent.appSettings;
        self.myStrategy  = self.appSettings.myStrategy;
        self.monentSize  = 150;
        self.datetime    = datetime.datetime;
        self.buyTaxRate  = self.parent.buyTaxRate; #매수 수수료
        
        self.startTime     = self.appSettings.vRunStartTime.toString("hhmm"); #자동매매 시작시간
        self.endTime       = self.appSettings.vRunEndTime.toString("hhmm");   #자동매매 종료시간
        self.tradeMaxCount = self.appSettings.vTradeMaxCount;                 #자동매매 거래 종목 갯수 제한
        self.buyRateActive = self.appSettings.vBuyRate;                       #매수 비율/금액지정 여부(True: 비율, False:금액지정)
        self.buyRate       = self.appSettings.vBuyRateValue;                  #매수 매수가능금액 대비 지정비율
        self.buyAmount     = self.appSettings.vBuyAmountValue;                #매수 지정금액
        self.currentTab    = self.appSettings.currentTab;                     #TrailingStop/StopLoss 활성화 탭(0:TrailingStop, 1:StopLoss)

        self.tsProfitRate    = self.appSettings.vtsTargetProfit;         #TrailingStop 목표수익율
        self.tsLossRate      = self.appSettings.vtsTargetLoss;           #TrailingStop 목표손실율
        self.tsDivBuyActive  = self.appSettings.vtsTouchDivideBuyActive; #TrailingStop 추가매수 활성화 여부
        self.tsDivBuyCount   = self.appSettings.vtsTouchDivideBuy;       #TrailingStop 추가매수 횟수
        self.tsDivProfitRate = self.appSettings.vtsTouchDivideProfit;    #TrailingStop 목표수익율 달성 후 분할매도 추가수익율
        self.tsDivRate       = self.appSettings.vtsTouchDivideRate;      #TrailingStop 목표수익율 달성 후 분할매도 비율
        self.tsServeRate     = self.appSettings.vtsTouchDivideServeRate; #TrailingStop 목표수익율 달성 후 보존수익율
        
        self.slProfit       = self.appSettings.vslTargetProfit;          #StopLoss 목표수익율
        self.slLossRate     = self.appSettings.vslTargetLoss;            #StopLoss 목표손실율
        self.slDivBuyActive = self.appSettings.vslTouchDivideBuyActive;  #StopLoss 추가매수 활성화 여부
        self.slDivBuyCount  = self.appSettings.vslTouchDivideBuy;        #StopLoss 추가매수 횟수

        #조건검색 결과 전략분석
        self.conStrategy = {};
        #보유주식 계좌 전략분석
    
    #매수전략
    def buyStrategy(self, obj):
        dt          = self.datetime.now();
        hhmm        = "{0:02d}{1:02d}".format(dt.hour, dt.minute);
        isTradeTime = (hhmm >= self.startTime and hhmm <= self.endTime);
        
        if self.isRun and isTradeTime:
            if obj["f9001"] in self.conStrategy:
                thisStrategy = self.conStrategy[obj["f9001"]];
            
                #재매수금지 대상에 포함되지 않음
                #매수최대갯수를 넘지 않음
                #계좌보유주식 목록에 없음
                #순간체결강도 집계 목록이 30개 넘음
                #순간체결강도가 150이상
                #매도비율이 30%보다 낮다면
                if not (obj["f9001"], obj["f302"]) in self.appSettings.orderList \
                    and len(self.appSettings.orderList) <= self.tradeMaxCount    \
                    and self.parent.twMyStocks.isExist(obj["f9001"]) == None     \
                    and len(thisStrategy["momentList"]) > 50                     \
                    and thisStrategy.get("momentStrength", 0)  > 150             \
                    and thisStrategy.get("momentSell", 0) < 30:
                    
                    order = self.getBuyCount({
                        "sScrNo"    : "3001",
                        "nOrderType": 1,
                        "sCode"     : obj["f9001"],
                        "sCount"    : 0,
                        "nQty"      : 0,
                        "nPrice"    : obj["f10"  ],
                        "reason"    : "조건검색 신규 매수"
                    });

                    if order["nQty"] > 0:
                        #체결,잔고 signal받는 곳에서 처리할려고 했는데.. 그사이 너무 많이 매수 신청을 해서.. 신청즉시 재매수금지 등록을 해야함
                        #근데... 신청결과에서는 잔고부족이나, 기타 다른 오류는 확인이 불가한데... 이거 신청만 되고 체결이 안되면..
                        #그냥 재매수 금지항목에만 등록되는건데. 뭐 다른 방법이 없나???
                        self.appSettings.orderList.add((obj["f9001"], obj["f302"]));
                        result = self.sendOrder(order, {
                            "stockCode" : obj["f9001"],
                            "stockName" : obj["f302" ],
                        });

                        if result != 0:#모의서버 매수금지 항목이거나 기타 확인 과정의 오류가 발생한다고 해도.. 0값이 넘어오는데.. 이건 어쩌나?
                            self.appSettings.orderList.remove((obj["f9001"], obj["f302"]));
                    else:
                        result = -1;
            else:
                self.conStrategy[obj["stockCode"]] = {
                    "momentList"    : [],
                    "momentStrength": 0,
                    "momentSell"    : 0,
                };
    #매도전략
    def sellStrategy(self, obj):
        dt          = self.datetime.now();
        hhmm        = "{0:02d}{1:02d}".format(dt.hour, dt.minute);
        isTradeTime = (hhmm >= self.startTime and hhmm <= self.endTime);

        if self.isRun and isTradeTime:
            myStocks = self.parent.twMyStocks.getRowDatas(obj["f9001"]);
            for myStock in myStocks:
                if self.currentTab == 0:
                    self.trailingStop(obj, myStock);
                else:
                    self.stopLoss(obj, myStock);
    
    #주문취소
    def orderCancel(self, chejanStock):
        """
        3001: 신규매수,
        3002: 신규매도,
        3011: TrailingStop(매수) 손실 추가매수,
        3012: TrailingStop(매도) 수익달성,
        3013: TrailingStop(매도) 수익보존,
        3014: TrailingStop(매도) 손실 전량매도,
        3015: TrailingStop(매도) 수익 달성 후 매도비율 높을경우 전량매도,
        3016: TrailingStop(매도) 추가매수 반등 수수료 전량매도,
        3021: StopLoss(매수) 손실 추가매수,
        3022: StopLoss(매도) 수익달성,
        3023: StopLoss(매도) 손실 전량매도,
        3999: 기타주문,
        """
        orderCount = chejanStock["orderCount"] if chejanStock["orderStatus"] == "접수" else chejanStock["missCount"];
        if orderCount > 0:
            chejanStock["isCancel"] = True;
            self.parent.twChejanStocks.addRows(chejanStock);
            
            result = self.sendOrder({
                "nOrderType" : 3 if chejanStock["hogaGb"] == "+매수" else 4,
                "sScrNo"     : chejanStock["screenNo"  ],
                "sCode"      : chejanStock["stockCode" ], #주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                "nQty"       : orderCount               , #접수인 상태에서는 주문수량을 취소하고, 체결 상태에서는 미체결 수량을 취소한다.
                "nPrice"     : chejanStock["nowPrice"  ],
                "sOrgOrderNo": chejanStock["orderNo"   ],
                "reason"     : "체결 대기시간초과 취소({0})".format(chejanStock["hogaGb"]),
            }, chejanStock);

            if result == 0:
                if chejanStock["screenNo"] == "3001":
                    self.appSettings.orderList.remove((chejanStock["stockCode"], chejanStock["stockName"]));
            else:
                chejanStock["isCancel"] = False;
            self.parent.twChejanStocks.addRows(chejanStock);
        else:
            result = -1;
        return result;
    
    #트레일링 스탑
    def trailingStop(self, obj, myStock):
        myStrategy = self.myStrategy[obj["f9001"]]           \
                     if obj["f9001"] in self.myStrategy else \
                     None;
        conStrategy = self.conStrategy[obj["f9001"]];

        if myStrategy == None:
            return;
    
        nowPrice = int(obj["f10"]);#현재가
        result   = -1;

        if myStrategy["tsActive"]:
            #목표 수익율 진입
            if myStrategy["tsDivSell"] < 1:
                #현재 수익율이 목표수익율 달성시 최초 분할매도
                orderCount = int(myStock["reminingCount"] * self.tsDivRate / 100);
                orderCount = myStock["reminingCount"] \
                             if orderCount == 0 else  \
                             orderCount;
                if orderCount > 0:
                    myStrategy["tsDivSell"] = 1;
                    #수익달성시 재매수 금지목록에 추가한다
                    self.appSettings.orderList.add((obj["f9001"], obj["f302"]));
                    result = self.sendOrder({
                        "sScrNo"    : "3012",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"],
                        "nQty"      : orderCount,
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop 목표가 달성매도 momentSell:({0})".format(conStrategy["momentSell"]),
                    }, myStock);

                    if result != 0:
                        myStrategy["tsDivSell"] = 0;
            
            #분할매도가 되어 있고, 현재 수익율이 +상태이며, 수익율이 보존수익율 보다 낮아진다면 수익율 보존 매도
            elif myStrategy["tsDivSell"] > 0 and myStock["profitRate"] > 0 and self.tsProfitRate / self.tsServeRate * 100 > myStock["profitRate"]:
                #고점대비 현재가가 수익보존율 보다 낮다면 전량매도

                ##해당 종목이 기존에 매도가 걸려 있다면.. 주문 취소(어떻게 주문취소가 끝난 이후를 알 수 있을까?)
                ##1. twMyStocks에 보유갯수랑, 가능갯수가 같은지 확인
                ##   2. 같다면 현재 주문 내역이 없는 종목으로 바로 전량 매도 주문
                ##   3. 같지 않다면 twChejanStocks에 해당 종목의 주문번호로 twChejanHisStocks에 취소내역이 있는지 확인
                ##      4. 있다면 이미 주문 취소가 된 내용으로 보유갯수, 가능갯수가 같을때까지 기다림
                ##      5. 주문 취소 신청
                if myStock["stockCount"] == myStock["reminingCount"]:
                    if myStock["reminingCount"] > 0:
                        myStrategy["tsDivSell"] += 1;
                        #수익달성시 재매수 금지목록에 추가한다
                        self.appSettings.orderList.add((obj["f9001"], obj["f302"]));
                        result = self.sendOrder({
                            "sScrNo"    : "3013",
                            "nOrderType": 2,
                            "sHogaGb"   : "03", #수익보존율 보다 낮을 경우 시장가 매도
                            "sCode"     : myStock["stockCode"    ],
                            "nQty"      : myStock["reminingCount"],
                            "nPrice"    : nowPrice,
                            "reason"    : "TrailingStop 수익보존 매도 momentSell:({0})".format(conStrategy["momentSell"]),
                        }, myStock);

                        if result != 0:
                            myStrategy["tsDivSell"] -= 1;
                else:
                    chejanStocks = self.parent.twChejanStocks.getRowDatas(myStock["stockCode"]);
                    for chejan in chejanStocks:
                        if not chejan["orderNo"] in self.parent.twChejanHisStocks.getColumnDatas("oriOrderNo"):
                            #취소 주문 내역이 없다면 취소주문
                            self.orderCancel(chejan);
            
            elif conStrategy.get("momentSell", 0) > 63:
                #수익율 달성이후 최근 매도비율 63% 초과시 전량 매도

                ##해당 종목이 기존에 매도가 걸려 있다면.. 주문 취소(어떻게 주문취소가 끝난 이후를 알 수 있을까?)
                ##1. twMyStocks에 보유갯수랑, 가능갯수가 같은지 확인
                ##   2. 같다면 현재 주문 내역이 없는 종목으로 바로 전량 매도 주문
                ##   3. 같지 않다면 twChejanStocks에 해당 종목의 주문번호로 twChejanHisStocks에 취소내역이 있는지 확인
                ##      4. 있다면 이미 주문 취소가 된 내용으로 보유갯수, 가능갯수가 같을때까지 기다림
                ##      5. 주문 취소 신청
                if myStock["stockCount"] == myStock["reminingCount"]:
                    if myStock["reminingCount"] > 0:
                        myStrategy["tsDivSell"] += 1;
                        #수익달성시 재매수 금지목록에 추가한다
                        self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                        result = self.sendOrder({
                            "sScrNo"    : "3015",
                            "nOrderType": 2,
                            "sHogaGb"   : "03", #매도비율 63% 초과시 시장가 매도
                            "sCode"     : myStock["stockCode"    ],
                            "nQty"      : myStock["reminingCount"],
                            "nPrice"    : nowPrice,
                            "reason"    : "TrailingStop 현재 매도비율 {0}% 초과 수익보존 매도".format(conStrategy["momentSell"]),
                        }, myStock);

                        if result != 0:
                            myStrategy["tsDivSell"] -= 1;
                else:
                    chejanStocks = self.parent.twChejanStocks.getRowDatas(myStock["stockCode"]);
                    for chejan in chejanStocks:
                        if not chejan["orderNo"] in self.parent.twChejanHisStocks.getColumnDatas("oriOrderNo"):
                            #취소 주문 내역이 없다면 취소주문
                            self.orderCancel(chejan);
        
        else:
            #목표 수익율 미진입
            if myStrategy["tsAddBuy"] != 0 and myStock["profitRate"] > 1 and conStrategy.get("momentSell", 0) > 63:
                #종목의 추가매수 이력이 있고, 수익율이 1%이상 반등, 매도비율 63% 초과시 전량 매도
                if myStock["reminingCount"] > 0:
                    myStrategy["tsDivSell"] += 1;
                    #재매수 금지목록에 추가한다
                    self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                    result = self.sendOrder({
                        "sScrNo"    : "3016",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"    ],
                        "nQty"      : myStock["reminingCount"],
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop(매도) 추가매수 반등 수수료 전량매도"
                    }, myStock);

                    if result != 0:
                        myStrategy["tsDivSell"] -= 1;
            
            elif int(myStrategy["averagePrice"] / nowPrice * 100) > 100 - self.tsLossRate and len(conStrategy["momentList"]) > 100 and conStrategy.get("momentSell", 0) < 30:
                #현재가가 대비 평단가 비율이 추가매수 비율보다 낮고 거래횟수가 100회이상 매도비율이 30%이하라면 보유수량 2배 추가매수(매수가능 금액이 부족하다면 가능한 금액만큼만 매수)
                if self.tsDivBuyActive:
                    if len(self.parent.twChejanStocks.getRowDatas(myStock["stockCode"])) == 0:
                        order = self.getBuyCount({
                            "sScrNo"     : "3011",
                            "nOrderType" : 1,
                            "sCode"      : myStock["stockCode" ],
                            "sCount"     : myStock["stockCount"],
                            "nQty"       : 0,
                            "nPrice"     : nowPrice,
                            "reason"     : "TrailingStop 추가매수({0})".format(myStrategy["tsAddBuy"]),
                        });

                        if order["nQty"] > 0:
                            myStrategy["tsAddBuy"] += 1;
                            result = self.sendOrder(order, myStock);

                            if result != 0:
                                myStrategy["tsAddBuy"] -= 1;
                        else:
                            #추가매수시 매수가능금액이 부족하다면 추가매수 횟수만 올린다.
                            myStrategy["tsAddBuy"] += 1;
                else:
                    if myStock["reminingCount"] > 0:
                        myStrategy["tsDivSell"] += 1;
                        #재매수 금지목록에 추가한다
                        self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                        result = self.sendOrder({
                            "sScrNo"    : "3014",
                            "nOrderType": 2,
                            "sHogaGb"   : "03", #시장가 매도
                            "sCode"     : myStock["stockCode"    ],
                            "nQty"      : myStock["reminingCount"],
                            "nPrice"    : 0,
                            "reason"    : "TrailingStop 추가매수 초과 손실매도"
                                          if self.tsDivBuyActive and self.tsDivBuyCount < myStrategy["tsAddBuy"] else
                                          "TrailingStop 손실매도",
                        }, myStock);

                        if result != 0:
                            myStrategy["tsDivSell"] -= 1;
        return result;
    
    #스탑로스
    def stopLoss(self, obj, myStock):
        myStrategy = self.myStrategy[obj["f9001"]]           \
                     if obj["f9001"] in self.myStrategy else \
                     {};
        
        nowPrice   = int(obj["f10"]);#현재가
        
        if self.slProfit <= myStock["profitRate"]:
            if myStock["reminingCount"] > 0:
                myStrategy["slDivSell"] += 1;
                #수익 달성시 재매수 금지목록에 추가한다.
                self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                result = self.sendOrder({
                    "sScrNo"    : "3022",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"    ],
                    "nQty"      : myStock["reminingCount"],
                    "nPrice"    : nowPrice,
                    "reason"    : "StopLoss 수익달성 매도"
                }, myStock);

                if result != 0:
                    myStrategy["slDivSell"] -= 1;
                
        elif int(myStrategy["averagePrice"] / nowPrice) > 100 - self.slLossRate:
            if self.slDivBuyActive:
                if len(self.parent.twChejanStocks.getRowDatas(myStock["stockCode"])) == 0:
                    order = self.getBuyCount({
                        "sScrNo"     : "3021",
                        "nOrderType" : 1,
                        "sCode"      : myStock["stockCode" ],
                        "sCount"     : myStock["stockCount"],
                        "nQty"       : 0,
                        "nPrice"     : nowPrice,
                        "reason"     : "StopLoss 추가매수({0})".format(myStrategy["slAddBuy"]),
                    });

                    if order["nQty"] > 0:
                        myStrategy["slAddBuy"] += 1;
                        #재매수 금지목록에 추가한다
                        self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                        result = self.sendOrder(order, myStock);

                        if result != 0:
                            myStrategy["slAddBuy"] -= 1;
                    else:
                        #추가매수시 매수가능금액이 부족하다면 추가매수 횟수만 올린다.
                        myStrategy["slAddBuy"] += 1;
            else:
                if myStock["reminingCount"] > 0:
                    myStrategy["slDivSell"] += 1;
                    #재매수 금지목록에 추가한다
                    self.appSettings.orderList.add((obj["f9001"], obj["f302"]));

                    result = self.sendOrder({
                        "sScrNo"    : "3023",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"    ],
                        "nQty"      : myStock["reminingCount"],
                        "nPrice"    : nowPrice,
                        "reason"    : "StopLoss 추가매수 초과 손실매도"
                                       if self.slDivBuyActive and self.slDivBuyCount < myStrategy["slAddBuy"] else
                                      "StopLoss 손실매도",
                    }, myStock);
                    
                    if result != 0:
                        myStrategy["slDivSell"] -= 1;
        
    #계좌 보유주식 일괄매도
    def stockSellAll(self):
        myStocks = iter(self.parent.twMyStocks.getRowDatas());    
        myStock = next(myStocks, None);
        while myStock != None:
            if myStock["reminingCount"] > 0:
                result = self.sendOrder({
                    "sScrNo"    : "3002",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"    ],
                    "nQty"      : myStock["reminingCount"],
                    "nPrice"    : myStock["nowPrice"     ],
                    "reason"    : "계좌 보유주식 일괄매도",
                }, myStock);
                
                if result == 0:
                    myStock = next(myStocks, None);
                else:
                    time.sleep(0.25);

    #매수가능 수량 조회
    def getBuyCount(self, order):
        myAccountInfo = self.parent.gbMyAccount.getAccountInfo();
        vOrderableAmount = myAccountInfo["vOrderableAmount"]; #주문가능금액
        nPrice = int(order["nPrice"]);
        orderAmount = 0;
        
        if order["sScrNo"] != "3001":#추가매수의 경우 보유수량의 2배 수량 매수, 단 금액이 부족하다면.. 금액 한도 내에서 매수
            orderAmount = order["sCount"] * 2 * (nPrice + int(nPrice * self.buyTaxRate / 10) * 10);
            if orderAmount > vOrderableAmount:
                order["nQty"] = int(vOrderableAmount / (nPrice + int(nPrice * self.buyTaxRate / 10) * 10));
            else:
                order["nQty"] = order["sCount"] * 2;
        else:#신규매수의 경우 추가매수 예비금을 제한 비율로 매수
            #추가매수 예수금 = (평가잔액 + 예수금) * 매수비율%
            addBuyReserveAmount = int((myAccountInfo["vTotalNowAmount"] +  myAccountInfo["vOrderableAmount"]) * self.buyRate / 100); #추가매수 예비금

            if self.buyRateActive:
                orderAmount = (vOrderableAmount - addBuyReserveAmount) * (self.buyRate / 100);
            else:
                orderAmount = self.buyAmount if (vOrderableAmount - addBuyReserveAmount) > self.buyAmount else (vOrderableAmount - addBuyReserveAmount);
            
            buyAmount = (nPrice + int(nPrice * self.buyTaxRate / 10 * 10));
            order["nQty"] = int(orderAmount / buyAmount) if orderAmount > 0 else 0;
        return order;

    #주문신청
    def sendOrder(self, order, stock):
        result = -1;
        if order["nQty"] > 0:
            if order["nOrderType"] == 2:
                #매도주문
                stock["reminingCount"] -= int(order["nQty"]);
                self.parent.twMyStocks.addRows(stock)
                
                result = self.parent.sendOrder({
                    "sRQName"   : "{0}({1})".format(stock["stockName"], stock["stockCode"]),
                    "sAccNo"    : self.parent.gbMyAccount.uValue1.currentData(),
                    "sScrNo"    : order["sScrNo"    ],                                              #화면번호
                    "nOrderType": order["nOrderType"],                                              #주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sHogaGb"   : order.get("sHogaGb", "00"),                                       #거래구분(sHogaGb) 00: 지정가, 03: 시장가
                    "sCode"     : order["sCode"     ],                                              #종목코드
                    "nQty"      : order["nQty"      ],                                              #주문수량
                    "nPrice"    : order["nPrice"    ] if order.get("sHogaGb", "00") == "00" else 0, #주문가격
                    "reason"    : order["reason"    ],                                              #주문사유
                });

                #chejanSignalSlot처리하려고 했는데.. QTableWidget갱신에 시간이 오래 걸리면 무한 매도 주문이 나가서 서버랑 연결이 끊어짐..
                #매도시.. 주문가능수량 갱신은.. 매도 주문 넣으면서..(취소 주문 넣을때는.. 전략에서 다시 주문가능수량 갱신해야 함)
                if result != 0:
                    stock["reminingCount"] += int(order["nQty"]);
                    self.parent.twMyStocks.addRows(stock);
                
            elif order["nOrderType"] == 1:
                #매수주문
                result = self.parent.sendOrder({
                    "sRQName"   : "{0}({1})".format(stock["stockName"], stock["stockCode"]),
                    "sAccNo"    : self.parent.gbMyAccount.uValue1.currentData(),
                    "sScrNo"    : order["sScrNo"    ],                                              #화면번호
                    "nOrderType": order["nOrderType"],                                              #주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sHogaGb"   : order.get("sHogaGb", "00"),                                       #거래구분(sHogaGb) 00: 지정가, 03: 시장가
                    "sCode"     : order["sCode"     ],                                              #종목코드
                    "nQty"      : order["nQty"      ],                                              #주문수량
                    "nPrice"    : order["nPrice"    ] if order.get("sHogaGb", "00") == "00" else 0, #주문가격
                    "reason"    : order["reason"    ],                                              #주문사유
                });

            elif order["nOrderType"] in [3, 4]:
                #매수취소(3), #매도취소(4)
                #취소항목은 addChejanSlot에서 완료 메세지를 받으면 그때 처리하자....
                    
                result = self.parent.sendOrder({
                    "sRQName"    : "{0}({1})".format(stock["stockName"], stock["stockCode"]),
                    "sAccNo"     : self.parent.gbMyAccount.uValue1.currentData(),
                    "nOrderType" : order["nOrderType" ],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sScrNo"     : order["sScrNo"     ],#화면번호
                    "sCode"      : order["sCode"      ],#종목코드
                    "nQty"       : order["nQty"       ],#주문수량
                    "nPrice"     : order["nPrice"     ],#주문가격
                    "reason"     : order["reason"     ],#주문사유
                    "sOrgOrderNo": order["sOrgOrderNo"],#원주문번호
                });
            
            elif result == -308:
                time.sleep(0.25);
            
            return result;
    
        else:
            print("{0} - 주문확인필요: {1}({2}) {3}주, {4},".format(self.datetime.now(), stock["stockName"], stock["stockCode"], order["nQty"], order["reason"]));
            return -1;        
            
    #데이터 수집 및 분석
    def dataAnalysis(self, obj):
        nowPrice    = int(obj["f10"]);#현재가
        conStrategy = self.conStrategy[obj["f9001"]]           \
                      if obj["f9001"] in self.conStrategy else \
                      None;
        
        #검색조건 결과 전략분석
        if conStrategy != None:
            conStrategy["momentList"].append(int(obj["f15"]));
            conStrategy["momentList"] = conStrategy["momentList"][self.monentSize * -1:];

            buySum  = 1;
            sellSum = 1;
            for cnt in conStrategy["momentList"]:
                if cnt > 0:
                    buySum += cnt;
                else:
                    sellSum += cnt;
            
            conStrategy["momentStrength"] = int(buySum / abs(sellSum if sellSum != 0 else 1) * 100); #최근체결강도 확인
            conStrategy["momentSell"]     = int((abs(sellSum) / (buySum + abs(sellSum))) * 100);     #최근매도비율
        else:
            self.conStrategy[obj["f9001"]] = {
                "momentList"    : [],
                "momentStrength": 0,
                "momentSell"    : 0,
            };
        
        #보유주식 계좌 전략분석
        myStocks = self.parent.twMyStocks.getRowDatas(obj["f9001"]);
        for myStock in myStocks:
            myStrategy = self.myStrategy[myStock["stockCode"]]           \
                         if myStock["stockCode"] in self.myStrategy else \
                         None;

            if myStrategy != None:
                if self.currentTab == 0:
                    if myStrategy["tsActive"] == False:
                        if myStock["profitRate"] >= self.tsProfitRate:
                            myStrategy["tsActive"   ] = True;
                            myStrategy["tsHighPrice"] = nowPrice;
                    else:
                        if myStrategy["tsHighPrice"] < nowPrice:
                            myStrategy["tsHighPrice"] = nowPrice;
                myStrategy["nowPrice"    ] = nowPrice;
                myStrategy["averagePrice"] = myStock["averagePrice"];
            else:
                self.myStrategy[myStock["stockCode"]] = {
                    "stockCode"   : myStock["stockCode"   ],
                    "stockName"   : myStock["stockName"   ],
                    "nowPrice"    : myStock["nowPrice"    ],
                    "averagePrice": myStock["averagePrice"],
                    "tsActive"    : False,
                    "tsHighPrice" : 0,
                    "tsDivSell"   : 0,
                    "tsAddBuy"    : 0,
                    "slAddBuy"    : 0,
                };
