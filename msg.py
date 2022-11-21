class msg:
    def __init__(self,type = '',sender = '',receiver = '',msg = ''):
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.length = len(msg)
        self.msg = msg

class group_msg:
    def __init__(self,type = '',sender = '',group_name = '',msg = ''):
        self.type = type
        self.sender = sender
        self.receiver = group_name
        self.length = len(msg)
        self.msg = msg