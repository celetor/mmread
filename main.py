import json
import requests
import os
import time
import shutil
import random
from until import *


def mkdir(path: str) -> bool:
    if os.path.exists(path):
        return False
    else:
        os.makedirs(path)
        return True


def search(key: str, header: dict) -> list:
    body = requests.get(API['search'].replace('{{key}}', key), headers=header).json()
    try:
        with open(f'./search.json', 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=4)
        bk_list = []
        for bk in body.get('books'):
            info = bk.get('bookInfo')
            if info.get('format') == 'epub':
                bk_list.append(info)
        print(json.dumps(bk_list, ensure_ascii=False, indent=4))
        return bk_list
    except BaseException as err:
        print('search error: ', err)
        if isinstance(body.get('books'), list):
            return body.get('books')
        else:
            return []


def detail(bid: str, header: dict) -> dict:
    try:
        body = requests.get(API['detail'].replace('{{bookId}}', bid), headers=header).json()

        with open(f'./{bid}/detail.json', 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=4)

        # 下载封面
        # res = requests.get(body.get('cover'))
        # with open(f'./{bid}/cover.jpg', 'wb') as f:
        #     f.write(res.content)

        print(json.dumps(body, ensure_ascii=False, indent=4))
        return body
    except BaseException as err:
        print('detail error: ', err)
        return {}


def toc(bid: str, header: dict) -> list:
    try:
        post_json = {
            'bookIds': [bid], 'synckeys': [0]
        }
        body = requests.post(API['toc'], json=post_json, headers=header).json()

        with open(f'./{bid}/toc.json', 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=4)

        json_data = body['data']

        # 把数组融合
        all_list = []
        for t in json_data:
            all_list.extend(t['updated'])
        for t in all_list:
            t['url'] = API['content'].replace('{{format}}', json_data[0]['book']['format']) \
                .replace('{{bookId}}', bid).replace('{{chapterUid}}', str(t['chapterUid']))

        first_uid = all_list[0]['chapterUid']
        last_uid = all_list[-1]['chapterUid']
        all_list[0]['all_chapter'] = API['content'].replace('{{format}}', json_data[0]['book']['format']) \
            .replace('{{bookId}}', bid).replace('{{chapterUid}}', f"{first_uid}-{last_uid}")

        print(json.dumps(all_list, ensure_ascii=False, indent=4))

        return all_list
    except BaseException as err:
        print('toc error', err)
        return []


def zip_download(url: str, bid: str, idx: str, header: dict) -> dict:
    try:
        res = requests.get(url, timeout=15000, headers=header)
        encrypt_key = res.headers.get('encryptkey')
        with open(f'./{bid}/zip/{idx}.zip', 'wb') as f:
            f.write(res.content)
        return {
            'encryptkey': encrypt_key,
            'path': f'./{bid}/zip/{idx}.zip'
        }
    except BaseException as err:
        print('zip_download error: ', err)
        return {}


def login_check(header: dict) -> bool:
    try:
        res = requests.get(API['login_check'], headers=header)
        if res.status_code == 200:
            print(f'登录成功')
            return True
        else:
            print('登录失败,请更新该目录下mmread.config文件中的请求头')
            return False
    except BaseException as err:
        print('login_check error: ', err)
        return False


def get_header() -> dict:
    try:
        if not os.path.isfile('./mmread.config'):
            with open('./mmread.config', 'w', encoding='utf-8') as f:
                json.dump(default_headers, f, indent=4)
            header = default_headers
            print('请更新该目录下mmread.config文件中的请求头')
        else:
            with open('./mmread.config', 'r', encoding='utf-8') as f:
                header = json.load(f)
        return header
    except BaseException as err:
        print('get_header error: ', err)
        return {}


def download_chapters(book_id: str, book_toc: list, headers: dict) -> None:
    try:
        num = random.randint(0, 1)
        if num == 1:
            ch = book_toc[0]
            print(f"全书下载")
            zip_content = zip_download(ch['all_chapter'], book_id, str(ch['chapterIdx']), headers)
            print(zip_content)
            unzip_mm(headers.get('vid'), zip_content['encryptkey'], zip_content['path'],
                     f'./{book_id}/content')
        else:
            for ch in book_toc:
                print(f"第{ch['chapterIdx']}章下载")
                zip_content = zip_download(ch['url'], book_id, str(ch['chapterIdx']), headers)
                print(zip_content)
                unzip_mm(headers.get('vid'), zip_content['encryptkey'], zip_content['path'],
                         f'./{book_id}/content')
    except BaseException as err:
        print('download_chapters error: ', err)
    return None


def main() -> None:
    headers = get_header()
    if not login_check(headers):
        headers = get_header()
        return

    search_key = input('输入要搜索的书籍: ')
    book_list = search(search_key, headers)
    book_id = input('\n\n请输入format为epub的书籍的bookId: ')
    # book_id = '29125598'
    mkdir(f'./{book_id}/zip')
    mkdir(f'./{book_id}/content')

    book_info = detail(book_id, headers)
    if book_info['format'] != 'epub':
        print('本书不是epub，请选择epub格式的书籍下载')
        main()

    book_toc = toc(book_id, headers)

    print('\n' * 3)
    download_chapters(book_id, book_toc, headers)
    # re_download_image(book_id)
    shutil.rmtree(f'./{book_id}/zip')
    print('epub生成中...')
    export_epub(f'./{book_id}')
    print('任务结束')


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
    # export_epub(r'F:\wechat_read\dist\29125598')
    print('15秒后自动退出...')
    time.sleep(15)
