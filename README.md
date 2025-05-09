# StockTradingManager
Kiwoom OpenAPI를 이용하여 조건식을 활용한 간단한 자동매매 프로그램이며,<br/>
해당 프로젝트는 Python(3.11.5-32bit)를 이용하여 구성되어 있음.<br/>
환경설정 및 추가개발을 하지 않는다면, 무설치 버전을(dist/main.exe) 통하며 아래 필수사항만 충족된다면 사용가능<br/>
$\bf{\color{#FF2222}(분석/차트/통계에 대한 데이터는... HTS/MTS를 이용하시는걸 추천)}$

# 프로젝트 참조 Package
    - PyQt5(5.15.9)
    - PyQt5Singleton(0.1)
    - pyinstaller(5.13.2)
    - python-telegram-bot(20.6)
    - https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/ 다운로드 설치 (C++를 사용한 데스트톱 개발 모듈 설치) 
    - pandas(2.0.3) (pip install pandas==2.0.3)
    - numpy 2.0 이하 버전 (pip install "numpy<2.0")
    - exchange_calendars(버전은 모름)

# 필수사항
## Kiwoom 계좌
https://www.google.com/search?q=kiwoom+%EA%B3%84%EC%A2%8C%EA%B0%9C%EC%84%A4&sca_esv=578828967&rlz=1C1BNSD_koKR1074KR1074&ei=1bdDZZviGoj51e8PxPaESA&ved=0ahUKEwjboNLeyKWCAxWIfPUHHUQ7AQkQ4dUDCBA&uact=5&oq=kiwoom+%EA%B3%84%EC%A2%8C%EA%B0%9C%EC%84%A4&gs_lp=Egxnd3Mtd2l6LXNlcnAiE2tpd29vbSDqs4TsoozqsJzshKQyBRAhGKABSPojUO4IWJIjcAh4AJABBJgB_QGgAfAOqgEGMC4xMC4yuAEDyAEA-AEBwgIKEAAYRxjWBBiwA8ICBRAAGIAE4gMEGAAgQYgGAZAGCg&sclient=gws-wiz-serp

## Kiwoom OpenAPI 설치
https://www.google.com/search?q=Kiwoon+OpenAPI+%EC%84%A4%EC%B9%98&rlz=1C1BNSD_koKR1074KR1074&oq=Kiwoon+OpenAPI+%EC%84%A4%EC%B9%98&gs_lcrp=EgZjaHJvbWUyBggAEEUYOdIBCDc0ODVqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8

## Kiwoom 조건검색식
https://www.google.com/search?q=kiwoom+%EC%A1%B0%EA%B1%B4%EA%B2%80%EC%83%89%EC%8B%9D&sca_esv=578828967&rlz=1C1BNSD_koKR1074KR1074&ei=JLdDZeCmDo3e-QbQwITIDQ&ved=0ahUKEwjgyJKKyKWCAxUNb94KHVAgAdkQ4dUDCBA&uact=5&oq=kiwoom+%EC%A1%B0%EA%B1%B4%EA%B2%80%EC%83%89%EC%8B%9D&gs_lp=Egxnd3Mtd2l6LXNlcnAiFmtpd29vbSDsobDqsbTqsoDsg4nsi51IvipQAFjFJ3AEeACQAQKYAcgBoAHOF6oBBjAuMjIuMbgBA8gBAPgBAagCAMICERAuGIAEGLEDGIMBGMcBGNEDwgILEAAYgAQYsQMYgwHCAgsQLhiABBixAxiDAcICFBAuGIAEGLEDGIMBGMcBGNEDGNQCwgIEEC4YA8ICIBAuGIAEGLEDGIMBGMcBGNEDGJcFGNwEGN4EGOAE2AEBwgIFEAAYgATCAgQQABgDwgIaEC4YgAQYsQMYgwEYlwUY3AQY3gQY4ATYAQHCAg8QLhiKBRjHARjRAxgKGEPCAgcQLhiKBRhDwgIeEC4YigUYxwEY0QMYChhDGJcFGNwEGN4EGOAE2AEBwgIHEAAYigUYQ8ICDhAuGIMBGNQCGLEDGIAEwgIPEC4YxwEY0QMYigUYChhDwgIFEC4YgATCAh4QLhjHARjRAxiKBRgKGEMYlwUY3AQY3gQY4ATYAQHCAg4QLhjHARixAxjRAxiABMICHRAuGMcBGLEDGNEDGIAEGJcFGNwEGN4EGOAE2AEBwgILEC4YgAQYxwEY0QPCAhQQLhiABBiXBRjcBBjeBBjgBNgBAcICBRAhGKAB4gMEGAAgQYgGAboGBggBEAEYFA&sclient=gws-wiz-serp

# 참고사항
## openAPI 자동로그인
https://www.google.com/search?q=openapi+%EC%9E%90%EB%8F%99%EB%A1%9C%EA%B7%B8%EC%9D%B8&sca_esv=578842681&rlz=1C1BNSD_koKR1074KR1074&ei=frpDZeGdIYKxoASWn4bwBg&ved=0ahUKEwjh1LWjy6WCAxWCGIgKHZaPAW4Q4dUDCBA&uact=5&oq=openapi+%EC%9E%90%EB%8F%99%EB%A1%9C%EA%B7%B8%EC%9D%B8&gs_lp=Egxnd3Mtd2l6LXNlcnAiF29wZW5hcGkg7J6Q64-Z66Gc6re47J24MgkQIRigARgKGCoyBxAhGKABGApI8zNQAFjGMnADeAGQAQSYAYQCoAHSF6oBBjEuMTguMrgBA8gBAPgBAagCAMICCxAAGIAEGLEDGIMBwgIREC4YgAQYsQMYgwEYxwEY0QPCAgQQABgDwgIREC4YgAQYsQMYgwEYxwEYrwHCAggQLhiABBixA8ICBRAuGIAEwgIFEAAYgATCAiAQLhiABBixAxiDARjHARjRAxiXBRjcBBjeBBjgBNgBAcICCBAAGIAEGLEDwgIHEAAYgAQYCsICCBAAGAgYHhgPwgIFEAAYogTCAgUQIRigAeIDBBgAIEGIBgG6BgYIARABGBQ&sclient=gws-wiz-serp
    
## Telegram 메세지 보내기
https://www.google.com/search?q=python+telegram+bot+%EB%A9%94%EC%8B%9C%EC%A7%80+%EB%B3%B4%EB%82%B4%EA%B8%B0&sca_esv=578842681&rlz=1C1BNSD_koKR1074KR1074&ei=ALtDZcPcL77Q1e8P_N2vCA&oq=python+telegram+bot+%EB%A9%94%EC%84%B8%EC%A7%80&gs_lp=Egxnd3Mtd2l6LXNlcnAiHXB5dGhvbiB0ZWxlZ3JhbSBib3Qg66mU7IS47KeAKgIIADIJECEYoAEYChgqMgcQIRigARgKMgcQIRigARgKSL0eUJEDWMYTcAR4AZABApgBugGgAdEJqgEDMC45uAEDyAEA-AEBwgIKEAAYRxjWBBiwA8ICBxAAGIoFGEPCAgUQABiABMICBBAAGB7CAgYQABgIGB7iAwQYACBBiAYBkAYK&sclient=gws-wiz-serp
