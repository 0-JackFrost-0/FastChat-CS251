class msg:
    """Help on class msg:
    The class is used to send messages between servers and clients, it carries all the information 
    for each message.
    """
    def __init__(self,type = '',sender = '',receiver = '',msg = '',group_name = None, aes_key=b''):
        """

        Args:
            type (str, optional): Denotes the message type, it informs the server what information does the message carry.. Defaults to ''.
            sender (str, optional): Contains the senders username. Defaults to ''.
            receiver (str, optional): Contains the receivers username. Defaults to ''.
            msg (str, optional): Is the main message to be delivered. Defaults to ''.
            group_name (_type_, optional): If the message was direct, then its empty, else the message is in a group, then contains the group name. Defaults to None.
            aes_key (bytes, optional): _description_. Defaults to b''.
        """
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.msg = msg
        self.aes_key = aes_key
        self.group_name = group_name