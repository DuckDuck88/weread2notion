import time
from flask import Flask, render_template, request, Response

from weread_2_notion import weread_2_notion

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


if __name__ == '__main__':
    app.run(port=5000, debug=True)
