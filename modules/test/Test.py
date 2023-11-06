import datetime, time;

def writeFile():
    for i in range(100000):
        with open("./testLog.log", "a", encoding="UTF-8", ) as fileData:
            txt = "[2023-11-06 13:39:06.073320:onReceiveRealData(주식체결)], 실시간타입(주식체결), 종목코드(025560), 종목코드,업종코드(025560), 종목명(미래산업            ), 기준가(00003190), 화면번호(4000               ), 실시간타입(CODE)(02), 체결시간(133904), 현재가(  +3420), 전일대비(  +230), 등락율( +7.21), (최우선)매도호가(   +3420), (최우선)매수호가(   +3415), 거래량(+는 매수체결, -는 매도체결)(   -21), 누적거래량(  1470566), 누적거래대금(         4968), 시가(   +3295), 고가(   +3475), 저가(   -3185), 전일대비기호(2), 전일거래량대비(계약,주)(   +836179), 거래대금증감(  +2970692770), 전일거래량대비(비율)( +231.81), 거래회전율(  4.83), 거래비용( 8), 체결강도(102.73), 시가총액(억)(   1041), 장구분(2), KO접근도(0), 상한가발생시간(000000), 하한가발생시간(000000), 전일 동시간 거래량 비율( 27429)";
            txt = "".join(["[", str(datetime.datetime.now()), "] ", txt]);
            fileData.write(txt + "\n");

if __name__ == "__main__":
    """
    startTime = time.perf_counter();
    writeFile();
    endTime = time.perf_counter();
    print(f"time elapsed : {int(round((endTime - startTime) * 1000))}ms");
    """
    
    startTime = time.perf_counter();
    for i in range(1000000):
        t = datetime.datetime.now();
    endTime = time.perf_counter();
    print(f"time elapsed : {int(round((endTime - startTime) * 1000))}ms");