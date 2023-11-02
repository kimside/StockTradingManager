from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 계좌평가현황요청 Class ################
#########################################
class Opw00004(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #singleRow
            "sField01": "계좌명",
            "sField02": "지점명",
            "sField03": "예수금",
            "sField04": "D+2추정예수금",
            "sField05": "유가잔고평가액",
            "sField06": "예탁자산평가액",
            "sField07": "총매입금액",
            "sField08": "추정예탁자산",
            "sField09": "매도담보대출금",
            "sField10": "당일투자원금",
            "sField11": "당월투자원금",
            "sField12": "누적투자원금",
            "sField13": "당일투자손익",
            "sField14": "당월투자손익",
            "sField15": "누적투자손익",
            "sField16": "당일손익율",
            "sField17": "당월손익율",
            "sField18": "누적손익율",
            "sField19": "출력건수",
            #multiRow
            "mField01": "종목코드",
            "mField02": "종목명",
            "mField03": "보유수량",
            "mField04": "평균단가",
            "mField05": "현재가",
            "mField06": "평가금액",
            "mField07": "손익금액",
            "mField08": "손익율",
            "mField09": "대출일",
            "mField10": "매입금액",
            "mField11": "결제잔고",
            "mField12": "전일매수수량",
            "mField13": "전일매도수량",
            "mField14": "금일매수수량",
            "mField15": "금일매도수량",
        };
