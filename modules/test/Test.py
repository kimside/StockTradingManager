import datetime, time;

if __name__ == "__main__":    
    a = 1000 / 1030 * 100;#수익중
    c = 1000 / 970  * 100;#손실중
    b = 100 - -3;
    print("수익중: {0}".format(a > b));
    print("손실중: {0}".format(c > b));