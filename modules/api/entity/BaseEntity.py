import json, pprint, datetime, unicodedata;

from PyQt5 import QtWidgets, QtCore;
#########################################
# BaseEntity Class ######################
#########################################
class BaseEntity(object):
    def update(self, dict):
        for key, value in dict.items():
            if key.startswith("s") and type(value) == list:
                dict[key] = "".join(value);
            else:
                #dict[key] = list(filter(None, value));
                dict[key] = value;
        self.__dict__.update(dict)
    
    def __getitem__(self, key):
        return getattr(self, key);
    
    def __setitem__(self, key, value):
        return setattr(self, key, value);

    def __iter__(self):
        return vars(self).iteritems();
    
    def __repr__(self):
        return pprint.pformat(vars(self), indent = 4, width = 1);
        
    def toJsonString(self):
        return json.dumps(self.__dict__, ensure_ascii = False);

if __name__ == "__main__":
    s = "a;b;c;d;";
    sa = s.split(";");
    for idx, key in enumerate(sa):
        if key != "":
            print(idx, sa[idx]);