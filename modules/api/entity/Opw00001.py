from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 예수금상세현황요청 Class ##############
#########################################
class Opw00001(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #singleRow
            "sField01": "예수금",
            "sField02": "주식증거금현금",
            "sField03": "수익증권증거금현금",      
            "sField04": "익일수익증권매도정산대금",
            "sField05": "해외주식원화대용설정금",
            "sField06": "신용보증금현금",
            "sField07": "신용담보금현금",
            "sField08": "추가담보금현금",
            "sField09": "기타증거금",
            "sField10": "미수확보금",
            "sField11": "공매도대금",
            "sField12": "신용설정평가금",
            "sField13": "수표입금액",
            "sField14": "기타수표입금액",
            "sField15": "신용담보재사용",
            "sField16": "코넥스기본예탁금",
            "sField17": "ELW예탁평가금",
            "sField18": "신용대주권리예정금액",
            "sField19": "생계형가입금액",
            "sField20": "생계형입금가능금액",
            "sField21": "대용금평가금액(합계)",
            "sField22": "잔고대용평가금액",
            "sField23": "위탁대용잔고평가금액",
            "sField24": "수익증권대용평가금액",
            "sField25": "위탁증거금대용",
            "sField26": "신용보증금대용",
            "sField27": "신용담보금대용",
            "sField28": "추가담보금대용",
            "sField29": "권리대용금",
            "sField30": "출금가능금액",
            "sField31": "랩출금가능금액",
            "sField32": "주문가능금액",
            "sField33": "수익증권매수가능금액",
            "sField34": "20%종목주문가능금액",
            "sField35": "30%종목주문가능금액",
            "sField36": "40%종목주문가능금액",
            "sField37": "100%종목주문가능금액",
            "sField38": "현금미수금",
            "sField39": "현금미수연체료",
            "sField40": "현금미수금합계",
            "sField41": "신용이자미납",
            "sField42": "신용이자미납연체료",
            "sField43": "신용이자미납합계",
            "sField44": "기타대여금",
            "sField45": "기타대여금연체료",
            "sField46": "기타대여금합계",
            "sField47": "미상환융자금",
            "sField48": "융자금합계",
            "sField49": "대주금합계",
            "sField50": "신용담보비율",
            "sField51": "중도이용료",
            "sField52": "최소주문가능금액",
            "sField53": "대출총평가금액",
            "sField54": "예탁담보대출잔고",
            "sField55": "매도담보대출잔고",
            "sField56": "d+1추정예수금",
            "sField57": "d+1매도매수정산금",
            "sField58": "d+1매수정산금",
            "sField59": "d+1미수변제소요금",
            "sField60": "d+1매도정산금",
            "sField61": "d+1출금가능금액",
            "sField62": "d+2추정예수금",
            "sField63": "d+2매도매수정산금",
            "sField64": "d+2매수정산금",
            "sField65": "d+2미수변제소요금",
            "sField66": "d+2매도정산금",
            "sField67": "d+2출금가능금액",
            "sField68": "출력건수",
            #multiRow
            "mField01": "통화코드",
            "mField02": "외화예수금",
            "mField03": "원화대용평가금",
            "mField04": "해외주식증거금",
            "mField05": "출금가능금액(예수금)",
            "mField06": "주문가능금액(예수금)",
            "mField07": "외화미수(합계)",
            "mField08": "외화현금미수금",
            "mField09": "연체료",
            "mField10": "d+1외화예수금",
            "mField11": "d+2외화예수금",
            "mField12": "d+3외화예수금",
            "mField13": "d+4외화예수금",
        };
