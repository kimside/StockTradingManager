from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 계좌수익률요청 Class ################
#########################################
class Opt10085(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #multiRow
            "mField01": "일자",
            "mField02": "종목코드",
            "mField03": "종목명",
            "mField04": "현재가",
            "mField05": "매입가",
            "mField06": "매입금액",
            "mField07": "보유수량",
            "mField08": "당일매도손익",
            "mField09": "당일매매수수료",
            "mField10": "당일매매세금",
            "mField11": "신용구분",
            "mField12": "대출일",
            "mField13": "결제잔고",
            "mField14": "청산가능수량",
            "mField15": "신용금액",
            "mField16": "신용이자",
            "mField17": "만기일"
        };