import time

import pywebio
from flask import Flask, render_template, request, Response

from weread_2_notion import weread_2_notion
from pywebio.platform.flask import webio_view
from pywebio.input import input, TEXT, input_group, textarea, PASSWORD
from pywebio.output import put_text, put_button, put_error, put_success

from flask import Flask

app = Flask(__name__)


@app.route('/wereadtonotion2', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        notion_token = request.form['notion_token']
        weread_cookie = request.form['weread_cookie']
        database_id = request.form['database_id']
        book_blacklist = request.form.getlist('book_blacklist')
        try:
            res = weread_2_notion(notion_token, weread_cookie, database_id, book_blacklist)
        except Exception as e:
            return Response(str(e), mimetype='text/plain')

        return Response(res, mimetype='text/plain')

    return render_template('wereadtonotion.html')


def weread_to_noiton():
    datas = input_group('configs', [
        input("Notion token：", type=PASSWORD, placeholder='输入 notion tikon', name='notion_token'),
        input("微信读书 cookie：", type=PASSWORD, placeholder='输入 微信读书 cookies', name='weread_cookie'),
        input("Database ID:,", type=PASSWORD, placeholder='输入 需要同步的 Notion 数据库 ID', name='database_id'),
        textarea("黑名单列表：", rows=3, placeholder='输入书籍黑名单列表,', name='book_blacklist')
    ])
    notion_token = datas['notion_token']
    weread_cookie = datas['weread_cookie']
    database_id = datas['database_id']
    datas['book_blacklist'] = datas['book_blacklist'].split(',')
    book_blacklist = datas['book_blacklist']
    print(datas)
    put_text(datas)
    try:
        res = weread_2_notion(notion_token, weread_cookie, database_id, book_blacklist)
        # res = 1 / int(notion_token)
    except Exception as e:
        put_error(e, closable=False)
        put_button('修改', onclick=weread_to_noiton)

    return put_success('成功:' + str(res), closable=True)


app.add_url_rule('/weread_to_noiton', 'webio_view', webio_view(weread_to_noiton),
                 methods=['GET', 'POST'])  # need GET,POST and OPTIONS methods

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
