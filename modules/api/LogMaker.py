import os, json, time, datetime, unicodedata;

class LogMaker:
    def __init__(self, parent=None, **kwargs):
        self.today_YYYYMMDD = datetime.datetime.now().strftime("%Y%m%d");
        self.logChejanDir = "logging/{0}/chejan/".format(self.today_YYYYMMDD);
        os.makedirs(os.path.dirname(self.logChejanDir), exist_ok=True);

        self.logOrderDir = "logging/{0}/order/".format(self.today_YYYYMMDD);
        os.makedirs(os.path.dirname(self.logOrderDir), exist_ok=True);

        self.logRealDir = "logging/{0}/real/".format(self.today_YYYYMMDD);
        os.makedirs(os.path.dirname(self.logRealDir), exist_ok=True);

        self.logConditionDir = "logging/{0}/condition/".format(self.today_YYYYMMDD);
        os.makedirs(os.path.dirname(self.logConditionDir), exist_ok=True);

        self.logKiwoomDir = "logging/{0}/kiwoom/".format(self.today_YYYYMMDD);
        os.makedirs(os.path.dirname(self.logKiwoomDir), exist_ok=True);

        self.nOrderType = {
            1: "신규매수",
            2: "신규매도",
            3: "매수취소",
            4: "매도취소",
            5: "매수정정",
            6: "매도정정",
        };
        
        self.fidList = {
            "reason"   : {"size": 30, "align": "<", "desc": "사유"},
            "stockCode": {"size":  6, "align":  "", "desc": "종목코드"},
            "conId"    : {"size":  3, "align": "<", "desc": "조건검색ID"},
            "conNm"    : {"size": 20, "align": ">", "desc": "조건검색명"},
            "inout"    : {"size":  4, "align": "<", "desc": "편입여부"},
            "sRealType": {"size":  8, "align": "<", "desc": "실시간타입"},
            "rType"    : {"size":  2, "align": ">", "desc": "실시간타입(CODE)"},
            "gubun"    : {"size":  1, "align":  "", "desc": "체잔구분"},
            "sTrCode"  : {"size": 22, "align": ">", "desc": "TrCode"},
            "msg"      : {"size":  0, "align":  "", "desc": "서버메세지"},
            "f10"      : {"size":  7, "align": ">", "desc": "현재가"},
            "f11"      : {"size":  6, "align": ">", "desc": "전일대비"},
            "f12"      : {"size":  6, "align": ">", "desc": "등락율"},
            "f27"      : {"size":  8, "align": ">", "desc": "(최우선)매도호가"},
            "f28"      : {"size":  8, "align": ">", "desc": "(최우선)매수호가"},
            "f13"      : {"size":  9, "align": ">", "desc": "누적거래량"},
            "f14"      : {"size": 13, "align": ">", "desc": "누적거래대금"},
            "f16"      : {"size":  8, "align": ">", "desc": "시가"},
            "f17"      : {"size":  8, "align": ">", "desc": "고가"},
            "f18"      : {"size":  8, "align": ">", "desc": "저가"},
            "f25"      : {"size":  0, "align":  "", "desc": "전일대비기호"},
            "f26"      : {"size": 10, "align": ">", "desc": "전일거래량대비(계약,주)"},
            "f29"      : {"size": 13, "align": ">", "desc": "거래대금증감"},
            "f30"      : {"size":  8, "align": ">", "desc": "전일거래량대비(비율)"},
            "f31"      : {"size":  6, "align": ">", "desc": "거래회전율"},
            "f32"      : {"size":  2, "align": ">", "desc": "거래비용"},
            "f311"     : {"size":  7, "align": ">", "desc": "시가총액(억)"},
            "f567"     : {"size":  0, "align":  "", "desc": "상한가발생시간"},
            "f568"     : {"size":  0, "align":  "", "desc": "하한가발생시간"},
            "f20"      : {"size":  0, "align":  "", "desc": "체결시간"},
            "f15"      : {"size":  6, "align": ">", "desc": "거래량(+는 매수체결, -는 매도체결)"},
            "f228"     : {"size":  6, "align": ">", "desc": "체결강도"},
            "f290"     : {"size":  1, "align":  "", "desc": "장구분"},
            "f691"     : {"size":  1, "align":  "", "desc": "KO접근도"},
            "f851"     : {"size":  6, "align": ">", "desc": "전일 동시간 거래량 비율"},
            "f21"      : {"size":  0, "align":  "", "desc": "호가시간"},
            "f41"      : {"size":  0, "align":  "", "desc": "매도호가1"},
            "f61"      : {"size":  0, "align":  "", "desc": "매도호가수량1"},
            "f81"      : {"size":  0, "align":  "", "desc": "매도호가직전대비1"},
            "f51"      : {"size":  0, "align":  "", "desc": "매수호가1"},
            "f71"      : {"size":  0, "align":  "", "desc": "매수호가수량1"},
            "f91"      : {"size":  0, "align":  "", "desc": "매수호가직전대비1"},
            "f42"      : {"size":  0, "align":  "", "desc": "매도호가2"},
            "f62"      : {"size":  0, "align":  "", "desc": "매도호가수량2"},
            "f82"      : {"size":  0, "align":  "", "desc": "매도호가직전대비2"},
            "f52"      : {"size":  0, "align":  "", "desc": "매수호가2"},
            "f72"      : {"size":  0, "align":  "", "desc": "매수호가수량2"},
            "f92"      : {"size":  0, "align":  "", "desc": "매수호가직전대비2"},
            "f43"      : {"size":  0, "align":  "", "desc": "매도호가3"},
            "f63"      : {"size":  0, "align":  "", "desc": "매도호가수량3"},
            "f83"      : {"size":  0, "align":  "", "desc": "매도호가직전대비3"},
            "f53"      : {"size":  0, "align":  "", "desc": "매수호가3"},
            "f73"      : {"size":  0, "align":  "", "desc": "매수호가수량3"},
            "f93"      : {"size":  0, "align":  "", "desc": "매수호가직전대비3"},
            "f44"      : {"size":  0, "align":  "", "desc": "매도호가4"},
            "f64"      : {"size":  0, "align":  "", "desc": "매도호가수량4"},
            "f84"      : {"size":  0, "align":  "", "desc": "매도호가직전대비4"},
            "f54"      : {"size":  0, "align":  "", "desc": "매수호가4"},
            "f74"      : {"size":  0, "align":  "", "desc": "매수호가수량4"},
            "f94"      : {"size":  0, "align":  "", "desc": "매수호가직전대비4"},
            "f45"      : {"size":  0, "align":  "", "desc": "매도호가5"},
            "f65"      : {"size":  0, "align":  "", "desc": "매도호가수량5"},
            "f85"      : {"size":  0, "align":  "", "desc": "매도호가직전대비5"},
            "f55"      : {"size":  0, "align":  "", "desc": "매수호가5"},
            "f75"      : {"size":  0, "align":  "", "desc": "매수호가수량5"},
            "f95"      : {"size":  0, "align":  "", "desc": "매수호가직전대비5"},
            "f46"      : {"size":  0, "align":  "", "desc": "매도호가6"},
            "f66"      : {"size":  0, "align":  "", "desc": "매도호가수량6"},
            "f86"      : {"size":  0, "align":  "", "desc": "매도호가직전대비6"},
            "f56"      : {"size":  0, "align":  "", "desc": "매수호가6"},
            "f76"      : {"size":  0, "align":  "", "desc": "매수호가수량6"},
            "f96"      : {"size":  0, "align":  "", "desc": "매수호가직전대비6"},
            "f47"      : {"size":  0, "align":  "", "desc": "매도호가7"},
            "f67"      : {"size":  0, "align":  "", "desc": "매도호가수량7"},
            "f87"      : {"size":  0, "align":  "", "desc": "매도호가직전대비7"},
            "f57"      : {"size":  0, "align":  "", "desc": "매수호가7"},
            "f77"      : {"size":  0, "align":  "", "desc": "매수호가수량7"},
            "f97"      : {"size":  0, "align":  "", "desc": "매수호가직전대비7"},
            "f48"      : {"size":  0, "align":  "", "desc": "매도호가8"},
            "f68"      : {"size":  0, "align":  "", "desc": "매도호가수량8"},
            "f88"      : {"size":  0, "align":  "", "desc": "매도호가직전대비8"},
            "f58"      : {"size":  0, "align":  "", "desc": "매수호가8"},
            "f78"      : {"size":  0, "align":  "", "desc": "매수호가수량8"},
            "f98"      : {"size":  0, "align":  "", "desc": "매수호가직전대비8"},
            "f49"      : {"size":  0, "align":  "", "desc": "매도호가9"},
            "f69"      : {"size":  0, "align":  "", "desc": "매도호가수량9"},
            "f89"      : {"size":  0, "align":  "", "desc": "매도호가직전대비9"},
            "f59"      : {"size":  0, "align":  "", "desc": "매수호가9"},
            "f79"      : {"size":  0, "align":  "", "desc": "매수호가수량9"},
            "f99"      : {"size":  0, "align":  "", "desc": "매수호가직전대비9"},
            "f50"      : {"size":  0, "align":  "", "desc": "매도호가10"},
            "f70"      : {"size":  0, "align":  "", "desc": "매도호가수량10"},
            "f90"      : {"size":  0, "align":  "", "desc": "매도호가직전대비10"},
            "f60"      : {"size":  0, "align":  "", "desc": "매수호가10"},
            "f80"      : {"size":  0, "align":  "", "desc": "매수호가수량10"},
            "f100"     : {"size":  0, "align":  "", "desc": "매수호가직전대비10"},
            "f121"     : {"size":  0, "align":  "", "desc": "매도호가총잔량"},
            "f122"     : {"size":  0, "align":  "", "desc": "매도호가총잔량직전대비"},
            "f125"     : {"size":  0, "align":  "", "desc": "매수호가총잔량"},
            "f126"     : {"size":  0, "align":  "", "desc": "매수호가총잔량직전대비"},
            "f23"      : {"size":  0, "align":  "", "desc": "예상체결가"},
            "f24"      : {"size":  0, "align":  "", "desc": "예상체결수량"},
            "f128"     : {"size":  0, "align":  "", "desc": "순매수잔량"},
            "f129"     : {"size":  0, "align":  "", "desc": "매수비율"},
            "f138"     : {"size":  0, "align":  "", "desc": "순매도잔량"},
            "f139"     : {"size":  0, "align":  "", "desc": "매도비율"},
            "f200"     : {"size":  0, "align":  "", "desc": "예상체결가전일종가대비"},
            "f201"     : {"size":  0, "align":  "", "desc": "예상체결가전일종가대비등락율"},
            "f238"     : {"size":  0, "align":  "", "desc": "예상체결가전일종가대비기호"},
            "f291"     : {"size":  0, "align":  "", "desc": "예상체결가(예상체결 시간동안에만 유효한 값)"},
            "f292"     : {"size":  0, "align":  "", "desc": "예상체결량"},
            "f293"     : {"size":  0, "align":  "", "desc": "예상체결가전일대비기호"},
            "f294"     : {"size":  0, "align":  "", "desc": "예상체결가전일대비"},
            "f295"     : {"size":  0, "align":  "", "desc": "예상체결가전일대비등락율"},
            "f621"     : {"size":  0, "align":  "", "desc": "LP매도호가수량1"},
            "f631"     : {"size":  0, "align":  "", "desc": "LP매수호가수량1"},
            "f622"     : {"size":  0, "align":  "", "desc": "LP매도호가수량2"},
            "f632"     : {"size":  0, "align":  "", "desc": "LP매수호가수량2"},
            "f623"     : {"size":  0, "align":  "", "desc": "LP매도호가수량3"},
            "f633"     : {"size":  0, "align":  "", "desc": "LP매수호가수량3"},
            "f624"     : {"size":  0, "align":  "", "desc": "LP매도호가수량4"},
            "f634"     : {"size":  0, "align":  "", "desc": "LP매수호가수량4"},
            "f625"     : {"size":  0, "align":  "", "desc": "LP매도호가수량5"},
            "f635"     : {"size":  0, "align":  "", "desc": "LP매수호가수량5"},
            "f626"     : {"size":  0, "align":  "", "desc": "LP매도호가수량6"},
            "f636"     : {"size":  0, "align":  "", "desc": "LP매수호가수량6"},
            "f627"     : {"size":  0, "align":  "", "desc": "LP매도호가수량7"},
            "f637"     : {"size":  0, "align":  "", "desc": "LP매수호가수량7"},
            "f628"     : {"size":  0, "align":  "", "desc": "LP매도호가수량8"},
            "f638"     : {"size":  0, "align":  "", "desc": "LP매수호가수량8"},
            "f629"     : {"size":  0, "align":  "", "desc": "LP매도호가수량9"},
            "f639"     : {"size":  0, "align":  "", "desc": "LP매수호가수량9"},
            "f630"     : {"size":  0, "align":  "", "desc": "LP매도호가수량10"},
            "f640"     : {"size":  0, "align":  "", "desc": "LP매수호가수량10"},
            "f299"     : {"size":  0, "align":  "", "desc": "전일거래량대비예상체결률"},
            "f215"     : {"size":  0, "align":  "", "desc": "장운영구분"},
            "f216"     : {"size":  0, "align":  "", "desc": "투자자별ticker"},
            "f131"     : {"size":  0, "align":  "", "desc": "시간외매도호가총잔량"},
            "f132"     : {"size":  0, "align":  "", "desc": "시간외매도호가총잔량직전대비"},
            "f135"     : {"size":  0, "align":  "", "desc": "시간외매수호가총잔량"},
            "f136"     : {"size":  0, "align":  "", "desc": "시간외매수호가총잔량직전대비"},
            "f141"     : {"size": 12, "align": "<", "desc": "매도거래원1"},
            "f161"     : {"size":  7, "align": ">", "desc": "매도거래원수량1"},
            "f166"     : {"size":  7, "align": ">", "desc": "매도거래원별증감1"},
            "f146"     : {"size":  3, "align":  "", "desc": "매도거래원코드1"},
            "f271"     : {"size":  4, "align":  "", "desc": "매도거래원색깔1"},
            "f151"     : {"size": 12, "align": "<", "desc": "매수거래원1"},
            "f171"     : {"size":  7, "align": ">", "desc": "매수거래원수량1"},
            "f176"     : {"size":  7, "align": ">", "desc": "매수거래원별증감1"},
            "f156"     : {"size":  3, "align":  "", "desc": "매수거래원코드1"},
            "f281"     : {"size":  4, "align":  "", "desc": "매수거래원색깔1"},
            "f142"     : {"size": 12, "align": "<", "desc": "매도거래원2"},
            "f162"     : {"size":  7, "align": ">", "desc": "매도거래원수량2"},
            "f167"     : {"size":  7, "align": ">", "desc": "매도거래원별증감2"},
            "f147"     : {"size":  3, "align":  "", "desc": "매도거래원코드2"},
            "f272"     : {"size":  4, "align":  "", "desc": "매도거래원색깔2"},
            "f152"     : {"size": 12, "align": "<", "desc": "매수거래원2"},
            "f172"     : {"size":  7, "align": ">", "desc": "매수거래원수량2"},
            "f177"     : {"size":  7, "align": ">", "desc": "매수거래원별증감2"},
            "f157"     : {"size":  3, "align":  "", "desc": "매수거래원코드2"},
            "f282"     : {"size":  4, "align":  "", "desc": "매수거래원색깔2"},
            "f143"     : {"size": 12, "align": "<", "desc": "매도거래원3"},
            "f163"     : {"size":  7, "align": ">", "desc": "매도거래원수량3"},
            "f168"     : {"size":  7, "align": ">", "desc": "매도거래원별증감3"},
            "f148"     : {"size":  3, "align":  "", "desc": "매도거래원코드3"},
            "f273"     : {"size":  4, "align":  "", "desc": "매도거래원색깔3"},
            "f153"     : {"size": 12, "align": "<", "desc": "매수거래원3"},
            "f173"     : {"size":  7, "align": ">", "desc": "매수거래원수량3"},
            "f178"     : {"size":  7, "align": ">", "desc": "매수거래원별증감3"},
            "f158"     : {"size":  3, "align":  "", "desc": "매수거래원코드3"},
            "f283"     : {"size":  4, "align":  "", "desc": "매수거래원색깔3"},
            "f144"     : {"size": 12, "align": "<", "desc": "매도거래원4"},
            "f164"     : {"size":  7, "align": ">", "desc": "매도거래원수량4"},
            "f169"     : {"size":  7, "align": ">", "desc": "매도거래원별증감4"},
            "f149"     : {"size":  3, "align":  "", "desc": "매도거래원코드4"},
            "f274"     : {"size":  4, "align":  "", "desc": "매도거래원색깔4"},
            "f154"     : {"size": 12, "align": "<", "desc": "매수거래원4"},
            "f174"     : {"size":  7, "align": ">", "desc": "매수거래원수량4"},
            "f179"     : {"size":  7, "align": ">", "desc": "매수거래원별증감4"},
            "f159"     : {"size":  3, "align":  "", "desc": "매수거래원코드4"},
            "f284"     : {"size":  4, "align":  "", "desc": "매수거래원색깔4"},
            "f145"     : {"size": 12, "align": "<", "desc": "매도거래원5"},
            "f165"     : {"size":  7, "align": ">", "desc": "매도거래원수량5"},
            "f170"     : {"size":  7, "align": ">", "desc": "매도거래원별증감5"},
            "f150"     : {"size":  3, "align":  "", "desc": "매도거래원코드5"},
            "f275"     : {"size":  4, "align":  "", "desc": "매도거래원색깔5"},
            "f155"     : {"size": 12, "align": "<", "desc": "매수거래원5"},
            "f175"     : {"size":  7, "align": ">", "desc": "매수거래원수량5"},
            "f180"     : {"size":  7, "align": ">", "desc": "매수거래원별증감5"},
            "f160"     : {"size":  3, "align":  "", "desc": "매수거래원코드5"},
            "f285"     : {"size":  4, "align":  "", "desc": "매수거래원색깔5"},
            "f261"     : {"size":  6, "align": ">", "desc": "외국계매도추정합"},
            "f262"     : {"size":  6, "align": ">", "desc": "외국계매도추정합변동"},
            "f263"     : {"size":  6, "align": ">", "desc": "외국계매수추정합"},
            "f264"     : {"size":  6, "align": ">", "desc": "외국계매수추정합변동"},
            "f267"     : {"size":  6, "align": ">", "desc": "외국계순매수추정합"},
            "f268"     : {"size":  6, "align": ">", "desc": "외국계순매수변동"},
            "f337"     : {"size":  1, "align":  "", "desc": "거래소구분"},
            "f36"      : {"size":  0, "align":  "", "desc": "NAV"},
            "f37"      : {"size":  0, "align":  "", "desc": "NAV전일대비"},
            "f38"      : {"size":  0, "align":  "", "desc": "NAV등락율"},
            "f39"      : {"size":  0, "align":  "", "desc": "추적오차율"},
            "f667"     : {"size":  0, "align":  "", "desc": "ELW기어링비율"},
            "f668"     : {"size":  0, "align":  "", "desc": "ELW손익분기율"},
            "f669"     : {"size":  0, "align":  "", "desc": "ELW자본지지점"},
            "f265"     : {"size":  0, "align":  "", "desc": "NAV/지수괴리율"},
            "f266"     : {"size":  0, "align":  "", "desc": "NAV/ETF괴리율"},
            "f666"     : {"size":  0, "align":  "", "desc": "ELW패리티"},
            "f1211"    : {"size":  0, "align":  "", "desc": "ELW프리미엄"},
            "f670"     : {"size":  0, "align":  "", "desc": "ELW이론가"},
            "f671"     : {"size":  0, "align":  "", "desc": "ELW내재변동성"},
            "f672"     : {"size":  0, "align":  "", "desc": "ELW델타"},
            "f673"     : {"size":  0, "align":  "", "desc": "ELW감마"},
            "f674"     : {"size":  0, "align":  "", "desc": "ELW쎄타"},
            "f675"     : {"size":  0, "align":  "", "desc": "ELW베가"},
            "f676"     : {"size":  0, "align":  "", "desc": "ELW로"},
            "f706"     : {"size":  0, "align":  "", "desc": "LP호가내재변동성"},
            "f297"     : {"size":  6, "align": "<", "desc": "임의연장"},
            "f592"     : {"size":  6, "align":  "", "desc": "장전임의연장"},
            "f593"     : {"size":  6, "align":  "", "desc": "장후임의연장"},
            "f305"     : {"size":  7, "align": ">", "desc": "상한가"},
            "f306"     : {"size":  7, "align": ">", "desc": "하한가"},
            "f307"     : {"size":  7, "align": ">", "desc": "기준가"},
            "f689"     : {"size":  0, "align":  "", "desc": "조기종료ELW발생"},
            "f594"     : {"size":  0, "align":  "", "desc": "통화단위"},
            "f382"     : {"size":  4, "align": ">", "desc": "증거금율표시"},
            "f370"     : {"size": 20, "align": "<", "desc": "종목정보"},
            "f300"     : {"size":  2, "align": ">", "desc": "Extra Item"},
            "f195"     : {"size":  0, "align":  "", "desc": "미결제약정"},
            "f182"     : {"size":  0, "align":  "", "desc": "이론가"},
            "f184"     : {"size":  0, "align":  "", "desc": "이론베이시스"},
            "f183"     : {"size":  0, "align":  "", "desc": "시장베이시스"},
            "f186"     : {"size":  0, "align":  "", "desc": "괴리율"},
            "f181"     : {"size":  0, "align":  "", "desc": "미결제약정전일대비"},
            "f185"     : {"size":  0, "align":  "", "desc": "괴리도"},
            "f197"     : {"size":  0, "align":  "", "desc": "KOSPI200"},
            "f246"     : {"size":  0, "align":  "", "desc": "시초미결제약정수량"},
            "f247"     : {"size":  0, "align":  "", "desc": "최고미결제약정수량"},
            "f248"     : {"size":  0, "align":  "", "desc": "최저미결제약정수량"},
            "f196"     : {"size":  0, "align":  "", "desc": "미결제증감"},
            "f1365"    : {"size":  0, "align":  "", "desc": "실시간상한가"},
            "f1366"    : {"size":  0, "align":  "", "desc": "실시간하한가"},
            "f1367"    : {"size":  0, "align":  "", "desc": "협의대량누적체결수량"},
            "f101"     : {"size":  0, "align":  "", "desc": "매도호가건수1"},
            "f111"     : {"size":  0, "align":  "", "desc": "매수호가건수1"},
            "f102"     : {"size":  0, "align":  "", "desc": "매도호가건수2"},
            "f112"     : {"size":  0, "align":  "", "desc": "매수호가건수2"},
            "f103"     : {"size":  0, "align":  "", "desc": "매도호가건수3"},
            "f113"     : {"size":  0, "align":  "", "desc": "매수호가건수3"},
            "f104"     : {"size":  0, "align":  "", "desc": "매도호가건수4"},
            "f114"     : {"size":  0, "align":  "", "desc": "매수호가건수4"},
            "f105"     : {"size":  0, "align":  "", "desc": "매도호가건수5"},
            "f115"     : {"size":  0, "align":  "", "desc": "매수호가건수5"},
            "f123"     : {"size":  0, "align":  "", "desc": "매도호가총건수"},
            "f127"     : {"size":  0, "align":  "", "desc": "매수호가총건수"},
            "f137"     : {"size":  0, "align":  "", "desc": "호가순잔량"},
            "f190"     : {"size":  0, "align":  "", "desc": "델타"},
            "f191"     : {"size":  0, "align":  "", "desc": "감마"},
            "f193"     : {"size":  0, "align":  "", "desc": "세타"},
            "f192"     : {"size":  0, "align":  "", "desc": "베가"},
            "f194"     : {"size":  0, "align":  "", "desc": "로"},
            "f187"     : {"size":  0, "align":  "", "desc": "내재가치"},
            "f219"     : {"size":  0, "align":  "", "desc": "선물최근월물지수"},
            "f188"     : {"size":  0, "align":  "", "desc": "시간가치"},
            "f189"     : {"size":  0, "align":  "", "desc": "내재변동성(I.V.)"},
            "f391"     : {"size":  0, "align":  "", "desc": "기준가대비시가등락율"},
            "f392"     : {"size":  0, "align":  "", "desc": "기준가대비고가등락율"},
            "f393"     : {"size":  0, "align":  "", "desc": "기준가대비저가등락율"},
            "f252"     : {"size":  0, "align":  "", "desc": "상승종목수"},
            "f251"     : {"size":  0, "align":  "", "desc": "상한종목수"},
            "f253"     : {"size":  0, "align":  "", "desc": "보합종목수"},
            "f255"     : {"size":  0, "align":  "", "desc": "하락종목수"},
            "f254"     : {"size":  0, "align":  "", "desc": "하한종목수"},
            "f256"     : {"size":  0, "align":  "", "desc": "거래형성종목수"},
            "f257"     : {"size":  0, "align":  "", "desc": "거래형성비율"},
            "f214"     : {"size":  0, "align":  "", "desc": "장시작예상잔여시간"},
            "f9001"    : {"size":  6, "align":  "", "desc": "종목코드,업종코드"},
            "f302"     : {"size": 20, "align": "<", "desc": "종목명"},
            "f9068"    : {"size":  0, "align":  "", "desc": "VI발동구분"},
            "f9008"    : {"size":  0, "align":  "", "desc": "KOSPI,KOSDAQ,전체구분"},
            "f9075"    : {"size":  0, "align":  "", "desc": "장전구분"},
            "f1221"    : {"size":  0, "align":  "", "desc": "VI 발동가격"},
            "f1223"    : {"size":  0, "align":  "", "desc": "매매체결처리시각"},
            "f1224"    : {"size":  0, "align":  "", "desc": "VI 해제시각"},
            "f1225"    : {"size":  0, "align":  "", "desc": "VI 적용구분(정적/동적/동적+정적)"},
            "f1236"    : {"size":  0, "align":  "", "desc": "기준가격 정적"},
            "f1237"    : {"size":  0, "align":  "", "desc": "기준가격 동적"},
            "f1238"    : {"size":  0, "align":  "", "desc": "괴리율 정적"},
            "f1239"    : {"size":  0, "align":  "", "desc": "괴리율 동적"},
            "f1489"    : {"size":  0, "align":  "", "desc": "VI발동가 등락률"},
            "f1490"    : {"size":  0, "align":  "", "desc": "VI발동횟수"},
            "f9069"    : {"size":  0, "align":  "", "desc": "발동방향구분"},
            "f1279"    : {"size":  0, "align":  "", "desc": "Extra Item"},
            "f9201"    : {"size":  0, "align":  "", "desc": "계좌번호"},
            "f9203"    : {"size":  7, "align": ">", "desc": "주문번호"},
            "f9205"    : {"size":  0, "align":  "", "desc": "관리자사번"},
            "f912"     : {"size":  0, "align":  "", "desc": "주문업무분류"},
            "f913"     : {"size":  4, "align": ">", "desc": "주문상태"},
            "f900"     : {"size":  5, "align": ">", "desc": "주문수량"},
            "f901"     : {"size":  7, "align": ">", "desc": "주문가격"},
            "f902"     : {"size":  5, "align": ">", "desc": "미체결수량"},
            "f903"     : {"size":  7, "align": ">", "desc": "체결누계금액"},
            "f904"     : {"size":  0, "align":  "", "desc": "원주문번호"},
            "f905"     : {"size":  8, "align": ">", "desc": "주문구분"},
            "f906"     : {"size":  0, "align":  "", "desc": "매매구분"},
            "f907"     : {"size":  0, "align":  "", "desc": "매도수구분"},
            "f908"     : {"size":  6, "align":  "", "desc": "주문/체결시간"},
            "f909"     : {"size":  7, "align": ">", "desc": "체결번호"},
            "f910"     : {"size":  7, "align": ">", "desc": "체결가"},
            "f911"     : {"size":  5, "align": ">", "desc": "체결량"},
            "f914"     : {"size":  7, "align": ">", "desc": "단위체결가"},
            "f915"     : {"size":  5, "align": ">", "desc": "단위체결량"},
            "f938"     : {"size":  6, "align": ">", "desc": "당일매매수수료"},
            "f939"     : {"size":  6, "align": ">", "desc": "당일매매세금"},
            "f919"     : {"size":  1, "align": ">", "desc": "거부사유"},
            "f920"     : {"size": 19, "align": "<", "desc": "화면번호"},
            "f921"     : {"size":  0, "align":  "", "desc": "터미널번호"},
            "f922"     : {"size":  0, "align":  "", "desc": "신용구분(실시간 체결용)"},
            "f923"     : {"size":  0, "align":  "", "desc": "대출일(실시간 체결용)"},
            "f930"     : {"size":  5, "align": ">", "desc": "보유수량"},
            "f931"     : {"size":  7, "align": ">", "desc": "매입단가"},
            "f932"     : {"size":  9, "align": ">", "desc": "총매입가(당일누적)"},
            "f933"     : {"size":  5, "align": ">", "desc": "주문가능수량"},
            "f945"     : {"size":  5, "align": ">", "desc": "당일순매수량"},
            "f946"     : {"size":  1, "align":  "", "desc": "매도/매수구분"},
            "f950"     : {"size":  7, "align": ">", "desc": "당일총매도손익"},
            "f951"     : {"size":  0, "align":  "", "desc": "Extra Item"},
            "f8019"    : {"size":  6, "align": ">", "desc": "손익율(실현손익)"},
            "f397"     : {"size":  0, "align":  "", "desc": "파생상품거래단위"},
            "f917"     : {"size":  0, "align":  "", "desc": "신용구분"},
            "f916"     : {"size":  0, "align":  "", "desc": "대출일"},
            "f957"     : {"size":  0, "align":  "", "desc": "신용금액"},
            "f958"     : {"size":  0, "align":  "", "desc": "신용이자"},
            "f918"     : {"size":  0, "align":  "", "desc": "만기일"},
            "f990"     : {"size":  7, "align": ">", "desc": "당일실현손익(유가)"},
            "f991"     : {"size":  6, "align": ">", "desc": "당일실현손익률(유가)"},
            "f992"     : {"size":  7, "align": ">", "desc": "당일실현손익(신용)"},
            "f993"     : {"size":  6, "align": ">", "desc": "당일실현손익률(신용)"},
            "f959"     : {"size":  0, "align":  "", "desc": "담보대출수량"},
            "f924"     : {"size":  0, "align":  "", "desc": "Extra Item"},
            "f202"     : {"size":  6, "align": ">", "desc": "매도수량"},
            "f204"     : {"size":  5, "align": ">", "desc": "매도금액"},
            "f206"     : {"size":  6, "align": ">", "desc": "매수수량"},
            "f208"     : {"size":  5, "align": ">", "desc": "매수금액"},
            "f210"     : {"size":  7, "align": ">", "desc": "순매수수량"},
            "f211"     : {"size":  4, "align": ">", "desc": "순매수수량증감"},
            "f212"     : {"size":  5, "align": ">", "desc": "순매수금액"},
            "f213"     : {"size":  1, "align":  "", "desc": "순매수금액증감"},
            "f10010"   : {"size":  6, "align": ">", "desc": "알수없는항목"},
        };
    
    def getFidLogText(self, fId, value):
        logText = ", 알수없는항목({0}:{1})".format(fId, value);
        if fId in self.fidList:
            logText = ", {0}({1})".format(self.fidList[fId]["desc"], self.preFormat(value, self.fidList[fId]["size"], self.fidList[fId]["align"]));
        return logText;

        
    def preFormat(self, string, width=None, align="<", fill=" "):
        string = str(string)
        width = width if width != None else len(string);
        #count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF") for c in string));
        count = [];
        for char in string:
            count.append(2 if ord('가') <= ord(char) <= ord('힣') else 1);
        count = width - sum(count);

        return {
            ">": lambda s: fill * count + s, # lambda 매개변수 : 표현식
            "<": lambda s: s + fill * count,
            "^": lambda s: fill * (count / 2) + s + fill * (count / 2 + count % 2),
             "": lambda s: s,
        }[align](string)

    def logCondition(self, obj):
        logFile = ("logging/{0}/{1}/{2}.log").format(self.today_YYYYMMDD, "condition", "onReceiveRealCondition");
        writeText = ["[{0}:{1}]".format(datetime.datetime.now(), "onReceiveRealCondition")];
        for key in obj:
            writeText.append(self.getFidLogText(key, obj[key]));
        writeText.append("\n");
        with open(logFile, "a", encoding="UTF-8", ) as fileData:
            fileData.writelines("".join(writeText));
    
    def logKiwoom(self, obj):
        logFile = ("logging/{0}/{1}/{2}.log").format(self.today_YYYYMMDD, "kiwoom", "onReceiveMsg");
        writeText = ["[{0}:{1}]".format(datetime.datetime.now(), "onReceiveMsg")];
        for key in obj:
            writeText.append(self.getFidLogText(key, obj[key]));
        writeText.append("\n");
        with open(logFile, "a", encoding="UTF-8", ) as fileData:
            fileData.writelines("".join(writeText));
    
    def logOrder(self, obj):
        fileDiv = "sendOrder({0})".format(self.nOrderType[obj["f905"]]);
        logFile = ("logging/{0}/{1}/{2}.log").format(self.today_YYYYMMDD, "order", fileDiv);
        writeText = ["[{0}:{1}]".format(datetime.datetime.now(), fileDiv)];
        for key in obj:
            writeText.append(self.getFidLogText(key, obj[key]));
        writeText.append("\n");
        with open(logFile, "a", encoding="UTF-8", ) as fileData:
            fileData.writelines("".join(writeText));
    
    def logReal(self, obj):
        fileDiv = "onReceiveRealData({0})".format(obj["sRealType"]);
        logFile = ("logging/{0}/{1}/{2}.log").format(self.today_YYYYMMDD, "real", fileDiv);
        writeText = ["[{0}:{1}]".format(datetime.datetime.now(), fileDiv)];
        for key in obj:
            writeText.append(self.getFidLogText(key, obj[key]));
        writeText.append("\n");
        with open(logFile, "a", encoding="UTF-8", ) as fileData:
            fileData.writelines("".join(writeText));
    
    def logChejan(self, obj):
        obj["f9001"] = obj["f9001"][-6:];#종목코드
        obj["f302" ] = self.api.dynamicCall("GetMasterCodeName(QString)", obj["f9001"]) if obj["f302"] == "" else obj["f302"].strip();#종목명
        obj["f10"  ] = obj["f10" ].replace("+","").replace("-",""); #현재가

        if obj["gubun"] == "1":   
            obj["f27" ] = obj["f27" ].replace("+","").replace("-",""); #최우선 매도호가
            obj["f28" ] = obj["f28" ].replace("+","").replace("-",""); #최우선 매수호가
            obj["f306"] = obj["f306"].replace("+","").replace("-",""); #하한가
            obj["f305"] = obj["f305"].replace("+","").replace("-",""); #상한가

        if "gubun" in obj and obj["gubun"] == "0":
            if "f905" in obj and obj["f905"] == "+매수":#매수쳬결
                fileDiv = "onReceiveChejanData(cheBuy)";
            elif "f905" in obj and obj["f905"] == "-매도":#매도체결
                fileDiv = "onReceiveChejanData(cheSell)";
            else:
                fileDiv = "onReceiveChejanData(etc)";
        elif "gubun" in obj and obj["gubun"] == "1":
            if "f946" in obj and obj["f946"] == "2":#매수 잔고변경
                fileDiv = "onReceiveChejanData(janBuy)";
            elif "f946" in obj and obj["f946"] == "1":#매도 잔고변경
                fileDiv = "onReceiveChejanData(janSell)";
            else:
                fileDiv = "onReceiveChejanData(etc)";

        logFile = ("logging/{0}/{1}/{2}.log").format(self.today_YYYYMMDD, "chejan", fileDiv);
        writeText = ["[{0}:{1}]".format(datetime.datetime.now(), fileDiv)];
        for key in obj:
            writeText.append(self.getFidLogText(key, obj[key]));
        writeText.append("\n");
        with open(logFile, "a", encoding="UTF-8", ) as fileData:
            fileData.writelines("".join(writeText));
