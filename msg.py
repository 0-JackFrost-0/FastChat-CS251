class msg:
    def __init__(self,type = '',sender = '',receiver = '',msg = '',group_name = None):
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.msg = msg
        self.group_name = group_name