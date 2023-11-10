import os, json, datetime;

from PyQt5          import QtCore, QAxContainer;
from PyQt5Singleton import Singleton;

from modules.exception.NotInsallOpenAPI import NotInsallOpenAPI;
from modules.api.LogMaker               import LogMaker;
from modules.api.entity.UserInfo        import UserInfo;
from modules.api.entity.Optkwfid        import Optkwfid;

class KiwoomAPI(LogMaker, metaclass=Singleton):
    loginSignal    = QtCore.pyqtSignal(object);
    conInOutSignal = QtCore.pyqtSignal(object);
    stockSignal    = QtCore.pyqtSignal(object);
    apiMsgSignal   = QtCore.pyqtSignal(object);
    chejanSignal   = QtCore.pyqtSignal(object);

    ##생성자
    def __init__(self, parent=None, **kwargs):
        super().__init__();
        
        self.api = QAxContainer.QAxWidget("KHOPENAPI.KHOpenAPICtrl.1");
        
        if len(self.api.verbs()) == 0:
            raise NotInsallOpenAPI;

        self.realReceiveList    = set(); #실시간 수신 종목 코드(계좌번호를 바꾸던지, 아니면 배치를 정지시킬때 해당 목록을 SetRealRemove시켜야 한다.);
        self.receiveTrDataMulti = False;
        self.reminingParams     = None;
        self.reminingDatas      = None;
        self.trOutput           = None;

        self.onEventConnectLoop        = QtCore.QEventLoop();
        self.onReceiveTrDataLoop       = QtCore.QEventLoop();
        self.onReceiveConditionVerLoop = QtCore.QEventLoop();
        self.sendConditionLoop         = QtCore.QEventLoop();

        self.api.OnEventConnect.connect(self.onEventConnect);                 ##CommConnect 콜백
        self.api.OnReceiveTrData.connect(self.onReceiveTrData);               ##CommRqData  콜백
        self.api.OnReceiveConditionVer.connect(self.onReceiveConditionVer);   ##GetConditionLoad 콜백
        self.api.OnReceiveTrCondition.connect(self.onReceiveTrCondition);     ##SendCondition 콜백
        self.api.OnReceiveRealCondition.connect(self.onReceiveRealCondition); ##OnReceiveRealCondition 콜백
        self.api.OnReceiveRealData.connect(self.onReceiveRealData);           ##OnReceiveRealData 콜백
        self.api.OnReceiveMsg.connect(self.onReceiveMsg);                     ##OnReceiveMsg 콜백
        self.api.OnReceiveChejanData.connect(self.onReceiveChejanData);       ##OnReceiveChejanData 콜백
        
        self.isLogin = False;
        self.buyTaxRate  = 0.0035;
        self.sellTaxRate = 0.0035;
        self.taxRate     = 0.002;
        self.sScrNoList  = {};

        self.errCodes = {
            -12 : "실패",
            -11 : "조건식번호 없음",
            -12 : "조건식번호와 조건식 불일치",

            -100: "사용자정보교환 실패",
            -101: "서버 접속 실패",
            -102: "버전처리 실패",
            -103: "개인방화벽 실패",
            -104: "메모리 보호 실패",
            -105: "함수 입력값 오류",
            -106: "통신연결 종료",
            -107: "보안모듈 오류",
            -108: "공인인증 로그인 필요",

            -200: "시세조회 과부하",
            -201: "전문작성 초기화 실패",
            -202: "전문작성 입력값 오류",
            -203: "데이터 없음",
            -204: "조회가능한 종목수 초과(한번에 조회 가능한 종목개수는 최대 100종목)",
            -205: "데이터 수신실패",
            -206: "조회가능한 FID수 초과(한번에 조회 가능한 FID개수는 최대 100개)",
            -207: "실시간 해제오류",
            -209: "시세조회 제한",
            -211: "1초 이내에 조회 요청이 5회를 초과하였습니다. 잠시 기다려주십시오.",

            -300: "입력값 오류",
            -301: "계좌비밀번호 없음",
            -302: "타인계좌 사용오류",
            -303: "주문가격이 주문착오 금액기준 초과",
            -304: "주문가격이 주문착오 금액기준 초과",
            -305: "주문수량이 총발행주수의 1% 초과 오류",
            -306: "주문수량이 총발행주수의 3% 조과 오류",
            -307: "주문전송 실패",
            -308: "주문전송 과부하",
            -309: "주문수량 300계약 초과",
            -310: "주문수량 500계약 초과",
            -311: "주문전송제한 과부하",
            -340: "계좌정보 없음",

            -500: "종목코드 없음",

            -10000: "계좌정보를 선택하여 주십시오.",
            -10001: "조건식을 선택하여 주십시오.",
            -10002: "동일 조건식에 대한 조건검색 요청은 1분에 1회로 제한됩니다.\r\n(프로그램 재시작이 제한시간 초기화 됩니다.)",
            -10003: "OpenAPI 모듈에 비밀번호 등록이 되어 있지 않습니다.\r\n(OpenAPI에 비밀번호 등록 또는 전체계좌에 등록 후 시도하시기 바랍니다.)",
        };
    
    ##오류코드별 메세지
    def getErrMsg(self, errCode):
        errMsg = "알 수 없는 오류가 발생하였습니다.";

        try:
            errMsg = self.errCodes[errCode];
        except:
            print("KiwoomAPI: 알 수 없는 오류코드가 발생하였습니다.(errCode: {0})".format(errCode));
        
        return errMsg;

    ##연결상태
    def isConnected(self):
        self.isLogin = (True if self.api.dynamicCall("GetConnectState()") == 1 else False);
        return self.isLogin;
    
    ##로그인 처리
    def login(self):
        self.api.dynamicCall("CommConnect()");
        if not self.onEventConnectLoop.isRunning():
            self.onEventConnectLoop.exec_();
        return self.isConnected();

    ##로그아웃 처리(지원하지 않음)
    def logout(self):
        return self.api.dynamicCall("CommTerminate()");

    ##로그인 처리 콜백
    def onEventConnect(self, errCode):
        if errCode == 0:
            self.isLogin = True;
            self.userInfo = UserInfo(
                accountCnt    = self.api.dynamicCall("GetLoginInfo(String)", "ACCOUNT_CNT"),
                accountList   = self.api.dynamicCall("GetLoginInfo(String)", "ACCLIST").split(";")[:-1],
                userId        = self.api.dynamicCall("GetLoginInfo(String)", "USER_ID"),
                userName      = self.api.dynamicCall("GetLoginInfo(String)", "USER_NAME"),
                keyBsecgb     = self.api.dynamicCall("GetLoginInfo(String)", "KEY_BSECGB"),
                firewSecgb    = self.api.dynamicCall("GetLoginInfo(String)", "FIREW_SECGB"),
                getServerGubun= self.api.dynamicCall("GetLoginInfo(String)", "GetServerGubun"),
            );

            if self.userInfo.getServerGubun != "1":
                self.buyTaxRate  = 0.00015;
                self.setlTaxRate = 0.00015;

            msg = "로그인처리 성공...";
            self.loginSignal.emit(self.isLogin);
        else:
            self.isLogin = False;
            msg = "로그인처리 실패...(errCode: {0})".format(errCode);
            self.loginSignal.emit(self.isLogin);
        
        self.apiMsgSignal.emit({
            "sScrNo" : "9999",
            "sRQName": "시스템",
            "sTrCode": "",
            "sMsg"   : msg,
        });
        
        if self.onEventConnectLoop.isRunning():
            self.onEventConnectLoop.exit();

    ##사용자 기본정보 가져오기
    def getUserInfo(self):
        if not self.isConnected():
            self.login();
        return self.userInfo;

    ##Tr 요청처리
    def reqCommRqData(self, reqParams):        
        sTrCode = reqParams["sTrCode"];
        input   = reqParams["input"];
        output  = reqParams["output"];
        sScrNo  = reqParams.get("sScrNo", "9000");
        sRQName = reqParams.get("sRQName", sTrCode);
        next    = reqParams.get("next", 0);
        
        self.reminingParams     = reqParams;
        self.trOutput           = output;
        self.receiveTrDataMulti = False;

        for id, value in input.items():
            self.api.dynamicCall("SetInputValue(QString, QString)", id, value);
        
        result = self.api.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, next, sScrNo);
        
        self.apiMsgSignal.emit({
            "sScrNo" : sScrNo,
            "sRQName": sRQName,
            "sTrCode": sTrCode,
            "sMsg"   : ("{0} 요청이 {1}하였습니다({2})").format(sTrCode, "성공" if result == 0 else "실패", result),
        });

        if result == 0:
            if not self.onReceiveTrDataLoop.isRunning():
                self.onReceiveTrDataLoop.exec_();
        else:
            self.trOutput = result;

        return self.trOutput;

    ##Tr 요청처리 콜백(단건, 다건조회시 동일한 콜백을 사용하고 있어 parameter로 구분해 처리해야 한다.)
    #sScrNo,       // 화면번호
    #sRQName,      // 사용자 구분명
    #sTrCode,      // TR이름
    #sRecordName,  // 레코드 이름
    #sPrevNext,    // 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 2:연속(추가조회) 데이터 있음
    def onReceiveTrData(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        rows = self.api.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName);
        rows = rows if rows != 0 else 1;
            
        if sTrCode not in ("KOA_NORMAL_BUY_KP_ORD" , "KOA_NORMAL_BUY_KQ_ORD", 
                           "KOA_NORMAL_SELL_KP_ORD", "KOA_NORMAL_SELL_KQ_ORD",
                           "KOA_NORMAL_KP_CANCEL"  , "KOA_NORMAL_KQ_CANCEL",
                           "KOA_NORMAL_KP_MODIFY"  , "KOA_NORMAL_KQ_MODIFY"):
            if self.receiveTrDataMulti:
                rowData = self.reminingDatas if self.reminingDatas != None else [];
                for row in range(rows):
                    instance = type("wrapper", self.trOutput.__class__.__bases__, dict(self.trOutput.__class__.__dict__));
                    wrapper = instance();
                    for key, value in wrapper.getFieldDesc().items():
                        wrapper.__setattr__(key, self.api.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, row, value).strip());
                    rowData.append(wrapper);
                self.reminingDatas = rowData;
            else:
                rowData = self.reminingDatas if self.reminingDatas != None else {};
                
                for row in range(rows):
                    for key, value in self.trOutput.getFieldDesc().items():
                        column = rowData.get(key, []);
                        column.append(self.api.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, row, value).strip());
                        rowData[key] = column;
                self.reminingDatas = rowData;
                
            if sPrevNext == "2":
                for id, value in self.reminingParams["input"].items():
                    self.api.dynamicCall("SetInputValue(QString, QString)", id, value);
                result = self.api.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, sPrevNext, sScrNo);
            else:
                if self.receiveTrDataMulti:
                    self.trOutput = rowData;
                else:
                    self.trOutput.update(rowData);
                
                self.apiMsgSignal.emit({
                    "sScrNo" : sScrNo,
                    "sRQName": sRQName,
                    "sTrCode": "",
                    "sMsg"   : ("{0} 종목정보 검색을 처리하였습니다.").format("다건(Multiple)" if self.receiveTrDataMulti == True else "단건(Single)"),
                });
                
                self.reminingDatas = None;
                self.receiveTrDataMulti = False;

                if self.onReceiveTrDataLoop.isRunning():
                    self.onReceiveTrDataLoop.exit();
        #else:
        #    obj = {
        #        "sScrNo" : sScrNo,
        #        "sRQName": sRQName,
        #        "sTrCode": sTrCode,
        #        "orderNo": self.api.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "field").strip(),
        #    };
                
    #조건검색목록 요청처리
    def getConditionLoad(self):
        self.api.dynamicCall("GetConditionLoad()");
        if not self.onReceiveConditionVerLoop.isRunning():
            self.onReceiveConditionVerLoop.exec_();
        return self.conditions;

    #조건검색목록 요청콜백
    #iRet, // 호출 성공여부, 1: 성공, 나머지 실패
    #sMsg, // 호출결과 메시지
    def onReceiveConditionVer(self, iRet, sMsg):
        result = [];
        if iRet == 1:
            conditions = self.api.dynamicCall("GetConditionNameList()");
            conditions = conditions.split(";")[:-1];

            for condition in conditions:
                cIndex, cName = condition.split("^");
                result.append((cIndex, cName));

        self.apiMsgSignal.emit({
            "sScrNo" : "9999",
            "sRQName": "시스템",
            "sTrCode": "",
            "sMsg"   : ("조건검색목록 조회가 {0}하였습니다({1})").format("성공" if iRet == 1 else "실패", sMsg),
        });    
        
        self.conditions = result;

        if self.onReceiveConditionVerLoop.isRunning():
            self.onReceiveConditionVerLoop.exit();

    #조건검색결과 요청처리
    #sScrNo,  //화면번호
    #conName, //조건검색명
    #conId,   //조건아이디
    #nSearch, //실시간옵션. 0:조건검색만, 1:조건검색+실시간 조건검색
    def sendCondition(self, sScrNo, conName, conId, nSearch=1):
        result = self.api.dynamicCall("SendCondition(QString, QString, int, int)", sScrNo, conName, conId, nSearch);
        
        if result == 1:
            if not self.sendConditionLoop.isRunning():
                self.sendConditionLoop.exec_();
        else:
            self.searchList = None;
        
        self.apiMsgSignal.emit({
            "sScrNo" : sScrNo,
            "sRQName": "시스템",
            "sTrCode": "",
            "sMsg"   : ("{0} 조건검색결과 처리가 {1}하였습니다.({2})").format(conName, "성공" if result == 1 else "실패", result),
        });
        
        return self.searchList;

    #조건검색중지 요청처리
    #sScrNo, //화면번호
    #conName,//조건검색명
    #conId,  //조건아이디
    def sendConditionStop(self, sScrNo, conName, conId):
        self.api.dynamicCall("SendConditionStop(QString, QString, int)", sScrNo, conName, conId);
        self.apiMsgSignal.emit({
            "sScrNo" : sScrNo,
            "sRQName": "시스템",
            "sTrCode": "",
            "sMsg"   : ("{0} 조건검색결 중지 처리를 {1}하였습니다.").format(conName, "성공"),
        });

    #조건검색결과 요청콜백
    #sScrNo,   //화면번호
    #codeList, //종목코드 리스트(종목코드가 ";"로 구분되서 전달됩니다.)
    #conName,  //조건식 이름
    #conId,    //조건 고유번호
    #nNext,    //연속조회 여부
    def onReceiveTrCondition(self, sScrNo, codeList, conName, conId, nNext):
        self.searchList = codeList.split(";")[:-1];

        for stockCode in self.searchList:
            self.setRealReg(sScrNo, stockCode);
        
        self.apiMsgSignal.emit({
            "sScrNo" : sScrNo,
            "sRQName": "시스템",
            "sTrCode": "",
            "sMsg"   : ("{0} 조건검색결 결과 수신이 성공하였습니다.").format(conName),
        });

        if self.sendConditionLoop.isRunning():
            self.sendConditionLoop.exit();

    #조건검색결과 실시간 요청콜백
    #sScrNo,   //화면번호
    #sType,    //이벤트 종류, "I":종목편입, "D", 종목이탈
    #conName,  //조건식 이름
    #conId,    //조건 고유번호
    def onReceiveRealCondition(self, sCode, sType, sConName, sConId):
        masterCodeName  = self.api.dynamicCall("GetMasterCodeName(QString)" , sCode);
        masterLastPrice = self.api.dynamicCall("GetMasterLastPrice(QString)", sCode); 
        
        self.conInOutSignal.emit({
            "stockCode": sCode[-6:],
            "stockName": masterCodeName,
            "stdPrice" : masterLastPrice,
            "type"     : sType,
        });

        if sType == "I":
            self.setRealReg("8000", sCode[-6:]);
        else:
            #모니터링을 위해서는 계속 수신해야 하는데.. 실시간조회 삭제??
            #self.setRealRemove("8000", sCode[-6:]);
            #self.setRealReg("8000", sCode[-6:]);
            pass;
        
        #수신 빈도가 높아서 임시로 보류
        #self.apiMsgSignal.emit({
        #    "sScrNo" : "9999",
        #    "sRQName": "시스템",
        #    "sTrCode": "",
        #    "sMsg"   : ("조건검색결과({0})에 {1}: {2}({3})").format(sConName, "(+)종목편입" if sType == "I" else "(-)종목이탈", masterCodeName, sCode[-6:]),
        #});

        #self.writeLog("condition", logCondition({
        #    "conId": sConId,
        #    "conNm": sConName,
        #    "f302" : masterCodeName,
        #    "f9001": sCode[-6:],
        #    "inout": "종목편입" if sType == "I" else "종목이탈",
        #});

    #복수종목조회 요청처리
    #sArrCode,   // 조회하려는 종목코드 리스트
    #bNext,      // 연속조회 여부 0:기본값, 1:연속조회(지원안함)
    #nCodeCount, // 종목코드 갯수
    #nTypeFlag,  // 0:주식 종목, 3:선물옵션 종목
    #sRQName,    // 사용자 구분명
    #sScrNo      // 화면번호
    def reqCommKwRqData(self, reqParams):
        codeList = reqParams["codeList"];
        codeCnt  = reqParams["codeCnt"];
        sRQName  = reqParams.get("sRQName", "시스템");
        sScrNo   = reqParams["sScrNo"];
        output   = reqParams["output"];
        
        self.reminingParams     = reqParams;
        self.receiveTrDataMulti = True;
        self.trOutput           = output;

        self.api.dynamicCall("CommKwRqData(QString, bool, int, int, QString, QString)", codeList, 0, codeCnt, 0, sRQName, sScrNo);
        
        self.apiMsgSignal.emit({
            "sScrNo" : sScrNo,
            "sRQName": sRQName,
            "sTrCode": "",
            "sMsg"   : ("다건(Multiple) {0}건의 종목정보 검색을 요청하였습니다").format(len(codeList.split(";"))),
        });
        
        self.onReceiveTrDataLoop = QtCore.QEventLoop()
        if not self.onReceiveTrDataLoop.isRunning():
            self.onReceiveTrDataLoop.exec_();
        
        return self.trOutput;

    #실시간 데이터 요청 등록처리
    #sScrNo,   // 화면 번호
    #sCodeList,// 종목코드 목록
    #sFidList, // 실시간 데이터 조회 목록
    #sOptType, // 0: 기존등록된 대상은 삭제 후, 현재 종목만 실시간 조회, 1: 기존 종목들에 추가로 등록
    def setRealReg(self, sScrNo, sCodeList, sFidList="9001;302;10;307;11;12;13;228;305;306", sOptType="0"):
        if not sScrNo in self.sScrNoList:
            self.sScrNoList[sScrNo] = [sScrNo];
        
        for stockCode in sCodeList.split(";"):
            isRegister = False;
            for scr in self.sScrNoList[sScrNo]:
                isRegister = (scr, stockCode) in self.realReceiveList;
                if isRegister:
                    break;
            
            if not isRegister:
                saveScrNo = sScrNo;
                if 100 <= len(list((rScrNo, rStockCode) for rScrNo, rStockCode in self.realReceiveList if rScrNo == self.sScrNoList[sScrNo][-1])):
                    saveScrNo = str(int(self.sScrNoList[sScrNo][-1]) + 1);
                    self.sScrNoList[sScrNo].append(saveScrNo);
                    sOptType  = "0";
                else:
                    sOptType  = "1";

                self.api.dynamicCall("SetRealReg(QString, QString, QString, QString)", saveScrNo, stockCode, sFidList, sOptType);
                self.realReceiveList.add((sScrNo, stockCode));
           
    #실시간 데이터 요청 삭제처리(SetRealReg로 등록한 대상만 해제 가능)
    #(CommRqData, CommKwRqData등 상세정보 호출과 동시에 실시간 수신하는 항목은 sScrNo전체를 비워줘야 함 SetRealRemove("화면번호","ALL"))
    #sScrNo,   // 화면 번호
    #sDelCode, // 삭제하려는 종목 코드
    def setRealRemove(self, sScrNo="8000", sDelCode="ALL"):
        if sScrNo in self.sScrNoList:
            if sDelCode == "ALL":
                for s in self.sScrNoList[sScrNo]:
                    removeTargets = set(list((rScrNo, rStockCode) for rScrNo, rStockCode in self.realReceiveList if rScrNo == s));
                    self.realReceiveList = self.realReceiveList.difference(removeTargets);
                    self.api.dynamicCall("SetRealRemove(QString, QString)", s, sDelCode);
                del(self.sScrNoList[sScrNo]);
            else:
                for s in self.sScrNoList[sScrNo]:
                    if (s, sDelCode) in self.realReceiveList:
                        self.realReceiveList.remove((s, sDelCode));
                        self.api.dynamicCall("SetRealRemove(QString, QString)", sScrNo, sDelCode);
            
    #전체 또는 화면번호 내 실시간 데이터 요청 삭제
    #sScrNo, // 화면번호
    def setRealClear(self, sScrNo=None):
        if sScrNo != None:
            self.setRealRemove(sScrNo);
        else:
            for targetScrNo in list(scrNo for scrNo, stockCode in self.realReceiveList):
                self.setRealRemove(targetScrNo, "ALL");

    #실시간 데이터 수신 콜백
    #sCode,     //종목코드
    #sRealType, //실시간타입
    #sRealData, //사용안함
    def onReceiveRealData(self, sCode, sRealType, sRealData):
        obj = {
            "sRealType": sRealType                                                                                    , #실시간유형
            "stockCode": sCode[-6:]                                                                                   , #종목코드
            "f9001"    : sCode[-6:]                                                                                   , #종목코드
            "f302"     : self.api.dynamicCall("GetMasterCodeName(QString)", sCode)                                    , #종목명
            "f307"     : self.api.dynamicCall("GetMasterLastPrice(QString)", sCode).replace("-", "")                  , #기준가
            "f920"     : ";".join(list(scrNo for scrNo, stockCode in self.realReceiveList if stockCode == sCode[-6:])), #화면번호
        };
        
        if sRealType == "주식시세":
            obj["rType"] = "01";
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  10); #현재가
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  12); #등락율
            obj["f27"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  27); #(최우선)매도호가
            obj["f28"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  28); #(최우선)매수호가
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  14); #누적거래대금
            obj["f16"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  16); #시가
            obj["f17"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  17); #고가
            obj["f18"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  18); #저가
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  25); #전일대비기호
            obj["f26"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  26); #전일거래량대비(계약,주)
            obj["f29"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  29); #거래대금증감
            obj["f30"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  30); #전일거래량대비(비율)
            obj["f31"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  31); #거래회전율
            obj["f32"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  32); #거래비용
            obj["f311" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 311); #시가총액(억)
            obj["f567" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 567); #상한가발생시간
            obj["f568" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 568); #하한가발생시간
        
        elif sRealType == "주식체결":
            obj["rType"] = "02";
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  20); #체결시간
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  10); #현재가
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  12); #등락율
            obj["f27"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  27); #(최우선)매도호가
            obj["f28"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  28); #(최우선)매수호가
            obj["f15"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  15); #거래량(+는 매수체결, -는 매도체결)
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  14); #누적거래대금
            obj["f16"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  16); #시가
            obj["f17"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  17); #고가
            obj["f18"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  18); #저가
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  25); #전일대비기호
            obj["f26"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  26); #전일거래량대비(계약,주)
            obj["f29"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  29); #거래대금증감
            obj["f30"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  30); #전일거래량대비(비율)
            obj["f31"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  31); #거래회전율
            obj["f32"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  32); #거래비용
            obj["f228" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 228); #체결강도
            obj["f311" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 311); #시가총액(억)
            obj["f290" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 290); #장구분
            obj["f691" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 691); #KO접근도
            obj["f567" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 567); #상한가발생시간
            obj["f568" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 568); #하한가발생시간
            obj["f851" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 851); #전일 동시간 거래량 비율
        
        elif sRealType == "장시작시간":
            obj["rType"] = "07";
            obj["f215" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 215); #장운영구분
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  20); #체결시간
            obj["f214" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 214); #장시작예상잔여시간
        
        elif sRealType == "업종지수":
            obj["rType"] = "10";
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 20); #체결시간
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10); #현재가
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 12); #등락율
            obj["f15"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 15); #거래량(+는 매수체결, -는 매도체결)
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 14); #누적거래대금
            obj["f16"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 16); #시가
            obj["f17"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 17); #고가
            obj["f18"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 18); #저가
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 25); #전일대비기호
            obj["f26"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 26); #전일거래량대비(계약,주)

        """
        elif sRealType == "주식우선호가":
            obj["rType"] = "03";
            obj["f21"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  21); #호가시간
            obj["f41"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  41); #매도호가1
            obj["f61"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  61); #매도호가수량1
            obj["f81"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  81); #매도호가직전대비1
            obj["f51"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  51); #매수호가1
            obj["f71"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  71); #매수호가수량1
            obj["f91"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  91); #매수호가직전대비1
            obj["f42"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  42); #매도호가2
            obj["f62"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  62); #매도호가수량2
            obj["f82"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  82); #매도호가직전대비2
            obj["f52"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  52); #매수호가2
            obj["f72"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  72); #매수호가수량2
            obj["f92"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  92); #매수호가직전대비2
            obj["f43"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  43); #매도호가3
            obj["f63"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  63); #매도호가수량3
            obj["f83"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  83); #매도호가직전대비3
            obj["f53"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  53); #매수호가3
            obj["f73"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  73); #매수호가수량3
            obj["f93"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  93); #매수호가직전대비3
            obj["f44"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  44); #매도호가4
            obj["f64"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  64); #매도호가수량4
            obj["f84"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  84); #매도호가직전대비4
            obj["f54"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  54); #매수호가4
            obj["f74"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  74); #매수호가수량4
            obj["f94"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  94); #매수호가직전대비4
            obj["f45"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  45); #매도호가5
            obj["f65"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  65); #매도호가수량5
            obj["f85"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  85); #매도호가직전대비5
            obj["f55"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  55); #매수호가5
            obj["f75"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  75); #매수호가수량5
            obj["f95"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  95); #매수호가직전대비5
            obj["f46"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  46); #매도호가6
            obj["f66"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  66); #매도호가수량6
            obj["f86"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  86); #매도호가직전대비6
            obj["f56"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  56); #매수호가6
            obj["f76"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  76); #매수호가수량6
            obj["f96"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  96); #매수호가직전대비6
            obj["f47"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  47); #매도호가7
            obj["f67"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  67); #매도호가수량7
            obj["f87"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  87); #매도호가직전대비7
            obj["f57"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  57); #매수호가7
            obj["f77"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  77); #매수호가수량7
            obj["f97"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  97); #매수호가직전대비7
            obj["f48"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  48); #매도호가8
            obj["f68"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  68); #매도호가수량8
            obj["f88"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  88); #매도호가직전대비8
            obj["f58"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  58); #매수호가8
            obj["f78"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  78); #매수호가수량8
            obj["f98"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  98); #매수호가직전대비8
            obj["f49"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  49); #매도호가9
            obj["f69"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  69); #매도호가수량9
            obj["f89"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  89); #매도호가직전대비9
            obj["f59"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  59); #매수호가9
            obj["f79"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  79); #매수호가수량9
            obj["f99"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  99); #매수호가직전대비9
            obj["f50"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  50); #매도호가10
            obj["f70"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  70); #매도호가수량10
            obj["f90"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  90); #매도호가직전대비10
            obj["f60"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  60); #매수호가10
            obj["f80"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  80); #매수호가수량10
            obj["f100" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 100); #매수호가직전대비10
            obj["f121" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 121); #매도호가총잔량
            obj["f122" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 122); #매도호가총잔량직전대비
            obj["f125" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 125); #매수호가총잔량
            obj["f126" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 126); #매수호가총잔량직전대비
            obj["f23"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  23); #예상체결가
            obj["f24"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  24); #예상체결수량
            obj["f128" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 128); #순매수잔량
            obj["f129" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 129); #매수비율
            obj["f138" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 138); #순매도잔량
            obj["f139" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 139); #매도비율
            obj["f200" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 200); #예상체결가전일종가대비
            obj["f201" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 201); #예상체결가전일종가대비등락율
            obj["f238" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 238); #예상체결가전일종가대비기호
            obj["f291" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 291); #예상체결가(예상체결 시간동안에만 유효한 값)
            obj["f292" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 292); #예상체결량
            obj["f293" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 293); #예상체결가전일대비기호
            obj["f294" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 294); #예상체결가전일대비
            obj["f295" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 295); #예상체결가전일대비등락율
            obj["f621" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 621); #LP매도호가수량1
            obj["f631" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 631); #LP매수호가수량1
            obj["f622" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 622); #LP매도호가수량2
            obj["f632" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 632); #LP매수호가수량2
            obj["f623" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 623); #LP매도호가수량3
            obj["f633" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 633); #LP매수호가수량3
            obj["f624" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 624); #LP매도호가수량4
            obj["f634" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 634); #LP매수호가수량4
            obj["f625" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 625); #LP매도호가수량5
            obj["f635" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 635); #LP매수호가수량5
            obj["f626" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 626); #LP매도호가수량6
            obj["f636" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 636); #LP매수호가수량6
            obj["f627" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 627); #LP매도호가수량7
            obj["f637" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 637); #LP매수호가수량7
            obj["f628" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 628); #LP매도호가수량8
            obj["f638" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 638); #LP매수호가수량8
            obj["f629" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 629); #LP매도호가수량9
            obj["f639" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 639); #LP매수호가수량9
            obj["f630" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 630); #LP매도호가수량10
            obj["f640" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 640); #LP매수호가수량10
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  13); #누적거래량
            obj["f299" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 299); #전일거래량대비예상체결률
            obj["f215" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 215); #장운영구분
            obj["f216" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 216); #투자자별ticker
        
        elif sRealType == "주식호가잔량":
            obj["rType"] = "04";
            obj["f215" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 27); #장운영구분
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 28); #체결시간
        
        elif sRealType == "주식시간외호가":
            obj["rType"] = "05";
            obj["f215" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 27); #장운영구분
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 28); #체결시간

        elif sRealType == "주식당일거래원":
            obj["rType"] = "06";
            obj["f141" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 141); #매도거래원1
            obj["f161" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 161); #매도거래원수량1
            obj["f166" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 166); #매도거래원별증감1
            obj["f146" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 146); #매도거래원코드1
            obj["f271" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 271); #매도거래원색깔1
            obj["f151" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 151); #매수거래원1
            obj["f171" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 171); #매수거래원수량1
            obj["f176" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 176); #매수거래원별증감1
            obj["f156" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 156); #매수거래원코드1
            obj["f281" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 281); #매수거래원색깔1
            obj["f142" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 142); #매도거래원2
            obj["f162" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 162); #매도거래원수량2
            obj["f167" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 167); #매도거래원별증감2
            obj["f147" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 147); #매도거래원코드2
            obj["f272" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 272); #매도거래원색깔2
            obj["f152" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 152); #매수거래원2
            obj["f172" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 172); #매수거래원수량2
            obj["f177" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 177); #매수거래원별증감2
            obj["f157" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 157); #매수거래원코드2
            obj["f282" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 282); #매수거래원색깔2
            obj["f143" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 143); #매도거래원3
            obj["f163" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 163); #매도거래원수량3
            obj["f168" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 168); #매도거래원별증감3
            obj["f148" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 148); #매도거래원코드3
            obj["f273" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 273); #매도거래원색깔3
            obj["f153" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 153); #매수거래원3
            obj["f173" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 173); #매수거래원수량3
            obj["f178" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 178); #매수거래원별증감3
            obj["f158" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 158); #매수거래원코드3
            obj["f283" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 283); #매수거래원색깔3
            obj["f144" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 144); #매도거래원4
            obj["f164" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 164); #매도거래원수량4
            obj["f169" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 169); #매도거래원별증감4
            obj["f149" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 149); #매도거래원코드4
            obj["f274" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 274); #매도거래원색깔4
            obj["f154" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 154); #매수거래원4
            obj["f174" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 174); #매수거래원수량4
            obj["f179" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 179); #매수거래원별증감4
            obj["f159" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 159); #매수거래원코드4
            obj["f284" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 284); #매수거래원색깔4
            obj["f145" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 145); #매도거래원5
            obj["f165" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 165); #매도거래원수량5
            obj["f170" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 170); #매도거래원별증감5
            obj["f150" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 150); #매도거래원코드5
            obj["f275" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 275); #매도거래원색깔5
            obj["f155" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 155); #매수거래원5
            obj["f175" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 175); #매수거래원수량5
            obj["f180" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 180); #매수거래원별증감5
            obj["f160" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 160); #매수거래원코드5
            obj["f285" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 285); #매수거래원색깔5
            obj["f261" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 261); #외국계매도추정합
            obj["f262" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 262); #외국계매도추정합변동
            obj["f263" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 263); #외국계매수추정합
            obj["f264" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 264); #외국계매수추정합변동
            obj["f267" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 267); #외국계순매수추정합
            obj["f268" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 268); #외국계순매수변동
            obj["f337" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 337); #거래소구분
        """
        """
        elif sRealType == "주식예상체결":
            obj["rType"] = "08";
            obj["f20" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 20); #체결시간
            obj["f10" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10); #현재가
            obj["f11" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 11); #전일대비
            obj["f12" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 12); #등락율
            obj["f14" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 14); #거래량(+는 매수체결, -는 매도체결)
            obj["f13" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 13); #누적거래량
            obj["f25" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 25); #전일대비기호
        
        elif sRealType == "주식종목정보":
            obj["rType"] = "09";
            obj["f297" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 297); #임의연장
            obj["f592" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 592); #장전임의연장
            obj["f593" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 593); #장후임의연장
            obj["f305" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 305); #상한가
            obj["f306" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 306); #하한가
            obj["f307" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 307); #기준가
            obj["f689" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 689); #조기종료ELW발생
            obj["f594" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 594); #통화단위
            obj["f382" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 382); #증거금율표시
            obj["f370" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 370); #종목정보
            obj["f300" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 300); #Extra Item
        
        elif sRealType == "업종지수":
            obj["rType"] = "10";
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 20); #체결시간
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10); #현재가
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 12); #등락율
            obj["f15"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 15); #거래량(+는 매수체결, -는 매도체결)
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 14); #누적거래대금
            obj["f16"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 16); #시가
            obj["f17"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 17); #고가
            obj["f18"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 18); #저가
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 25); #전일대비기호
            obj["f26"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 26); #전일거래량대비(계약,주)
        
        elif sRealType =="업종등락":
            obj["rType"] = "11";
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  20); #체결시간
            obj["f252" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 252); #상승종목수
            obj["f251" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 251); #상한종목수
            obj["f253" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 253); #보합종목수
            obj["f255" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 255); #하락종목수
            obj["f254" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 254); #하한종목수
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  14); #누적거래대금
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  10); #현재가
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  12); #등락율
            obj["f256" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 256); #거래형성종목수
            obj["f257" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 257); #거래형성비율
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  25); #전일대비기호
        
        elif sRealType == "VI발동/해제":
            obj["rType"] = "12";
            obj["f9001"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9001); #종목코드,업종코드
            obj["f302" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  302); #종목명
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   13); #누적거래량
            obj["f14"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   14); #누적거래대금
            obj["f9068"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9068); #VI발동구분
            obj["f9008"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9008); #KOSPI,KOSDAQ,전체구분
            obj["f9075"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9075); #장전구분
            obj["f1221"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1221); #VI 발동가격
            obj["f1223"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1223); #매매체결처리시각
            obj["f1224"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1224); #VI 해제시각
            obj["f1225"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1225); #VI 적용구분(정적/동적/동적+정적)
            obj["f1236"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1236); #기준가격 정적
            obj["f1237"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1237); #기준가격 동적
            obj["f1238"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1238); #괴리율 정적
            obj["f1239"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1239); #괴리율 동적
            obj["f1489"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1489); #VI발동가 등락률
            obj["f1490"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1490); #VI발동횟수
            obj["f9069"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9069); #발동방향구분
            obj["f1279"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 1279); #Extra Item
        
        elif sRealType == "주문체결":
            obj["rType"] = "13";
            obj["f9201"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9201); #계좌번호
            obj["f9203"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9203); #주문번호
            obj["f9205"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9205); #관리자사번
            obj["f9001"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9001); #종목코드,업종코드
            obj["f912" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  912); #주문업무분류
            obj["f913" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  913); #주문상태
            obj["f302" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  302); #종목명
            obj["f900" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  900); #주문수량
            obj["f901" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  901); #주문가격
            obj["f902" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  902); #미체결수량
            obj["f903" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  903); #체결누계금액
            obj["f904" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  904); #원주문번호
            obj["f905" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  905); #주문구분
            obj["f906" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  906); #매매구분
            obj["f907" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  907); #매도수구분
            obj["f908" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  908); #주문/체결시간
            obj["f909" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  909); #체결번호
            obj["f910" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  910); #체결가
            obj["f911" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  911); #체결량
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   10); #현재가
            obj["f27"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   27); #(최우선)매도호가
            obj["f28"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   28); #(최우선)매수호가
            obj["f914" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  914); #단위체결가
            obj["f915" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  915); #단위체결량
            obj["f938" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  938); #당일매매수수료
            obj["f939" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  939); #당일매매세금
            obj["f919" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  919); #거부사유
            obj["f920" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  920); #화면번호
            obj["f921" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  921); #터미널번호
            obj["f922" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  922); #신용구분(실시간 체결용)
            obj["f923" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  923); #대출일(실시간 체결용)
        
        elif sRealType == "잔고":
            obj["rType"] = "14";
            obj["f9201"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9201); #계좌번호
            obj["f9001"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 9001); #종목코드,업종코드
            obj["f917" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  917); #신용구분
            obj["f916" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  916); #대출일
            obj["f302" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  302); #종목명
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   10); #현재가
            obj["f930" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  930); #보유수량
            obj["f931" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  931); #매입단가
            obj["f932" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  932); #총매입가(당일누적)
            obj["f933" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  933); #주문가능수량
            obj["f945" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  945); #당일순매수량
            obj["f946" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  946); #매도/매수구분
            obj["f950" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  950); #당일총매도손익
            obj["f951" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  951); #Extra Item
            obj["f27"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   27); #(최우선)매도호가
            obj["f28"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,   28); #(최우선)매수호가
            obj["f307" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  307); #기준가
            obj["f8019"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 8019); #손익율(실현손익)
            obj["f957" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  957); #신용금액
            obj["f958" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  958); #신용이자
            obj["f918" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  918); #만기일
            obj["f990" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  990); #당일실현손익(유가)
            obj["f991" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  991); #당일실현손익률(유가)
            obj["f992" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  992); #당일실현손익(신용)
            obj["f993" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  993); #당일실현손익률(신용)
            obj["f959" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  959); #담보대출수량
            obj["f924" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  924); #Extra Item
        
        elif sRealType == "종목프로그램매매":
            obj["rType"] = "15";
            obj["f20"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  20); #체결시간
            obj["f10"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  10); #현재가
            obj["f25"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  25); #전일대비기호
            obj["f11"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  11); #전일대비
            obj["f12"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  12); #등락율
            obj["f13"  ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode,  13); #누적거래량
            obj["f202" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 202); #매도수량
            obj["f204" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 204); #매도금액
            obj["f206" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 206); #매수수량
            obj["f208" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 208); #매수금액
            obj["f210" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 210); #순매수수량
            obj["f211" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 211); #순매수수량증감
            obj["f212" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 212); #순매수금액
            obj["f213" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 213); #순매수금액증감
            obj["f214" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 214); #장시작예상잔여시간
            obj["f215" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 215); #장운영구분
            obj["f216" ] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 216); #투자자별ticker
        elif sRealType == "ECN주식체결":
            #ECN주식체결, ECN주식호가잔량은.. 14:00 시작하는 장마감 후 시간외거래 데이터임(현재지원하지 않음)
            obj["rType"] = "16";
            obj["f10010"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10010); #???
            obj["f10011"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10011); #???
            obj["f10012"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10012); #???
            obj["f10027"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10027); #???
            obj["f10028"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10028); #???
            obj["f10013"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10013); #???
            obj["f10014"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10014); #???
            obj["f10016"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10016); #???
            obj["f10017"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10017); #???
            obj["f10018"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10018); #???
            obj["f10025"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10025); #???
        elif sRealType == "ECN주식호가잔량":
            obj["rType"] = "17";
            #ECN주식체결, ECN주식호가잔량은.. 14:00 시작하는 장마감 후 시간외거래 데이터임(현재지원하지 않음)
            obj["f10021"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10021); #???
            obj["f10041"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10041); #???
            obj["f10042"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10042); #???
            obj["f10043"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10043); #???
            obj["f10044"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10044); #???
            obj["f10045"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10045); #???
            obj["f10061"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10061); #???
            obj["f10062"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10062); #???
            obj["f10063"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10063); #???
            obj["f10064"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10064); #???
            obj["f10065"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10065); #???
            obj["f10081"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10081); #???
            obj["f10082"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10082); #???
            obj["f10083"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10083); #???
            obj["f10084"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10084); #???
            obj["f10085"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10085); #???
            obj["f10051"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10051); #???
            obj["f10052"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10052); #???
            obj["f10053"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10053); #???
            obj["f10054"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10054); #???
            obj["f10055"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10055); #???
            obj["f10071"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10071); #???
            obj["f10072"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10072); #???
            obj["f10073"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10073); #???
            obj["f10074"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10074); #???
            obj["f10075"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10075); #???
            obj["f10091"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10091); #???
            obj["f10092"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10092); #???
            obj["f10093"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10093); #???
            obj["f10094"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10094); #???
            obj["f10095"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10095); #???
            obj["f10121"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10121); #???
            obj["f10122"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10122); #???
            obj["f10125"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10125); #???
            obj["f10126"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10126); #???
            obj["f10023"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10023); #???
            obj["f10024"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10024); #???
            obj["f10035"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10035); #???
            obj["f10033"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10033); #???
            obj["f10034"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10034); #???
        
        elif sRealType == "시간외종목정보":
            obj["rType"] = "18";
            obj["f10297"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10297); #???
            obj["f10305"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10304); #???
            obj["f10306"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10306); #???
            obj["f10307"] = self.api.dynamicCall("GetCommRealData(QString, int)", sCode, 10307); #???

        else:
            obj["rType"] = "99";
            print("처리되지 않는 type: '{0}'입니다 ".format(sRealType));
        """
        if "f10" in obj:
            obj["f10"] = obj["f10"].replace("-", "");
        
        #주식우선호가(매수/매도 1호가 가격이 변경되면 전달) 데이터가 너무 많이 온다.. 화면 버벅임..
        #사용하지 않는 실시간 데이터는 로그로 저장하지 않는다(부하가 많을때 처리량이 밀림)
        if sRealType in ["주식체결", "장시작시간", "업종지수"]:
            self.stockSignal.emit(obj);
            #틱 거래정보 로그를 남길 필요가 있을까??
            #self.writeLog("real", obj);
    
    #키움서버에서 수신된 메세지
    #sScrNo,  //화면번호
    #sRQName, //사용자 구분명
    #sTrCode, //TR이름
    #sMsg,    //kiwoom서버에서 전달받은 메세지
    def onReceiveMsg(self, sScrNo, sRQName, sTrCode, sMsg):
        sMsg = sMsg.strip();
        #모의투자 제한종목이거나, 취소주문에 수량이나 취소주문 찰나에 체결 되어 원주문이 없을때.. 여기로 결과가 반환된다.
        #근데.. 주문에 대한 정보가 없는데?? 어케 알지..
        #100000: 정상
        #RC4007: 모의투자 매매제한 종목입니다.
        #RC4033: 모의투자 정정/취소할 수량이 없습니다.
        msgCode = "100000" if "100000" in sMsg else sMsg[1:7];

        if msgCode != "100000" and sMsg != "조회가 완료되었습니다.":
            self.apiMsgSignal.emit({
                "sScrNo" : sScrNo,
                "sRQName": sRQName,
                "sTrCode": sTrCode,
                "sMsg"   : "{0} (message from kiwoom Server...)".format(sMsg),
            });

        self.writeLog("kiwoom", {
            "f920"   : sScrNo,
            "sTrCode": sTrCode,
            "msg"    : sMsg,
        });
    
    #매수주문 요청
    #BSTR sRQName,    // 사용자 구분명
    #BSTR sScreenNo,  // 화면번호
    #BSTR sAccNo,     // 계좌번호 10자리
    #LONG nOrderType, // 주문유형 1:+매수, 2:-매도 3:매수취소, 4:매도취소, 5:매수정정, 6:매도정정
    #BSTR sCode,      // 종목코드 (6자리)
    #LONG nQty,       // 주문수량
    #LONG nPrice,     // 주문가격
    #BSTR sHogaGb,    // 거래구분(혹은 호가구분)은 아래 참고
    #BSTR sOrgOrderNo // 원주문번호. 신규주문에는 공백 입력, 정정/취소시 입력합니다.
    #      서버에 주문을 전송하는 함수 입니다.
    #      9개 인자값을 가진 주식주문 함수이며 리턴값이 0이면 성공이며 나머지는 에러입니다.
    #      1초에 5회만 주문가능하며 그 이상 주문요청하면 에러 -308을 리턴합니다.
    #      ※ 시장가주문시 주문가격은 0으로 입력합니다. 주문가능수량은 해당 종목의 상한가 기준으로 계산됩니다.
    #      ※ 취소주문일때 주문가격은 0으로 입력합니다.
    #      
    #      [거래구분]
    #      00 : 지정가
    #      03 : 시장가
    #      05 : 조건부지정가
    #      06 : 최유리지정가
    #      07 : 최우선지정가
    #      10 : 지정가IOC
    #      13 : 시장가IOC
    #      16 : 최유리IOC
    #      20 : 지정가FOK
    #      23 : 시장가FOK
    #      26 : 최유리FOK
    #      61 : 장전시간외종가
    #      62 : 시간외단일가매매
    #      81 : 장후시간외종가
    #      ※ 모의투자에서는 지정가 주문과 시장가 주문만 가능합니다.
    #      
    #      [정규장 외 주문]
    #      장전 동시호가 주문
    #          08:30 ~ 09:00.	거래구분 00:지정가/03:시장가 (일반주문처럼)
    #          ※ 08:20 ~ 08:30 시간의 주문은 키움에서 대기하여 08:30 에 순서대로 거래소로 전송합니다.
    #      장전시간외 종가
    #          08:30 ~ 08:40. 	거래구분 61:장전시간외종가.  가격 0입력
    #          ※ 전일 종가로 거래. 미체결시 자동취소되지 않음
    #      장마감 동시호가 주문
    def sendOrder(self, paramsMap):
        sRQName     = paramsMap.get("sRQName"    , "주문요청");
        sScrNo      = paramsMap.get("sScrNo"     , "3000");
        sHogaGb     = paramsMap.get("sHogaGb"    , "00");#거래구분(sHogaGb) 00: 지정가, 03: 시장가
        sOrgOrderNo = paramsMap.get("sOrgOrderNo", "");
        sAccNo      = paramsMap["sAccNo"];
        nOrderType  = paramsMap["nOrderType"];
        sCode       = paramsMap["sCode"];
        nQty        = paramsMap["nQty"];
        nPrice      = paramsMap["nPrice"];
        reason      = paramsMap["reason"];
        
        masterCodeName = self.api.dynamicCall("GetMasterCodeName(QString)", sCode);
        result = self.api.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [sRQName, sScrNo, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo]);
        
        if result == 0:
            #self.apiMsgSignal.emit({
            #    "sScrNo" : sScrNo,
            #    "sRQName": sRQName,
            #    "sTrCode": sCode,
            #    "sMsg"   : "{0}({1})를 {2}({3})주를 {4} 신청하였습니다.(result:{5})".format(masterCodeName, sCode, nPrice, nQty, self.nOrderType[nOrderType], result),
            #});
                
            self.writeLog("order", {
                "f302"  : masterCodeName,
                "f9001" : sCode,
                "f901"  : nPrice,
                "f900"  : nQty,
                "f905"  : nOrderType,
                "f920"  : sScrNo,
                "reason": reason,
            });
        else:
            #self.apiMsgSignal.emit({
            #    "sScrNo" : sScrNo,
            #    "sRQName": sRQName,
            #    "sTrCode": sCode,
            #    "sMsg"   : "{0}({1})를 {2}({3})주를 {4} 신청 오류가 발생하였습니다.({5})".format(masterCodeName, sCode, nPrice, nQty, self.nOrderType[nOrderType], self.errCodes[result]),
            #});

            self.writeLog("kiwoom", {
                "f920"   : sScrNo,
                "sTrCode": "sendOrder",
                "msg"    : ("{0}({1})를 {2}({3})주를 {4} 신청 오류가 발생하였습니다.({5})").format(masterCodeName, sCode, nPrice, nQty, self.nOrderType[nOrderType], self.errCodes[result]),
            });

            result = -1;
        
        return result;
    
    #체결잔고 정보 요청
    #BSTR sGubun,   // 접수와 체결시 "0"값, 국내주식 잔고변경은 "1"값, 파생잔고변경은 "4"
    #LONG nItemCnt, // Item건수
    #BSTR sFIdList  // Fid목록
    def onReceiveChejanData(self, sGubun, nItemCnt, sFidList):
        obj = {
            "gubun": sGubun,
        };
        
        for fid in sFidList.split(";"):
            obj["f" + fid] = self.api.dynamicCall("GetChejanData(QString)", fid).strip();
        
        obj["f9001"] = obj["f9001"][-6:];#종목코드
        obj["f302" ] = self.api.dynamicCall("GetMasterCodeName(QString)", obj["f9001"]) if obj["f302"] == "" else obj["f302"].strip();#종목명
        obj["f10"  ] = obj["f10" ].replace("+","").replace("-",""); #현재가

        if obj["gubun"] == "1":   
            obj["f27" ] = obj["f27" ].replace("+","").replace("-",""); #최우선 매도호가
            obj["f28" ] = obj["f28" ].replace("+","").replace("-",""); #최우선 매수호가
            obj["f306"] = obj["f306"].replace("+","").replace("-",""); #하한가
            obj["f305"] = obj["f305"].replace("+","").replace("-",""); #상한가
        
        #주문취소, 주문정정의 마지막 echo 값으로 전달하지 않아도 된다.
        self.chejanSignal.emit(obj);
        self.writeLog("chejan", obj);
        
    #차트 같은 대용량 데이터 수신 함수
    #(ex: 주식일봉차트조회 recevei이벤트 예시)
    # code = self.api.dynamicCall("GetCommData(QString, QString, int, QString)", "opt100081", "주식일봉차트조회", 0, "종목코드").strip()
    # code = self.api.dynamicCall("GetCommDataEx(QString, QString)", "opt100081", "주식일봉차트조회");
    #BSTR strTrCode,     // TR 이름
    #BSTR sRQName, // 레코드이름
    def GetCommDataEx(self, sTrCode, sRQName):
        return self.api.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName);