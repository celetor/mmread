import base64
from .Constant import WORK_LOG

# pip install pycryptodomex
# https://pycryptodome.readthedocs.io/en/latest/src/installation.html#windows-from-sources-python-3-5-and-newer
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad
except ImportError:
    print('请安装加解密库pycryptodomex')


def aes_encode(data: str, str_key: str, str_iv: str, mode: int = AES.MODE_CBC) -> str:
    try:
        key = str_key.encode('utf-8')
        iv = str_iv.encode('utf-8')
        cipher = AES.new(key, mode, iv)
        pad_pkcs7 = pad(data.encode('utf-8'), AES.block_size, style='pkcs7')
        result = base64.encodebytes(cipher.encrypt(pad_pkcs7))
        encrypted_text = str(result, encoding='utf-8').replace('\n', '')
        return encrypted_text
    except Exception as e:
        WORK_LOG.error(f'AES Encode Error: {e}')
        return ''


def aes_decode(data: str, str_key: str, str_iv: str, mode: int = AES.MODE_CBC) -> str:
    try:
        key = str_key.encode('utf-8')
        iv = str_iv.encode('utf-8')
        cipher = AES.new(key, mode, iv)
        base64_decrypted = base64.decodebytes(data.encode('utf-8'))
        una_pkcs7 = unpad(cipher.decrypt(base64_decrypted), AES.block_size, style='pkcs7')
        decrypted_text = str(una_pkcs7, encoding='utf-8')
        return decrypted_text
    except Exception as e:
        WORK_LOG.error(f'AES Decode Error: {e}')
        return ''
