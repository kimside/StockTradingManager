from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 주식기본정보요청 Class ################
#########################################
class Opt10001(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #singleRow
            "sField01": "종목코드",
            "sField02": "종목명",
            "sField03": "결산월",
            "sField04": "액면가",
            "sField05": "자본금",
            "sField06": "상장주식",
            "sField07": "신용비율",
            "sField08": "연중최고",
            "sField09": "연중최저",
            "sField10": "시가총액",
            "sField11": "시가총액비중",
            "sField12": "외인소진률",
            "sField13": "대용가",
            "sField14": "PER",
            "sField15": "EPS",
            "sField16": "ROE",
            "sField17": "PBR",
            "sField18": "EV",
            "sField19": "BPS",
            "sField20": "매출액",
            "sField21": "영업이익",
            "sField22": "당기순이익",
            "sField23": "250최고",
            "sField24": "250최저",
            "sField25": "시가",
            "sField26": "고가",
            "sField27": "저가",
            "sField28": "상한가",
            "sField29": "하한가",
            "sField30": "기준가",
            "sField31": "예상체결가",
            "sField32": "예상체결수량",
            "sField33": "250최고가일",
            "sField34": "250최고가대비율",
            "sField35": "250최저가일",
            "sField36": "250최저가대비율",
            "sField37": "현재가",
            "sField38": "대비기호",
            "sField39": "전일대비",
            "sField40": "등락율",
            "sField41": "거래량",
            "sField42": "거래대비",
            "sField43": "액면가단위",
            "sField44": "유통주식",
            "sField45": "유통비율",
        };