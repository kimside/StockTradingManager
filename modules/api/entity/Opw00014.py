from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 비밀번호일치여부요청 Class ############
#########################################
class Opw00014(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        return {
            #singleRow
            "sField01": "일치여부",
        };