import zipfile
from .Aes import aes_decode
from .Constant import WORK_LOG


# 获取AES解密的key和iv
def get_aes_key_iv(vid: str) -> dir:
    byte_array = []
    while len(byte_array) < 32:
        byte = vid.encode(encoding="utf-8")
        byte_array.extend(byte)
    arr1 = byte_array[0:16]
    arr2 = byte_array[16:32]
    key = bytes(arr1).decode('utf-8')
    iv = bytes(arr2).decode('utf-8')
    return {'key': key, 'iv': iv}


# 获取解压密码，vid为用户id，encryptkey可从正文的响应头获取
def get_unzip_key(vid: str, encrypt_key: str) -> str:
    aes_key_iv = get_aes_key_iv(vid)
    return aes_decode(encrypt_key, aes_key_iv.get('key'), aes_key_iv.get('iv'))


# 文件解压
def unzip_file(zip_path: str, password: str = None, folder_path: str = None):
    try:
        zip_file = zipfile.ZipFile(zip_path)  # 文件的路径与文件名
        zip_list = zip_file.namelist()  # 得到压缩包里所有文件
        for f in zip_list:
            zip_file.extract(f, folder_path, pwd=password.encode("utf-8"))  # 循环解压文件到指定目录
        zip_file.close()  # 关闭文件，必须有，释放内存
    except Exception as e:
        WORK_LOG.error(f'Unzip Error: {e}')


# 解压微信阅读出版书
def unzip_mm(vid: str, encrypt_key: str, zip_path: str, folder_path: str = None):
    pwd = get_unzip_key(vid, encrypt_key)
    unzip_file(zip_path, pwd, folder_path)
    WORK_LOG.info(f'{zip_path} 解压成功,密码: {pwd}')
