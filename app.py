import os, json
import time
from src import *
import requests


def get_header() -> dict:
    try:
        if not os.path.isfile('mmread.json'):
            with open('mmread.json', 'w', encoding='utf-8') as f:
                json.dump(default_headers, f, indent=4)
            header = default_headers
            print('请更新该目录下mmread.json文件中的请求头')
        else:
            with open('mmread.json', 'r', encoding='utf-8') as f:
                header = json.load(f)
        return header
    except BaseException as err:
        print('get_header error: ', err)
        return {}


def main() -> None:
    while True:
        headers = get_header()
        if login_check(headers):
            break
        time.sleep(5)
    run(headers)


if __name__ == '__main__':
    try:
        _url = 'https://ghproxy.com/https://raw.githubusercontent.com/celetor/SourceGo/main/.github/scripts/mmread.json'
        version_check = requests.get(_url).json().get('code')
    except BaseException as e:
        version_check = 0
        print('version check error: ', e)
    if int(version_check) > 4:
        print('版本V1.5, 校验通过')
        main()
    else:
        print('软件版本校验失败，请更新后重试...')
    print('15秒后自动退出...')
    time.sleep(15)
