class NotInsallOpenAPI(Exception):
    def __init__(self, message="Kiwoom OpenAPI가 설치되지 않았습니다."):
        self.message = message
        super().__init__(self.message)