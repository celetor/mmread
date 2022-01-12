import os
from .LogUntils import Logger

TMP_DIR = os.path.join(os.path.expanduser('~'), 'Documents', '.mmread')
WORK_LOG = Logger('./mmread.log', level='debug').logger

API = {
    'login_check': 'https://i.weread.qq.com/review/feeds?count=20&listMode=1&listType=1',
    'search': 'https://i.weread.qq.com/store/search?keyword={{key}}',
    'detail': 'https://i.weread.qq.com/book/info?bookId={{bookId}}&myzy=1&source=reading',
    'toc': 'https://i.weread.qq.com/book/chapterInfos',
    'content': 'https://i.weread.qq.com/book/chapterdownload?pf=wechat_wx-2001-android-100-weread&pfkey=pfKey&zoneId=1&bookVersion=0&bookType={{format}}&quote=&release=1&stopAutoPayWhenBNE=1&preload=0&bookId={{bookId}}&chapters={{chapterUid}}'
}

default_headers = {
    "accesstoken": "input",
    "vid": "input",
    "baseapi": "30",
    "appver": "4.6.5.10145867",
    "user-agent": "WeRead/4.6.5 WRBrand/other Dalvik/2.1.0 (Linux; U; Android 11; HUAWEI2012 Build/RP1A.201005.001)",
    "osver": "11",
    "beta": "0",
    "channelid": "9",
    "basever": "4.6.5.10145867"
}

default_css = '''/*theme -> default_epub.css*/
* {
    font-size: 14px;
    font-style: normal;
    font-weight: normal;
    color: #000000;
    line-height: 1.5em;
    text-align: justify;
    text-indent: 0;
    padding: 0;
    margin: 0;
    hyphens: auto;
}

/*template -> stylesheets.css*/
.bodyPic {
    text-align: center;
    margin: 1em 0em;
}

.width30 {
    width: 30%;
}

.frontCover {
    qrfullpage: 1;
}

.manhua {
}

.bgColor-1 {
    background-color: #F2F2F2;
}

.copyRightTitle-1 {
    font-family: "汉仪旗黑65S","HY-QiHei65";
    font-size: 1.5em;
    text-align: center;
    text-indent: 0;
    margin: 1em auto 1em auto;
    background-color: #0E0C0D;
    color: #ffffff;
}

.contentCR-1 {
    font-family: "汉仪旗黑50S","HYQiHei-50s";
    font-size: 1em;
    text-indent: 0;
    text-align: center;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}

.contentCR-2 {
    font-family: "汉仪楷体","ETrump KaiTi","方正仿宋","FZFSJW--GB1-0";
    font-size: 1em;
    text-indent: 0;
    text-align: center;
    margin-top: 2em;
}

.rich_media_meta_list {
    display: none;
}

a {
    display: none;
}

body {
    background-color: #0E0C0D;
}'''
