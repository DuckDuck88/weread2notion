from logger import info, exception
from weread_2_notion import weread_2_notion
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *

from flask import Flask

app = Flask(__name__)


def output_help_info(scope=None):
    put_collapse('使用说明', [
        put_markdown('''
        1. 获取 Notion token
            - 打开[Notion developers](https://www.notion.so/my-integrations)并登录
            - 点击New integration 输入 name 提交.(如果已有，则点击 view integration)
            - 点击show，然后copy
        2. 从微信读书中获取 cookie
            - 在浏览器中打开[微信读书官网](weread.qq.com)并登录
            - 打开开发者工具(按 F12)，点击 network(网络)，刷新页面, 点击第一个请求，复制 cookie 的值。
                > ![drULBf](https://markdown-mac-work-1306720256.cos.ap-guangzhou.myqcloud.com/png/drULBf.png)
        3. 准备 Noiton Database ID
            - 复制这个[Notion 数据库](https://www.notion.so/yayya/a9b3a8dfcc0543559005a263103fc81c)到你的 Notion 中，点击右上角的分享按钮，将页面分享为公开页面
            - 点击页面右上角三个点，在 connections 中找到选择你的 connections。选择第一步中创建的 integration 的 name
            - 打开你复制的 Notion 页面，通过该页面 URL 找到你的 Database ID 。
                > 例如：页面 https://www.notion.so/xxxx/d92bb4b8434745baa2061caf67d6ef7a?v=b4a5bfb89e8e44868a473179ee60x851 的 ID 为d92bb4b8434745baa2061caf67d6ef7a
                > ![bU4zTs](https://markdown-mac-work-1306720256.cos.ap-guangzhou.myqcloud.com/png/bU4zTs.png)
        4. 把如下信息输入到以下表单中
    ''', scope=scope)
    ], open=False)


def update_configs(name, value):
    return input_update(value, name='configs')


def input_config_info(scope=None):
    with use_scope(scope):
        datas = input_group('configs', [
            input("Notion token：", type=PASSWORD, placeholder='输入 notion tikon', name='notion_token', required=True),
            input("微信读书 cookie：", type=TEXT, placeholder='输入 微信读书 cookies', name='weread_cookie',
                  required=True),
            input("Database ID:,", type=TEXT, placeholder='输入 需要同步的 Notion 数据库 ID', name='database_id',
                  required=True),
            textarea("黑名单列表：", rows=3, placeholder='输入不同步的书籍黑名单，书名以逗号隔开', name='book_blacklist')
        ])
    notion_token = datas['notion_token']
    weread_cookie = datas['weread_cookie']
    database_id = datas['database_id']
    datas['book_blacklist'] = datas['book_blacklist'].replace(' ', '').replace('\n', '').replace('\r', '').split(',')
    book_blacklist = datas['book_blacklist']
    return notion_token, weread_cookie, database_id, book_blacklist


def list_to_str(l):
    res = ""
    for i in l:
        res += f'*《{i}》*  '
    return '> ' + res if res else '> 无'


def weread_to_notion():
    output_help_info(scope='head')
    # put_column([
    #     put_scope('head'),
    #     put_scope('main'),
    #     put_row([
    #         put_scope('left'),
    #         None,
    #         put_scope('right')
    #     ], size='25% 4% 69%'),
    # ])
    notion_token, weread_cookie, database_id, book_blacklist = input_config_info(scope='main')
    put_info('注意: 书籍较多时处理时间较长，当前页面可观察同步进度，关闭页面可以继续同步')
    try:
        with put_loading(shape='grow', color='primary'):
            all_book, handled_book, ignore_book = weread_2_notion(notion_token,
                                                                  weread_cookie,
                                                                  database_id,
                                                                  book_blacklist)
    except Exception as e:
        exception(f'失败:{str(e)}')
        put_error(f'{str(e)}', closable=False)
        return put_error(f'请刷新当前页面重新输入正确配置', closable=True)
    put_info(f'共有{len(all_book)}本书籍，其中{len(ignore_book)}本书籍被忽略，{len(handled_book)}本书籍被同步')
    put_markdown(f'**成功同步以下书籍**:\n{list_to_str(handled_book)}')
    put_markdown(f'**忽略以下书籍**:\n{list_to_str(ignore_book)}')
    return put_success(f'共有{len(all_book)}本书籍，其中{len(ignore_book)}本书籍被忽略，{len(handled_book)}本书籍被同步',
                       closable=True)


app.add_url_rule('/', 'webio_view', webio_view(weread_to_notion),
                 methods=['GET', 'POST'])  # need GET,POST and OPTIONS methods

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
