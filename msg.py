class msg:
    def __init__(self,type = '',sender = '',receiver = '',msg = '',group_name = None, aes_key=b''):
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.msg = msg
        self.aes_key = aes_key
        self.group_name = group_name