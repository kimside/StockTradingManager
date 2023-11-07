import datetime, time;

from PyQt5 import QtCore;
from modules.strategy.AbstractStrategy import AbstractStrategy;

#1. 조건검색으로 검색된 항목을 이탈시키지 않고.. 계속 모니터링하면서..
#   내부적 로직의 특정 조건에 만족되면.. 매수신청
#2. 손익율이 -10%되면.. 지정금액 or 비율로 추가매수 실행
#3. 시장의 상황에 따라 실행하는 조건식을 선택(매수/투자비율 조정? 현금확보?)

class MyStrategy(AbstractStrategy):
    def __init__(self, parent=None):
        self.isRun = False;
        self.parent = parent;
        self.appSettings = self.parent.appSettings;
        self.myStrategy  = self.appSettings.myStrategy;
        self.monentSize  = 100;
        self.datetime    = datetime.datetime;
        self.buyTaxRate  = self.parent.buyTaxRate; #매수 수수료
        
        self.startTime     = self.appSettings.vRunStartTime.toString("hhmm"); #자동매매 시작시간
        self.endTime       = self.appSettings.vRunEndTime.toString("hhmm");   #자동매매 종료시간
        self.tradeMaxCount = self.appSettings.vTradeMaxCount;                 #자동매매 거래 종목 갯수 제한
        self.buyRateActive = self.appSettings.vBuyRate;                       #매수 비율/금액지정 여부(True: 비율, False:금액지정)
        self.buyRate       = self.appSettings.vBuyRateValue;                  #매수 매수가능금액 대비 지정비율
        self.buyAmount     = self.appSettings.vBuyAmountValue;                #매수 지정금액태
        self.currentTab    = self.appSettings.currentTab;                     #TrailingStop/StopLoss 활성화 탭(0:TrailingStop, 1:StopLoss)

        self.tsProfitRate    = self.appSettings.vtsTargetProfit;         #TrailingStop 목표수익율
        self.tsLossRate      = self.appSettings.vtsTargetLoss;           #TrailingStop 목표손실율

        self.tsDivBuyActive  = self.appSettings.vtsTouchDivideBuyActive; #TrailingStop 추가매수 활성화 여부
        self.tsDivBuyCount   = self.appSettings.vtsTouchDivideBuy;       #TrailingStop 추가매수 횟수
        self.tsDivProfitRate = self.appSettings.vtsTouchDivideProfit;    #TrailingStop 목표수익율 달성 후 분할매도 추가수익율
        self.tsDivRate       = self.appSettings.vtsTouchDivideRate;      #TrailingStop 목표수익율 달성 후 분할매도 비율
        self.tsServeRate     = self.appSettings.vtsTouchDivideServeRate; #TrailingStop 목표수익율 달성 후 보존수익율
        
        self.slProfit       = self.appSettings.vslTargetProfit;         #StopLoss 목표수익율
        self.slLoss         = self.appSettings.vslTargetLoss;           #StopLoss 목표손실율
        self.slDivBuyActive = self.appSettings.vslTouchDivideBuyActive; #StopLoss 추가매수 활성화 여부
        self.slDivBuyCount  = self.appSettings.vslTouchDivideBuy;       #StopLoss 추가매수 횟수

        #조건검색 결과 전략분석
        self.conStrategy = {};
        #보유주식 계좌 전략분석
    
    #매수전략
    def buyStrategy(self, obj):
        dt          = datetime.datetime.now();
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
                if not (obj["f9001"], obj["f302"]) in self.appSettings.orderList \
                    and len(self.appSettings.orderList) <= self.tradeMaxCount    \
                    and self.parent.twMyStocks.isExist(obj["f9001"]) == None     \
                    and len(thisStrategy["momentList"]) > 30                     \
                    and thisStrategy["momentStrength"]  > 150:
                    
                    orderCount = self.getBuyCount(int(obj["f10"]));
                    if orderCount > 0:
                        result = self.sendOrder({
                            "sScrNo"     : "3001",
                            "nOrderType" : 1,
                            "sCode"      : obj["f9001"],
                            "nQty"       : orderCount,
                            "nPrice"     : obj["f10"  ],
                            "reason"     : "조건검색 신규 매수"
                        }, {
                            "stockCode"    : obj["f9001"],
                            "stockName"    : obj["f302" ],
                        });
                    else:
                        result = -1;
            else:
                self.conStrategy[obj["stockCode"]] = {
                    "momentList"    : [],
                    "momentStrength": 0,
                };
    #매도전략
    def sellStrategy(self, obj):
        dt          = datetime.datetime.now();
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
        3021: StopLoss(매수) 손실 추가매수,
        3022: StopLoss(매도) 수익달성,
        3023: StopLoss(매도) 손실 전량매도,
        """
        orderCount = chejanStock["orderCount"] if chejanStock["orderStatus"] == "접수" else chejanStock["missCount"];
        if orderCount > 0:
            result = self.sendOrder({
                "nOrderType" : 3 if chejanStock["hogaGb"] == "+매수" else 4,
                "sScrNo"     : chejanStock["screenNo"  ],
                "sCode"      : chejanStock["stockCode" ], #주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                "nQty"       : orderCount               , #접수인 상태에서는 주문수량을 취소하고, 체결 상태에서는 미체결 수량을 취소한다.
                "nPrice"     : chejanStock["nowPrice"  ],
                "sOrgOrderNo": chejanStock["orderNo"   ],
                "reason"     : "미체결 대기시간 초과 주문취소({0})".format(chejanStock["hogaGb"]),
            }, chejanStock);
        else:
            result = -1;
        return result;
    
    #트레일링 스탑
    def trailingStop(self, obj, myStock):
        myStrategy = self.myStrategy[obj["f9001"]]           \
                     if obj["f9001"] in self.myStrategy else \
                     None;
        
        if myStrategy == None:
            return;
    
        nowPrice        = int(obj["f10"]);#현재가
        result          = -1;

        if myStrategy["tsActive"]:
            #목표 수익율 진입
            if myStrategy["tsDivSell"] == 0:
                #현재 수익율이 목표수익율 달성시 최초 분할매도
                orderCount = int(myStock["reminingCount"] * self.tsDivRate / 100);
                orderCount = myStock["reminingCount"] \
                             if orderCount == 0 else  \
                             orderCount;
                if orderCount > 0:
                    result = self.sendOrder({
                        "sScrNo"    : "3012",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"],
                        "nQty"      : orderCount,
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop 목표가 달성매도",
                    }, myStock);

                    if result == 0:
                        myStrategy["tsDivSell"] += 1;
            
            elif nowPrice > myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (self.tsProfitRate + (myStrategy["tsDivSell"] * self.tsDivProfitRate)) / 100):
                #현재가가 초과 수익가를 넘었다면 분할매도
                maxSellCnt = int(100 / self.tsDivRate);
                #분할매도 마지막 회차에는 주문가능수량을 전량 매도신청한다.
                orderCount = int(myStock["reminingCount"] * self.tsDivRate * myStrategy["tsDivSell"] / 100 \
                                 if myStrategy["tsDivSell"] < maxSellCnt else                              \
                                 myStock["reminingCount"]);
                orderCount = myStock["reminingCount"] if orderCount == 0 else orderCount;
                
                if orderCount > 0:
                    result = self.sendOrder({
                        "sScrNo"    : "3012",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"],
                        "nQty"      : orderCount,
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop 추가목표가 달성매도({0})".format(myStrategy.get("tsDivSell") + 1 if myStrategy["tsDivSell"] < maxSellCnt else "Last"),
                    }, myStock);

                    if result == 0:
                        myStrategy["tsDivSell"] += 1;

            elif nowPrice < myStrategy["averagePrice"] + (myStrategy["tsHighPrice"] - myStrategy["averagePrice"]) * self.tsServeRate / 100:
                #고점대비 현재가가 수익보존율 보다 낮다면 매도
                if myStock["reminingCount"] > 0:
                    result = self.sendOrder({
                        "sScrNo"    : "3013",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"    ],
                        "nQty"      : myStock["reminingCount"],
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop 수익보존 매도",
                    }, myStock);

                    if result == 0:
                        myStrategy["tsDivSell"] += 1;

        else:
            #목표 수익율 미진입(손실율에 도달했다면)
            if nowPrice < myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (self.tsLossRate * myStrategy["tsAddBuy"]) / 100):
                if self.tsDivBuyActive and self.tsDivBuyCount > myStrategy["tsAddBuy"]:
                    #추가매수(TrailingStop 추가매수 활성화, TrailingStop 추가매수 횟수확인)
                    orderCount = self.getBuyCount(nowPrice);
                    if orderCount > 0:
                        result = self.sendOrder({
                            "sScrNo"     : "3011",
                            "nOrderType" : 1,
                            "sCode"      : myStock["stockCode"],
                            "nQty"       : orderCount,
                            "nPrice"     : nowPrice,
                            "reason"     : "TrailingStop 추가매수({0})".format(myStrategy["tsAddBuy"] + 1),
                        }, myStock);

                        if result == 0:
                            myStrategy["tsAddBuy"] += 1;
                    else:
                        #추가매수시 매수가능금액이 부족하다면 추가매수 횟수만 올린다.
                        myStrategy["tsAddBuy"] += 1;
                else:
                    if myStock["reminingCount"] > 0:
                        result = self.sendOrder({
                            "sScrNo"    : "3014",
                            "nOrderType": 2,
                            "sCode"     : myStock["stockCode"    ],
                            "nQty"      : myStock["reminingCount"],
                            "nPrice"    : nowPrice,
                            "reason"    : "TrailingStop 추가매수 초과 손실매도"
                                          if self.tsDivBuyActive and self.tsDivBuyCount < myStrategy["tsAddBuy"] else
                                          "TrailingStop 손실매도",
                        }, myStock);

                        if result == 0:
                            myStrategy["tsDivSell"] += 1;
        return result;
    
    #스탑로스
    def stopLoss(self, obj, myStock):
        myStrategy = self.myStrategy[obj["f9001"]]           \
                     if obj["f9001"] in self.myStrategy else \
                     {};
        
        nowPrice   = int(obj["f10"]);#현재가
        
        if self.slProfit <= myStock["profitRate"]:
            if myStock["reminingCount"] > 0:
                result = self.sendOrder({
                    "sScrNo"    : "3022",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"    ],
                    "nQty"      : myStock["reminingCount"],
                    "nPrice"    : nowPrice,
                    "reason"    : "StopLoss 수익달성 매도"
                }, myStock);

                if result == 0:
                    myStrategy["slDivSell"] += 1;
                
        elif nowPrice < myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (self.slLoss * myStrategy["slAddBuy"]) / 100):
            if self.slDivBuyActive and self.slDivBuyCount > myStrategy["slAddBuy"]:
                orderCount = self.getBuyCount(nowPrice);
                if orderCount > 0:
                    result = self.sendOrder({
                        "sScrNo"     : "3021",
                        "nOrderType" : 1,
                        "sCode"      : myStock["stockCode"],
                        "nQty"       : orderCount,
                        "nPrice"     : nowPrice,
                        "reason"     : "StopLoss 추가매수({0})".format(myStrategy["slAddBuy"] + 1),
                    }, myStock);

                    if result == 0:
                        myStrategy["slAddBuy"] += 1;
                else:
                    #추가매수시 매수가능금액이 부족하다면 추가매수 횟수만 올린다.
                    myStrategy["slAddBuy"] += 1;
            else:
                if myStock["reminingCount"] > 0:
                    result = self.sendOrder({
                        "sScrNo"    : "3001",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"    ],
                        "nQty"      : myStock["reminingCount"],
                        "nPrice"    : nowPrice,
                        "reason"    : "StopLoss 추가매수 초과 손실매도"
                                       if self.slDivBuyActive and self.slDivBuyCount < myStrategy["slAddBuy"] else
                                      "StopLoss 손실매도",
                    }, myStock);
                    
                    if result == 0:
                        myStrategy["slDivSell"] += 1;
        
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
    def getBuyCount(self, nowPrice):
        vOrderableAmount = self.parent.gbMyAccount.getAccountInfo()["vOrderableAmount"]; #주문가능금액
        orderAmount = 0;
        if self.buyRateActive:
            orderAmount = vOrderableAmount * (self.buyRate / 100);
        else:
            orderAmount = self.buyAmount if vOrderableAmount > self.buyAmount else vOrderableAmount;
        buyAmount = (nowPrice + int(nowPrice * self.buyTaxRate / 10 * 10));
        return int(orderAmount / buyAmount);

    #주문신청
    def sendOrder(self, order, stock):
        if order["nQty"] > 0:
            if order["nOrderType"] == 2:
                #매도주문
                result = self.parent.sendOrder({
                    "sAccNo"     : self.parent.gbMyAccount.uValue1.currentData(),
                    "sScrNo"     : order["sScrNo"    ],#화면번호
                    "nOrderType" : order["nOrderType"],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sCode"      : order["sCode"     ],#종목코드
                    "nQty"       : order["nQty"      ],#주문수량
                    "nPrice"     : order["nPrice"    ],#주문가격
                    "reason"     : order["reason"    ],#주문사유
                });

                #chejanSignalSlot처리하려고 했는데.. QTableWidget갱신에 시간이 오래 걸리면 무한 매도 주문이 나가서 서버랑 연결이 끊어짐..
                #매도시.. 주문가능수량 갱신은.. 매도 주문 넣으면서..(취소 주문 넣을때는.. 전략에서 다시 주문가능수량 갱신해야 함)
                if result == 0:
                    stock["reminingCount"] = stock["reminingCount"] - int(order["nQty"]);
                    self.parent.twMyStocks.addRows(stock);
                elif result == -308:
                    time.sleep(0.25);
                
            elif order["nOrderType"] == 1:
                #매수주문
                result = self.parent.sendOrder({
                    "sAccNo"     : self.parent.gbMyAccount.uValue1.currentData(),
                    "sScrNo"     : order["sScrNo"    ],#화면번호
                    "nOrderType" : order["nOrderType"],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sCode"      : order["sCode"     ],#종목코드
                    "nQty"       : order["nQty"      ],#주문수량
                    "nPrice"     : order["nPrice"    ],#주문가격
                    "reason"     : order["reason"    ],#주문사유
                });

                if result == 0:
                    #체결,잔고 signal받는 곳에서 처리할려고 했는데.. 그사이 너무 많이 매수 신청을 해서.. 신청즉시 재매수금지 등록을 해야함
                    #근데... 신청결과에서는 잔고부족이나, 기타 다른 오류는 확인이 불가한데... 이거 신청만 되고 체결이 안되면..
                    #그냥 재매수 금지항목에만 등록되는건데. 뭐 다른 방법이 없나???
                    if order["reason"] == "조건검색 신규 매수":
                        self.appSettings.orderList.add((stock["stockCode"], stock["stockName"]));
                elif result == -308:
                    time.sleep(0.25);
            
            elif order["nOrderType"] in [3, 4]:
                #매수취소(3), #매도취소(4)
                #취소항목은 addChejanSlot에서 완료 메세지를 받으면 그때 처리하자....
                result = self.parent.sendOrder({
                    "sAccNo"     : self.parent.gbMyAccount.uValue1.currentData(),
                    "nOrderType" : order["nOrderType" ],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                    "sScrNo"     : order["sScrNo"     ],#화면번호
                    "sCode"      : order["sCode"      ],#종목코드
                    "nQty"       : order["nQty"       ],#주문수량
                    "nPrice"     : order["nPrice"     ],#주문가격
                    "reason"     : order["reason"     ],#주문사유
                    "sOrgOrderNo": order["sOrgOrderNo"],#원주문번호
                });

                if result == -308:
                    time.sleep(0.25);
            
            if result == 0:
                self.parent.addConsoleSlot({
                    "sRQName": self.parent.nOrderType.get(order["nOrderType"], ""),
                    "sTrCode": "",
                    "sScrNo" : order["sScrNo"],
                    "sMsg"   : "{0}: {1}({2}) {3}주, ({4})".format(self.parent.nOrderType.get(order["nOrderType"], ""), stock["stockName"], stock["stockCode"], order["nQty"], order["reason"]),
                });
            return result;
    
        else:
            print("{0} - 주문확인필요: {1}, {2}({3}) {4}주, {5},".format(datetime.datetime.now(), self.parent.nOrderType.get(order["nOrderType"], ""), stock["stockName"], stock["stockCode"], order["nQty"], order["reason"]))
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
            #최근체결강도 확인(마지막 100틱 거래량 기준)
            conStrategy["momentStrength"] = int(abs(buySum) / abs(sellSum if sellSum != 0 else 1) * 100);
        else:
            self.conStrategy[obj["f9001"]] = {
                "momentList"    : [],
                "momentStrength": 0,
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
