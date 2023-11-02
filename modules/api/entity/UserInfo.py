from modules.api.entity.BaseEntity import BaseEntity;

#########################################
# 사용자정보 Class ######################
#########################################
class UserInfo(BaseEntity):
    def __init__(self, *args, **kwargs):
        if kwargs != None:
            for key, value in kwargs.items():
                self[key] = value;
    
    def getFieldDesc(self):
        for key, value in self.__dict__.items():
            print("{0}: {1}".format(key, value));
        pass;
