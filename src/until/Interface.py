import requests
import json
import os
import shutil

from .Constant import API, TMP_DIR
from .Unzip import unzip_mm
from .EpubCreate import export_epub


def mkdir(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


def search(key: str, header: dict) -> list:
    body = requests.get(API['search'].replace('{{key}}', key), headers=header).json()
    try:
        with open(f'{TMP_DIR}/search.json', 'w', encoding='utf-8') as f:
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

        with open(f'{TMP_DIR}/{bid}/detail.json', 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=4)

        print(json.dumps(body, ensure_ascii=False, indent=4))
        return body
    except BaseException as err:
        print('detail error: ', err)
        return {}


def toc(bid: str, header: dict) -> list:
    try:
        post_json = {'bookIds': [bid], 'synckeys': [0]}
        body = requests.post(API['toc'], json=post_json, headers=header).json()

        with open(f'{TMP_DIR}/{bid}/toc.json', 'w', encoding='utf-8') as f:
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
        with open(f'{TMP_DIR}/{bid}/zip/{idx}.zip', 'wb') as f:
            f.write(res.content)
        return {'encryptkey': encrypt_key, 'path': f'{TMP_DIR}/{bid}/zip/{idx}.zip'}
    except BaseException as err:
        print('zip_download error: ', err)
        return {}


def download_chapters(book_id: str, book_toc: list, headers: dict) -> None:
    try:
        num = 1  # random.randint(0, 1)
        if num == 1:
            ch = book_toc[0]
            print(f"全书下载")
            zip_content = zip_download(ch['all_chapter'], book_id, str(ch['chapterIdx']), headers)
            print(zip_content)
            unzip_mm(headers.get('vid'), zip_content['encryptkey'], zip_content['path'],
                     f'{TMP_DIR}/{book_id}/content')
        else:
            for ch in book_toc:
                print(f"第{ch['chapterIdx']}章下载")
                zip_content = zip_download(ch['url'], book_id, str(ch['chapterIdx']), headers)
                print(zip_content)
                unzip_mm(headers.get('vid'), zip_content['encryptkey'], zip_content['path'],
                         f'{TMP_DIR}/{book_id}/content')
    except BaseException as err:
        print('download_chapters error: ', err)
    return None


def login_check(header: dict) -> bool:
    try:
        res = requests.get(API['login_check'], headers=header)
        if res.status_code == 200:
            print(f'登录成功')
            return True
        else:
            print('登录失败,请更新该目录下mmread.json文件中的请求头')
            return False
    except BaseException as err:
        print('login_check error: ', err)
        return False


def run(headers):
    mkdir(TMP_DIR)
    search_key = input('输入要搜索的书籍: ')
    book_list = search(search_key, headers)
    book_id = input('\n\n请输入format为epub的书籍的bookId: ')

    mkdir(f'{TMP_DIR}/{book_id}/zip')
    mkdir(f'{TMP_DIR}/{book_id}/content')

    book_info = detail(book_id, headers)
    if book_info['format'] != 'epub':
        print('本书不是epub，请选择epub格式的书籍下载')
        run(headers)

    book_toc = toc(book_id, headers)

    print('\n' * 3)
    download_chapters(book_id, book_toc, headers)
    print('epub生成中...')
    export_epub(f'{TMP_DIR}/{book_id}')
    # shutil.rmtree(TMP_DIR)
    print('任务结束')
