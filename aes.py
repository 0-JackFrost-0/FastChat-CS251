from Crypto import Random
from Crypto.Cipher import AES

# Referenced from the-javapocalypse on github, https://github.com/the-javapocalypse/Python-File-Encryptor
class AESEncryptor:
    """ The AES encryptor is used to provide E2E encryption for communication.
    """
    def __init__(self, key):
        """The default constructor for the encryptor, 

        :param key: the default key, although this isn't used, as we generate new keys for every message
        :type key: bytes
        """
        self.key = key

    def pad(self, s):
        """Adds padding to the message

        :param s: the message to be padded
        :type s: str
        :return: the padded message in bytes
        :rtype: bytes
        """
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key):
        """Encrypts a message, with a given key

        :param message: The message to be encrypted
        :type message: str
        :param key: The key to be used for encryption
        :type key: bytes
        :return: Returns the ciphered text
        :rtype: bytes
        """
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def decrypt(self, ciphertext, key):
        """Decrypts the cipher text with the provided key

        :param ciphertext: The ciphered text which is to be deciphered
        :type ciphertext: bytes
        :param key: The key to be used for deciphering
        :type key: bytes
        :return: Returns the original message, in bytes form
        :rtype: bytes
        """
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")