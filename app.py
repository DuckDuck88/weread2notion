import time
from flask import Flask, render_template, request, Response

from weread_2_notion import weread_2_notion
from pywebio.platform.flask import webio_view
from pywebio.input import input, TEXT
from pywebio.output import put_text

from flask import Flask

app = Flask(__name__)


@app.route('/wereadtonotion', methods=['GET', 'POST'])
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


def test():
    height = input("Notion tken(cm)：", type=TEXT)
    weight = input(" 微信读书 cookies(kg)：", type=TEXT)

    # BMI = weight / (height / 100) ** 2

    top_status = [(14.9, '极瘦'), (18.4, '偏瘦'),
                  (22.9, '正常'), (27.5, '过重'),
                  (40.0, '肥胖'), (float('inf'), '非常肥胖')]

    put_text('这是输出')


app.add_url_rule('/test', 'webio_view', webio_view(test),
                 methods=['GET'])  # need GET,POST and OPTIONS methods

if __name__ == '__main__':
    app.run(port=5000, debug=True)
