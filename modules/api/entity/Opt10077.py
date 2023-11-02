from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 당일실현손익상세요청 Class ############
#########################################
class Opt10077(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #multiRow
            "mField01": "종목명",
            "mField02": "체결량",
            "mField03": "매입단가",
            "mField04": "체결가",
            "mField05": "당일매도손익",
            "mField06": "손익율",
            "mField07": "당일매매수수료",
            "mField08": "당일매매세금",
            "mField09": "종목코드"
        };