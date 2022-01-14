import sys
import os
import json
import shutil
import requests
import re

from PyQt5.Qt import QThread, pyqtSignal
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem

from src import *


def get_header() -> dict:
    try:
        if not os.path.isfile('mmread.json'):
            with open('mmread.json', 'w', encoding='utf-8') as f:
                json.dump(default_headers, f, indent=4)
            header = default_headers
            WORK_LOG.info('请更新该目录下mmread.json文件中的请求头')
        else:
            with open('mmread.json', 'r', encoding='utf-8') as f:
                header = json.load(f)
        return header
    except BaseException as err:
        WORK_LOG.error(f'get_header error: {err}')
        return {}


def version_check():
    try:
        _url = 'https://cdn.jsdelivr.net/gh/celetor/SourceGo@main/.github/scripts/mmread.json'
        _version_check = requests.get(_url).json().get('code')
    except Exception:
        _version_check = 0
        WORK_LOG.error('internet error')
    if int(_version_check) > 4:
        WORK_LOG.info('版本V1.5, 校验通过')
        return True
    else:
        WORK_LOG.info('软件版本校验失败，请更新后重试...')
        return False


# 工作线程
class WorkThread(QThread):
    signal = pyqtSignal(int, object)

    def __init__(self):
        super().__init__()
        self.headers = {}
        self.obj = {}

    def set_object(self, obj):
        self.obj = obj

    def run_login_check(self):
        self.headers = get_header()
        if login_check(self.headers):
            self.signal.emit(0, '有效')
        else:
            self.signal.emit(0, '失效')

    def search_book(self, keyword):
        mkdir(TMP_DIR)
        book_list = search(keyword, self.headers)
        self.signal.emit(1, book_list)

    def download_one_book(self, name, book_id):
        mkdir(f'{TMP_DIR}/{book_id}/zip')
        mkdir(f'{TMP_DIR}/{book_id}/content')

        book_info = detail(book_id, self.headers)
        book_toc = toc(book_id, self.headers)
        download_chapters(book_info, book_toc, self.headers)
        if book_info['format'] == 'epub':
            export_epub(f'{TMP_DIR}/{book_id}')
        else:
            content = [
                f'书名:{book_info["title"]}\n作者:{book_info["author"]}\n封面:{book_info["cover"]}\n简介:{book_info["intro"]}']
            bk_list = os.listdir(f'{TMP_DIR}/{book_id}/zip')
            bk_list.sort(key=lambda x: int(re.match(r'(\d+)\.txt', x).group(1)))
            for ch in book_toc:
                idx = ch['chapterIdx']
                content.append(f'第{idx}章 {ch["title"]}\n　　字数:{ch["wordCount"]}')
                path = f'{TMP_DIR}/{book_id}/zip/{idx}.txt'
                if os.path.isfile(path):
                    f = open(path, 'r', encoding='utf-8')
                    con = f.readlines()
                    f.close()
                    con[0] = re.sub(r'info\.txt.*ustar\s*', '', con[0]).strip(b'\x00'.decode())
                    con = ''.join(con)
                else:
                    con = ''
                content.append(con)
            content = '\n'.join(content)
            f = open(f'./{book_info["title"]}.txt', 'w', encoding='utf-8')
            f.write(content)
            f.close()

        self.signal.emit(2, f'{name} 下载完成')

    def run(self):
        index = self.obj['index']
        if index == 0:
            self.run_login_check()
        elif index == 1:
            self.search_book(self.obj.get('keyword'))
        elif index == 2:
            self.download_one_book(self.obj.get('name'), self.obj.get('bid'))
        elif index == 3:
            shutil.rmtree(TMP_DIR)


# UI主线程
class AppMainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(AppMainWin, self).__init__(parent)

        self.thread_1 = None
        self.book_list = []

        self.setupUi(self)
        self.init()
        self.signal_connect_slot()

    def init(self):
        self.listWidget.setIconSize(QSize(300, 200))
        self.listWidget.setSpacing(5)  # item间距(上下左右)
        self.pushButton.setEnabled(False)

    def signal_connect_slot(self):
        self.pushButton.clicked.connect(self.on_search_clicked)
        self.pushButton_2.clicked.connect(self.on_check_clicked)
        self.pushButton_3.clicked.connect(self.on_clear_clicked)

        self.thread_1 = WorkThread()
        self.thread_1.signal.connect(self.events)

    def events(self, key, msg):
        if key == 0:  # 检查登录
            self.lineEdit_2.setText(msg)
            if msg == '有效':
                self.pushButton_2.setEnabled(False)
                self.pushButton.setEnabled(True)
            else:
                self.pushButton_2.setEnabled(True)
                self.pushButton.setEnabled(False)
        elif key == 1:
            self.clear_item()
            self.book_list = []
            for bk in msg:
                if bk.get('bookInfo') is not None:
                    bk = bk.get('bookInfo')
                if bk.get('bookId') is None:
                    continue
                item = QListWidgetItem(self.listWidget)
                bk_info = {
                    'bookId': bk['bookId'],
                    'title': bk['title'],
                    'author': bk['author'],
                    'intro': bk['intro'],
                    'cover': bk['cover'],
                    'format': bk['format']
                }
                self.book_list.append(bk_info)

                widget = ItemWidget(bk_info, item, self.listWidget)
                # 绑定删除信号
                widget.itemDeleted.connect(self.download_book)
                self.listWidget.setItemWidget(item, widget)
        else:
            self.statusbar.showMessage(msg)
            print(msg)

    def on_check_clicked(self):
        self.thread_1.set_object({'index': 0})
        self.thread_1.start()

    def on_search_clicked(self):
        keyword = self.lineEdit.text()
        self.thread_1.set_object({'index': 1, 'keyword': keyword})
        self.thread_1.start()

    def on_clear_clicked(self):
        if os.path.exists(TMP_DIR):
            self.thread_1.set_object({'index': 3})
            self.thread_1.start()
        self.statusbar.showMessage(f'缓存清理成功')

    def download_book(self, item):
        index = self.listWidget.indexFromItem(item).row()
        bk = self.book_list[index]
        name = bk.get('title')
        bid = bk.get('bookId')
        self.statusbar.showMessage(f'{name} 下载中...')
        self.thread_1.set_object({'index': 2, 'name': name, 'bid': bid})
        self.thread_1.start()

    def clear_item(self):
        # 清空所有Item
        for _ in range(self.listWidget.count()):
            # 删除item
            # 一直是0的原因是一直从第一行删,删掉第一行后第二行变成了第一行
            # 这个和删除list [] 里的数据是一个道理
            item = self.listWidget.takeItem(0)
            # 删除widget
            self.listWidget.removeItemWidget(item)
            del item


if __name__ == '__main__':
    if version_check():
        app = QApplication(sys.argv)
        window = AppMainWin()  # 类名,注意要和自己定义的类名一致。
        window.setWindowIcon(QIcon(os.path.join(os.getcwd(), "resource", "ic_launcher.ico")))
        window.show()
        sys.exit(app.exec_())
