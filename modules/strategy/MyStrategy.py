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
        self.monentSize = 100;

        #조건검색 결과 전략분석
        self.conStrategy = {};
        #보유주식 계좌 전략분석
    
    #매수전략
    def buyStrategy(self, obj):
        isTradeTime = datetime.datetime.now().strftime("%H%M") >= self.appSettings.vRunStartTime.toString("hhmm") and \
                      datetime.datetime.now().strftime("%H%M") <= self.appSettings.vRunEndTime.toString("hhmm");
        
        if self.isRun and isTradeTime:
            if obj["f9001"] in self.conStrategy:
                thisStrategy = self.conStrategy[obj["f9001"]];
            
                #재매수금지 대상에 포함되지 않음
                #매수최대갯수를 넘지 않음 and len(self.appSettings.orderList) <= self.appSettings.vTradeMaxCount \
                #계좌보유주식 목록에 없음
                #순간체결강도 집계 목록이 30개 넘음
                #순간체결강도가 150이상
                if not (obj["f9001"], obj["f302"]) in self.appSettings.orderList           \
                    and len(self.appSettings.orderList) <= self.appSettings.vTradeMaxCount \
                    and self.parent.twMyStocks.isExist(obj["f9001"]) == None               \
                    and len(thisStrategy["momentList"]) > 30                               \
                    and thisStrategy["momentStrength"]  > 150:
                    
                    orderCount = self.getBuyCount(int(obj["f10"]));
                    obj["reminingCount"] = orderCount;
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
                            "reminingCount": orderCount,
                        });
            else:
                self.conStrategy[obj["stockCode"]] = {
                    "momentList"    : [],
                    "momentStrength": 0,
                };
    #매도전략
    def sellStrategy(self, obj):
        isTradeTime = datetime.datetime.now().strftime("%H%M") >= self.appSettings.vRunStartTime.toString("hhmm") and \
                      datetime.datetime.now().strftime("%H%M") <= self.appSettings.vRunEndTime.toString("hhmm");

        if self.isRun and isTradeTime:
            myStocks = self.parent.twMyStocks.getRowDatas(obj["f9001"]);
            for myStock in myStocks:
                if self.parent.appSettings.currentTab == 0:
                    self.trailingStop(obj, myStock);
                else:
                    self.stopLoss(obj, myStock);
    
    #주문취소
    def orderCancel(self, stock):
        result = -1;
        #접수인 상태에서는 주문수량을 취소하고, 체결 상태에서는 미체결 수량을 취소한다.
        nQty = stock["missCount"] if stock["missCount"] != 0 else stock["orderCount"];
        if nQty != 0:
            result = self.sendOrder({
                "nOrderType" : 3 if stock["hogaGb"] == "+매수" else 4,
                "sCode"      : stock["stockCode" ],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
                "nQty"       : stock["missCount" ] if stock["missCount"] != 0 else stock["orderCount"],#미체결수량만큼 취소한다.
                "nPrice"     : stock["nowPrice"  ],
                "reason"     : "미체결 대기시간 초과 주문취소({0})".format(stock["hogaGb"]),
                "sOrgOrderNo": stock["orderNo"   ],
            }, stock);
            #print("미체결 대기시간 초과 주문취소 {0}({1}) {2} (result:{3})".format(stock["stockName"], stock["stockCode"], stock["hogaGb"], result));
        else:
            #print("미체결 대기시간 초과 주문취소 수량 확인 {0}({1}) {2} (수량:{3})".format(stock["stockName"], stock["stockCode"], stock["hogaGb"], nQty));
            result = -1;
        return result;
    
    #트레일링 스탑
    def trailingStop(self, obj, myStock):
        myStrategy   = self.appSettings.myStrategy[obj["f9001"]]           \
                       if obj["f9001"] in self.appSettings.myStrategy else \
                       None;
        
        tsProfitRate    = self.parent.appSettings.vtsTargetProfit;         #TrailingStop 목표수익율
        tsLossRate      = self.parent.appSettings.vtsTargetLoss;           #TrailingStop 목표손실율
        tsDivProfitRate = self.parent.appSettings.vtsTouchDivideProfit;    #TrailingStop 목표수익율 달성 후 분할매도 추가수익율
        tsDivRate       = self.parent.appSettings.vtsTouchDivideRate;      #TrailingStop 목표수익율 달성 후 분할매도 비율
        tsServeRate     = self.parent.appSettings.vtsTouchDivideServeRate; #TrailingStop 목표수익율 달성 후 보존수익율
        nowPrice        = int(obj["f10"]);#현재가

        if myStrategy.get("tsActive"):
            #목표 수익율 진입
            if myStrategy.get("tsDivSell") == 0:
                #현재 수익율이 목표수익율 달성시 최초 분할매도
                orderCount = int(myStock["reminingCount"] * tsDivRate / 100);
                orderCount = myStock["reminingCount"] \
                             if orderCount == 0 else  \
                             orderCount;
                result = self.sendOrder({
                    "sScrNo"     : "3012",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"],
                    "nQty"      : orderCount,
                    "nPrice"    : nowPrice,
                    "reason"    : "TrailingStop 목표가 달성매도",
                }, myStock);

                if result == 0:
                    myStrategy["tsDivSell"] += 1;
            
            elif nowPrice > myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (tsProfitRate + (myStrategy.get("tsDivSell") * tsDivProfitRate)) / 100):
                #현재가가 초과 수익가를 넘었다면 분할매도
                maxSellCnt = int(100 / tsDivRate);#분할매도 마지막 회차에는 주문가능수량을 전량 매도신청한다.
                orderCount = int(myStock["reminingCount"] * tsDivRate * myStrategy.get("tsDivSell") / 100 \
                                if myStrategy.get("tsDivSell") <= maxSellCnt else                         \
                                myStock["reminingCount"]);
                orderCount = myStock["reminingCount"] \
                             if orderCount == 0 else  \
                             orderCount;
                result = self.sendOrder({
                    "sScrNo"    : "3012",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"],
                    "nQty"      : orderCount,
                    "nPrice"    : nowPrice,
                    "reason"    : "TrailingStop 추가목표가 달성매도({0})".format(myStrategy.get("tsDivSell") + 1),
                }, myStock);

                if result == 0:
                    myStrategy["tsDivSell"] += 1;
            
            elif nowPrice < myStrategy["averagePrice"] + (myStrategy["tsHighPrice"] - myStrategy["averagePrice"]) * tsServeRate / 100:
                #고점대비 현재가가 수익보존율 보다 낮다면 매도
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
            if nowPrice < myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (tsLossRate * myStrategy.get("tsAddBuy")) / 100):
                if self.appSettings.vtsTouchDivideBuyActive and self.appSettings.vtsTouchDivideBuy > myStrategy.get("tsAddBuy"):
                    #추가매수(TrailingStop 추가매수 활성화, TrailingStop 추가매수 횟수확인)
                    orderCount = self.getBuyCount(nowPrice);
                    if orderCount > 0:
                        result = self.sendOrder({
                            "sScrNo"     : "3011",
                            "nOrderType" : 1,
                            "sCode"      : myStock["stockCode"],
                            "nQty"       : orderCount,
                            "nPrice"     : nowPrice,
                            "reason"     : "TrailingStop 추가매수({0})".format(myStrategy.get("tsAddBuy") + 1),
                        }, myStock);

                        if result == 0:
                            myStrategy["tsAddBuy"] += 1;
                else:
                    result = self.sendOrder({
                        "sScrNo"    : "3014",
                        "nOrderType": 2,
                        "sCode"     : myStock["stockCode"    ],
                        "nQty"      : myStock["reminingCount"],
                        "nPrice"    : nowPrice,
                        "reason"    : "TrailingStop 추가매수 초과 손실매도"
                                      if self.appSettings.vtsTouchDivideBuyActive and
                                         self.appSettings.vtsTouchDivideBuy < myStrategy.get("tsAddBuy") else
                                      "TrailingStop 손실매도",
                    }, myStock);
        self.appSettings.myStrategy[myStock["stockCode"]] = myStrategy;
        self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
        #속도가 너무 느리다
        #self.appSettings.sync();
    
    #스탑로스
    def stopLoss(self, obj, myStock):
        myStrategy = self.appSettings.myStrategy[obj["f9001"]]           \
                     if obj["f9001"] in self.appSettings.myStrategy else \
                     {};
        slProfit   = self.parent.appSettings.vslTargetProfit;#StopLoss 목표수익율
        slLoss     = self.parent.appSettings.vslTargetLoss;  #StopLoss 목표손실율
        nowPrice   = int(obj["f10"]);#현재가
        
        if slProfit <= myStock["profitRate"]:
            result = self.sendOrder({
                "sScrNo"    : "3022",
                "nOrderType": 2,
                "sCode"     : myStock["stockCode"    ],
                "nQty"      : myStock["reminingCount"],
                "nPrice"    : nowPrice,
                "reason"    : "StopLoss 수익달성 매도"
            }, myStock);
        elif nowPrice < myStrategy["averagePrice"] + int(myStrategy["averagePrice"] * (slLoss * myStrategy.get("slAddBuy")) / 100):
            if self.appSettings.vslTouchDivideBuyActive and self.appSettings.vslTouchDivideBuy > myStrategy.get("slAddBuy"):
                orderCount = self.getBuyCount(nowPrice);
                if orderCount > 0:
                    result = self.sendOrder({
                        "sScrNo"     : "3021",
                        "nOrderType" : 1,
                        "sCode"      : myStock["stockCode"],
                        "nQty"       : orderCount,
                        "nPrice"     : nowPrice,
                        "reason"     : "StopLoss 추가매수({0})".format(myStrategy.get("slAddBuy") + 1),
                    }, myStock);

                    if result == 0:
                        myStrategy["slAddBuy"] += 1;
                else:
                    #추가매수할 매수가능금액이 부족하다면.. 전량매도??
                    pass;
            else:
                result = self.sendOrder({
                    "sScrNo"    : "3001",
                    "nOrderType": 2,
                    "sCode"     : myStock["stockCode"    ],
                    "nQty"      : myStock["reminingCount"],
                    "nPrice"    : nowPrice,
                    "reason"    : "StopLoss 추가매수 초과 손실매도"
                                  if self.appSettings.vslTouchDivideBuyActive and
                                     self.appSettings.vslTouchDivideBuy < myStrategy.get("slAddBuy") else
                                  "StopLoss 손실매도",
                }, myStock);
        self.appSettings.myStrategy[myStock["stockCode"]] = myStrategy;
        self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
        #속도가 너무 느리다
        #self.appSettings.sync();
    
    #계좌 보유주식 일괄매도
    def stockSellAll(self):
        myStocks = iter(self.parent.twMyStocks.getRowDatas());    
        myStock = next(myStocks, None);
        while myStock != None:
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
        if self.appSettings.vBuyRate:
            orderAmount = vOrderableAmount * (self.appSettings.vBuyRateValue / 100);
        else:
            orderAmount = self.appSettings.vBuyAmountValue if vOrderableAmount > self.appSettings.vBuyAmountValue else vOrderableAmount;
        buyAmount = (nowPrice + int(nowPrice * self.parent.buyTaxRate / 10 * 10));
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
                    self.parent.twMyStocks.addRows([stock]);
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
                        #신규매수항목임
                        self.appSettings.orderList.add((stock["stockCode"], stock["stockName"]));
                        self.appSettings.setValue("orderList", self.appSettings.orderList);
                        #속도가 너무느리다
                        #self.appSettings.sync();
                elif result == -308:
                    time.sleep(0.25);
            
            elif order["nOrderType"] in [3, 4]:
                #매수취소(3), #매도취소(4)
                #취소항목은 addChejanSlot에서 완료 메세지를 받으면 그때 처리하자....
                result = self.parent.sendOrder({
                    "sAccNo"     : self.parent.gbMyAccount.uValue1.currentData(),
                    "nOrderType" : order["nOrderType" ],#주문유형 1:신규매수, 2:신규매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
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
                    "sScrNo" : "3000",
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
            myStrategy = self.appSettings.myStrategy[myStock["stockCode"]] \
                         if myStock["stockCode"] in self.appSettings.myStrategy else \
                         None;

            if myStrategy != None:
                if self.parent.appSettings.currentTab == 0:
                    if myStrategy["tsActive"] == False:
                        if myStock["profitRate"] >= self.parent.appSettings.vtsTargetProfit:
                            myStrategy["tsActive"   ] = True;
                            myStrategy["tsHighPrice"] = nowPrice;
                    else:
                        if myStrategy["tsHighPrice"] < nowPrice:
                            myStrategy["tsHighPrice"] = nowPrice;
                myStrategy["nowPrice"    ] = nowPrice;
                myStrategy["averagePrice"] = myStock["averagePrice"];
                self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
                #속도가 너무 느리다
                #self.appSettings.sync();
            else:
                self.appSettings.myStrategy[myStock["stockCode"]] = {
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
                self.appSettings.setValue("myStrategy", self.appSettings.myStrategy);
                #속도가 너무느리다
                #self.appSettings.sync();
