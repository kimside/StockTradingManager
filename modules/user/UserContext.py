import os, datetime, shutil;

from PyQt5 import QtCore;

#########################################
# 사용자별 경로/상태 격리 모듈               #
#########################################
# 키움 OpenAPI는 프로세스당 1개의 로그인만 허용하므로                                        #
# 여러 사용자가 같은 PC에서 이 프로그램을 사용할 경우                                        #
# 각자의 설정/로그/상태가 섞이지 않도록 userId 기준으로 경로를 분리한다.                        #
#                                                                                    #
# 사용 흐름:                                                                           #
#   1) 프로그램 시작 시 init() 호출 → bootstrap 파일에서 lastUserId 로드                     #
#      (없으면 "_default" 사용)                                                         #
#   2) 키움 로그인 성공 후 setUserId(loginUserId) 호출                                    #
#      → 다른 사용자면 경로를 전환하고 bootstrap 갱신                                       #
#   3) Settings, LogMaker 등은 getSettingsPath()/getLogDir()을 통해 항상 현재 사용자 경로 사용  #
#########################################

_DEFAULT_USER_ID = "_default";
_BOOTSTRAP_FILE  = "settings/_bootstrap.ini";

_currentUserId = None;


def _todayYYYYMMDD():
    dt = datetime.datetime.now();
    return "{0}{1:02d}{2:02d}".format(dt.year, dt.month, dt.day);


def _loadBootstrap():
    if not os.path.exists(_BOOTSTRAP_FILE):
        return "";
    bs = QtCore.QSettings(_BOOTSTRAP_FILE, QtCore.QSettings.IniFormat);
    return bs.value("lastUserId", "") or "";


def _saveBootstrap(userId):
    os.makedirs(os.path.dirname(_BOOTSTRAP_FILE), exist_ok=True);
    bs = QtCore.QSettings(_BOOTSTRAP_FILE, QtCore.QSettings.IniFormat);
    bs.setValue("lastUserId", userId);
    bs.sync();


def _migrateLegacyData(userId):
    #구버전에서 사용하던 settings/config.ini가 존재하면 현재 사용자 디렉토리로 이동한다.
    legacyCfg = "settings/config.ini";
    newCfg    = "settings/{0}/config.ini".format(userId);
    if os.path.exists(legacyCfg) and not os.path.exists(newCfg):
        os.makedirs(os.path.dirname(newCfg), exist_ok=True);
        try:
            shutil.move(legacyCfg, newCfg);
        except Exception:
            pass;


def _ensureDirs():
    userId = _currentUserId or _DEFAULT_USER_ID;
    os.makedirs("settings/{0}".format(userId), exist_ok=True);
    os.makedirs("logging/{0}/{1}".format(userId, _todayYYYYMMDD()), exist_ok=True);
    os.makedirs("logging/{0}/{1}/order".format(userId, _todayYYYYMMDD()), exist_ok=True);


def init():
    #프로그램 시작 직후 1회 호출. bootstrap에서 마지막 사용자 정보 로드.
    global _currentUserId;
    lastUserId = _loadBootstrap();
    _currentUserId = lastUserId if lastUserId else _DEFAULT_USER_ID;
    _migrateLegacyData(_currentUserId);
    _ensureDirs();
    return _currentUserId;


def getUserId():
    global _currentUserId;
    if _currentUserId is None:
        init();
    return _currentUserId;


def setUserId(userId):
    #로그인 성공 후 호출. 사용자가 바뀌었으면 True 반환.
    global _currentUserId;
    if not userId:
        return False;
    if _currentUserId == userId:
        return False;
    _currentUserId = userId;
    _saveBootstrap(userId);
    _ensureDirs();
    return True;


def getSettingsPath():
    return "settings/{0}/config.ini".format(getUserId());


def getLogDir(yyyymmdd=None):
    if yyyymmdd is None:
        yyyymmdd = _todayYYYYMMDD();
    return "logging/{0}/{1}/".format(getUserId(), yyyymmdd);
