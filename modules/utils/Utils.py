import sys, os;

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # 패키징 상태로 실행될 때
        base_path = os.getcwd();
        return os.path.join(base_path, relative_path);
    else:
        # 스크립트로 실행될 때
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)));
        return os.path.join(base_path, relative_path);