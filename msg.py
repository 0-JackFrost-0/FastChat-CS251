class msg:
    """The class is used to send messages between servers and clients, it carries all the information 
        for each message.
    """
    def __init__(self,type = '',sender = '',receiver = '',msg = '',group_name = None, aes_key=b''):
        """The constructor for the msg class

        :param type: Denotes the message type, it informs the server what information does the message carry. Defaults to ''.
        :type type: str, optional
        :param sender: Contains the senders username. Defaults to ''.
        :type sender: str, optional
        :param receiver: Contains the receivers username. Defaults to ''.
        :type receiver: str, optional
        :param msg: Is the main message to be delivered. Defaults to ''.
        :type msg: str, optional
        :param group_name: If the message was direct, then its empty, else the message is in a group, then contains the group name. Defaults to None.
        :type group_name: _type_, optional
        :param aes_key: The rsa encrypted aes key. Defaults to b''.
        :type aes_key: bytes, optional
        """
        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.msg = msg
        self.aes_key = aes_key
        self.group_name = group_name