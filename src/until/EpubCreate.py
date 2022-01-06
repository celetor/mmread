import random
import json
import os
import hashlib
import requests
# import hashlib

from ebooklib import epub
from .Constant import default_css


class EpubBookWriter:

    def __init__(self, bookTitle, bookAuthor):
        super().__init__()

        self.book = epub.EpubBook()
        self.book.set_identifier(
            "id_" + str(random.randint(111111, 222222)) + "_" + bookTitle)

        self.book.set_title(bookTitle)
        self.book.add_author(bookAuthor)

        self.chapters = []

    def set_cover(self, file_name, content, create_page=False):
        self.book.set_cover(file_name, content, create_page)

    def addChapter(self, title, html_content, file_name, links=None, lang="zh-CN"):
        # chapter = epub.EpubHtml(title=title, file_name=file_name, content=html_content,
        #                         uid=hashlib.md5(title.encode('utf-8')).hexdigest(), lang=lang)
        chapter = epub.EpubHtml(title=title, file_name=file_name, content=html_content, lang=lang)
        if links is not None:
            chapter.add_link(href=links, rel='stylesheet', type='text/css')
        self.chapters.append(chapter)
        self.book.add_item(chapter)
        return chapter

    def addAsset(self, file_name, content, uid=None, media_type="text/css"):
        asset = epub.EpubItem(uid, file_name, media_type, content)
        self.book.add_item(asset)

    def set_toc(self, toc):
        self.book.toc = toc

    def finalizeBook(self, outputFileName):
        # self.book.toc = [epub.Link(ch.file_name, ch.title, hashlib.md5(ch.title.encode('utf-8')).hexdigest()) for ch in
        #                  self.chapters]

        self.book.add_item(epub.EpubNcx())
        # self.book.add_item(epub.EpubNav())

        # self.book.spine = ['nav', *self.chapters]
        self.book.spine = self.chapters

        epub.write_epub(outputFileName, self.book, {})


def export_epub(cache_path: str) -> None:
    try:
        with open(f'{cache_path}/detail.json', 'r', encoding='utf-8') as f:
            detail_info = json.load(f)
        title = '' if detail_info.get('title') is None else detail_info.get('title')
        author = '' if detail_info.get('author') is None else detail_info.get('author')

        book = EpubBookWriter(title, author)
        try:
            with open(f'{cache_path}/content/Images/device_phone_frontcover.jpg', 'rb') as f:
                book.set_cover('Images/device_phone_frontcover.jpg', f.read())
        except BaseException as err:
            print('cover set error: ', err)

        with open(f'{cache_path}/toc.json', 'r', encoding='utf-8') as f:
            toc_info = json.load(f).get('data')

        # 下载图片
        image_url_list = []
        for pic in os.listdir(f'{cache_path}/content/Images'):
            # 是封面就跳过
            if pic == 'device_phone_frontcover.jpg':
                continue
            try:
                with open(f'{cache_path}/content/Images/{pic}', 'r', encoding='utf-8') as f:
                    image_url = f.read()
                    image_url_list.append({
                        'url': image_url,
                        'file': f'../Images/{pic}'
                    })
                with open(f'{cache_path}/content/Images/{pic}', 'wb') as f:
                    res = requests.get(image_url).content
                    f.write(res)
            except BaseException as err:
                print('get image url error: ', pic, err)

        # 替换图片链接
        for chap in os.listdir(f'{cache_path}/content/Text'):
            chao_content = ''
            with open(f'{cache_path}/content/Text/{chap}', 'r', encoding='utf-8') as f:
                chao_content = f.read()
            for img_rep in image_url_list:
                chao_content = chao_content.replace(img_rep['url'], img_rep['file'])
            with open(f'{cache_path}/content/Text/{chap}', 'w', encoding='utf-8') as f:
                f.write(chao_content)

        for folder in os.listdir(f'{cache_path}/content'):
            if os.path.isfile(f'{cache_path}/content/{folder}') or folder == 'Text':
                continue
            for file in os.listdir(f'{cache_path}/content/{folder}'):
                if file == 'device_phone_frontcover.jpg':
                    continue
                with open(f'{cache_path}/content/{folder}/{file}', 'rb') as f:
                    book.addAsset(f'{folder}/{file}', content=f.read(), media_type='')

        # 设置css
        book.addAsset('Styles/stylesheets.css', content=default_css)

        # 把数组融合
        chapter_list = []
        for t in toc_info:
            chapter_list.extend(t['updated'])

        toc_list = []
        toc_html_list = []
        toc_lv2 = False
        # 目录栗子
        # [
        #     epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
        #     [
        #         epub.Section('Simple book'),
        #         [c1, c2, c3, ]
        #     ],
        # ]
        for ch in chapter_list:
            chapter_title = ch.get('title')
            chapter_path = ch.get('files')
            epub_html_list = []
            # 主干拼接
            for c in chapter_path:
                with open(f'{cache_path}/content/{c}', 'r', encoding='utf-8') as f:
                    text = f.read()
                    # for img_rep in image_url_list:
                    #     text = text.replace(img_rep['url'], img_rep['file'])
                    epub_html = book.addChapter(chapter_title, text.encode('utf-8'), c)
                    epub_html_list.append(epub_html)
            if len(chapter_path) > 1:
                toc_lv2 = True
                if len(toc_html_list) > 0:
                    toc_list.append(toc_html_list)
                toc_html_list = [epub.Section(chapter_title), []]
            if toc_lv2:
                toc_html_list[1].append(epub_html_list[0])
            else:
                toc_list.append(
                    epub.Link(chapter_path[0], chapter_title,
                              hashlib.md5(chapter_title.encode('utf-8')).hexdigest())
                )
        book.set_toc(toc_list)
        book.finalizeBook(f'./{title}.epub')
        print(f'导出成功: ./{title}.epub')
    except BaseException as e:
        print('export_epub error: ', e)
