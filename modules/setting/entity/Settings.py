import json, pprint, datetime;

from PyQt5 import uic, QtWidgets, QtCore, QtGui;

from modules.user import UserContext;

#########################################
# Setting정보 Class #####################
#########################################
class Settings(object):
    def __init__(self):
        self._initQSettings();

    def _initQSettings(self):
        self.settings = QtCore.QSettings(UserContext.getSettingsPath(), QtCore.QSettings.IniFormat);

    def reload(self):
        #사용자가 변경되었을 때 현재 UserContext 경로로 QSettings를 다시 초기화한다.
        self._initQSettings();

    def __repr__(self):
        return pprint.pformat(vars(self), indent = 4, width = 1);
        
    def toJsonString(self):
        return json.dumps(self.__dict__, ensure_ascii = False);

    def save(self, json):
        for key, value in json.items():
            self.settings.setValue(key, value);

        self.settings.sync();

    def setValue(self, key, value):
        self.settings.setValue(key, value);
    
    def value(self, key, value, type=str):
        return self.settings.setValue(key, value, type);
    
    def load(self):
        json = {};
        for key in self.settings.allKeys():
            v = self.settings.value(key);

            if v != None:
                if v == "false" or v == "true":
                    json[key] = bool(v);
                elif v.replace("-", "").isdigit():
                    json[key] = int(v);
                else:
                    json[key] = v;
            else:
                json[key] = [];

        return json;
    
    def sync(self):
        self.settings.setValue("orderList", self.orderList);
        self.settings.setValue("myStrategy", self.myStrategy);
        
if __name__ == "__main__":
    a = "0";
    print(a.index("."))