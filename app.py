from logger import info, exception
from weread_2_notion import weread_2_notion
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *

from flask import Flask

app = Flask(__name__)


def output_help_info():
    put_collapse('使用说明', [
        put_markdown('''
        1. 获取 Notion token
            - 打开[此页面](https://www.notion.so/my-integrations)并登录
            - 点击New integration 输入 name 提交.(如果已有，则点击 view integration)
            - 点击show，然后copy
        2. 从微信读书中获取 cookie
            - 在浏览器中打开 weread.qq.com 并登录
            - 打开开发者工具(按 F12)，点击 network(网络)，刷新页面, 点击第一个请求，复制 cookie 的值。
        3. 准备 Noiton Database ID
            - 复制[此页面](https://www.notion.so/yayya/d92bb4b8434745baa2061caf67d6ef7a?v=b4a5bfb89e8e44868a473179ee608851)到你的 Notion 中，点击右上角的分享按钮，将页面分享为公开页面
            - 点击页面右上角三个点，在 connections 中找到选择你的 connections。第一步中创建的 integration 的 name
            - 通过 URL 找到你的 Database ID 的值。
                > 例如：页面 https://www.notion.so/yayya/d92bb4b8434745baa2061caf67d6ef7a?v=b4a5bfb89e8e44868a473179ee60x851 的 ID 为d92bb4b8434745baa2061caf67d6ef7a
        4. 把如下信息输入到以下表单中
    ''')
    ], open=False)


def weread_to_noiton():
    output_help_info()
    datas = input_group('configs', [
        input("Notion token：", type=PASSWORD, placeholder='输入 notion tikon', name='notion_token'),
        input("微信读书 cookie：", type=TEXT, placeholder='输入 微信读书 cookies', name='weread_cookie'),
        input("Database ID:,", type=TEXT, placeholder='输入 需要同步的 Notion 数据库 ID', name='database_id'),
        textarea("黑名单列表：", rows=3, placeholder='输入不想同步的书籍黑名单，每本书以逗号隔开', name='book_blacklist')
    ])
    notion_token = datas['notion_token']
    weread_cookie = datas['weread_cookie']
    database_id = datas['database_id']
    datas['book_blacklist'] = datas['book_blacklist'].replace(' ', '').replace('\n', '').replace('\r', '').split(',')
    book_blacklist = datas['book_blacklist']
    info(f'输入信息：{datas}')
    try:
        with put_loading():
            res = weread_2_notion(notion_token, weread_cookie, database_id, book_blacklist)
        # res = browsercookie.load()
        # res = 1 / int(notion_token)
    except Exception as e:
        put_error(e, closable=False)
        put_button('修改', onclick=weread_to_noiton)
        exception('失败:' + str(e))
    put_button('修改', onclick=weread_to_noiton)
    return put_success('成功:' + str(res), closable=True)


app.add_url_rule('/', 'webio_view', webio_view(weread_to_noiton),
                 methods=['GET', 'POST'])  # need GET,POST and OPTIONS methods

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
