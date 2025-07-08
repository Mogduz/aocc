from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import pickle

class CryptoObject:

    def __init__(self, salt: str, password: str) -> None:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(encoding='utf-8'),
            iterations=390_000,
        )
        key_derived = kdf.derive(password.encode(encoding='utf-8'))
        key = base64.urlsafe_b64encode(key_derived)
        self._fernet_object: Fernet = Fernet(key)

    def encrypt_object(self, obj: any) -> bytes:
        return self._fernet_object.encrypt(data=pickle.dumps(obj))

    def decrypt_object(self, enc_obj: bytes) -> any:
        return pickle.loads(self._fernet_object.decrypt(enc_obj))
    
    @staticmethod
    def genereate_random_secret(size: int = 32, shuffle: bool = False, shuffle_rounds: int = 100) -> str:
        import string, secrets
        signs: str = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.punctuation
        if shuffle:
            signs: str = CryptoObject.shuffle_string(string=signs, rounds=shuffle_rounds)
        return ''.join(secrets.choice(signs) for _ in range(size))

    @staticmethod
    def shuffle_string(string: str, rounds: int = 1) -> str:
        import random, time
        for i in range(0, rounds):
            signs: list = list(string)
            random.seed(time.time() * (i / 1000))
            random.shuffle(x=signs)
            string: str = ''.join(signs)
            time.sleep(i / 100000)
        return string