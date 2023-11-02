from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 미체결요청 Class ######################
#########################################
class Opt10075(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #multiRow
            "mField01": "계좌번호",
            "mField02": "주문번호",
            "mField03": "관리사번",
            "mField04": "종목코드",
            "mField05": "업무구분",
            "mField06": "주문상태",#체결, 미체결, 확인
            "mField07": "종목명",
            "mField08": "주문수량",
            "mField09": "주문가격",
            "mField10": "미체결수량",
            "mField11": "체결누계금액",
            "mField12": "원주문번호",
            "mField13": "주문구분",#+매수, -매도
            "mField14": "매매구분",#보통
            "mField15": "시간",#시간만.. 일자는??(당일것만 나오는것 같음)
            "mField16": "체결번호",
            "mField17": "체결가",
            "mField18": "체결량",
            "mField19": "현재가",
            "mField20": "매도호가",
            "mField21": "매수호가",
            "mField22": "단위체결가",
            "mField23": "단위체결량",
            "mField24": "당일매매수수료",
            "mField25": "당일매매세금",
            "mField26": "개인투자자"
        };