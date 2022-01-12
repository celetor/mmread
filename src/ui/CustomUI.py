from PyQt5.Qt import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QTextBrowser, QHBoxLayout, QVBoxLayout, QPushButton, QListWidgetItem

import requests


class ItemWidget(QWidget):
    itemDeleted = pyqtSignal(QListWidgetItem)

    def __init__(self, book_info, item, *args, **kwargs):
        super(ItemWidget, self).__init__(*args, **kwargs)
        self._item = item  # 保留list item的对象引用
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(book_info['cover']).content)
        self._item.setIcon(QIcon(pixmap))

        # 总部局-垂直
        verticalLayout = QVBoxLayout(self)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.addWidget(QLabel(f'《{book_info["title"]}》', self))
        # 水平布局
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(QLabel(f'作者: {book_info["author"]}', self))
        bt = QPushButton(self)
        bt.setText(f'下载 {book_info["format"].upper()}')
        bt.clicked.connect(self.download)
        bt.setMaximumWidth(100)
        horizontalLayout.addWidget(bt)
        verticalLayout.addLayout(horizontalLayout)
        # 简介
        intro = QTextBrowser(self)
        intro.setText(book_info["intro"])
        verticalLayout.addWidget(intro)

    def download(self):
        self.itemDeleted.emit(self._item)
