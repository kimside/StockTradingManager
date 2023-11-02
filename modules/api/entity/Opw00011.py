from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 증거금율별주문가능수량조회요청  Class #
#########################################
class Opw00011(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #singleRow
            "sField01": "종목증거금율",
            "sField02": "계좌증거금율",
            "sField03": "적용증거금율",
            "sField04": "증거금20주문가능금액",
            "sField05": "증거금20주문가능수량",
            "sField06": "증거금20전일재사용금액",
            "sField07": "증거금20금일재사용금액",
            "sField08": "증거금30주문가능금액",
            "sField09": "증거금30주문가능수량",
            "sField10": "증거금30전일재사용금액",
            "sField11": "증거금30금일재사용금액",
            "sField12": "증거금40주문가능금액",
            "sField13": "증거금40주문가능수량",
            "sField14": "증거금40전일재사용금액",
            "sField15": "증거금40금일재사용금액",
            "sField16": "증거금50주문가능금액",
            "sField17": "증거금50주문가능수량",
            "sField18": "증거금50전일재사용금액",
            "sField19": "증거금50금일재사용금액",
            "sField20": "증거금60주문가능금액",
            "sField21": "증거금60주문가능수량",
            "sField22": "증거금60전일재사용금액",
            "sField23": "증거금60금일재사용금액",
            "sField24": "증거금100주문가능금액",
            "sField25": "증거금100주문가능수량",
            "sField26": "증거금100전일재사용금액",
            "sField27": "증거금100금일재사용금액",
            "sField28": "미수불가주문가능금액",
            "sField29": "미수불가주문가능수량",
            "sField30": "미수불가전일재사용금액",
            "sField31": "미수불가금일재사용금액",
            "sField32": "예수금",
            "sField33": "대용금",
            "sField34": "미수금",
            "sField35": "주문가능대용",
            "sField36": "주문가능현금",
        };