import datetime, time;

if __name__ == "__main__":    
    a = "TrailingStop(매수) 손실 추가매수";
    
    if "(" in a and ")" in a:
        stockCode = a[a.index("(")+1:a.index(")")];
        print(stockCode);

