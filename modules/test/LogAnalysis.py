import pprint, os;

if __name__ == "__main__":
    """
    D:/workspace/StockTrading/logging/20231023/real/onReceiveRealData(주식체결).log ('15:15:21', 93)
    D:/workspace/StockTrading/logging/20231024/real/onReceiveRealData(주식체결).log ('10:40:20', 235)
    D:/workspace/StockTrading/logging/20231025/real/onReceiveRealData(주식체결).log ('09:01:37', 258)
    D:/workspace/StockTrading/logging/20231026/real/onReceiveRealData(주식체결).log ('09:58:17', 178)
    D:/workspace/StockTrading/logging/20231027/real/onReceiveRealData(주식체결).log ('10:16:19', 186)
    D:/workspace/StockTrading/logging/20231030/real/onReceiveRealData(주식체결).log ('10:12:54', 184)
    D:/workspace/StockTrading/logging/20231031/real/onReceiveRealData(주식체결).log ('14:03:35', 208)
    D:/workspace/StockTrading/logging/20231101/real/onReceiveRealData(주식체결).log ('09:06:01', 235)
    D:/workspace/StockTrading/logging/20231102/real/onReceiveRealData(주식체결).log ('09:00:27', 289)
    D:/workspace/StockTrading/logging/20231103/real/onReceiveRealData(주식체결).log ('09:46:17', 260)
    #target Process time : 0.003
    """
    """
    logFiles = [
        "D:/workspace/StockTrading/logging/20231023/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231024/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231025/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231026/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231027/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231028/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231029/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231030/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231031/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231101/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231102/real/onReceiveRealData(주식체결).log",
        "D:/workspace/StockTrading/logging/20231103/real/onReceiveRealData(주식체결).log",
    ];
    """
    logFiles = [
        "D:/workspace/StockTrading/logging/20231106/real/onReceiveRealData(주식체결).log",
        #"D:/workspace/StockTrading/modules/test/testLog.log",
    ];

    for logFile in logFiles:
        times = {};
        if os.path.isfile(logFile):
            with open(logFile, "r", encoding="UTF-8", ) as fileData:
                while True:
                    line = fileData.readline();
                    if not line:
                        break;
                    times[line[12:20]] = times.get(line[12:20], 0) + 1;

            sorted_dict = sorted(times.items(), key = lambda item: item[1], reverse = True);

            p = 0;
            for i in sorted_dict:
                if p == 6:
                    break;
                print(logFile, i)
                p +=1;