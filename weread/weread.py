import hashlib
import re
from http.cookies import SimpleCookie
import requests
from requests.utils import cookiejar_from_dict
from logger import error


class WeRead:
    WEREAD_URL = "https://weread.qq.com/"
    WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/user/notebooks"
    # WEREAD_NOTEBOOKS_URL = "https://i.weread.qq.com/shelf/friendCommon"
    WEREAD_BOOKMARKLIST_URL = "https://i.weread.qq.com/book/bookmarklist"
    WEREAD_CHAPTER_INFO = "https://i.weread.qq.com/book/chapterInfos"
    WEREAD_READ_INFO_URL = "https://i.weread.qq.com/book/readinfo"
    WEREAD_REVIEW_LIST_URL = "https://i.weread.qq.com/review/list"
    WEREAD_BOOK_INFO = "https://i.weread.qq.com/book/info"

    def __init__(self, weread_cookie):
        self.session = requests.Session()
        self.session.cookies = self.parse_cookie_string(weread_cookie)

    def get_bookmark_list(self, bookId):
        """获取我的划线"""
        params = dict(bookId=bookId)
        r = self.session.get(self.WEREAD_BOOKMARKLIST_URL, params=params)
        if r.ok:
            updated = r.json().get("updated")
            updated = sorted(updated, key=lambda x: (
                x.get("chapterUid", 1), int(x.get("range").split("-")[0])))
            return r.json()["updated"]
        return None

    def get_bookinfo(self, bookId):
        """获取书的详情"""
        params = dict(bookId=bookId)
        r = self.session.get(self.WEREAD_BOOK_INFO, params=params)
        isbn = ""
        newRating = 0
        intro = ""
        category = ""
        if r.ok:
            data = r.json()
            isbn = data.get("isbn", "-1")
            newRating = data.get("newRating", '-1') / 1000
            intro = data.get('intro', '本书没有介绍！')
            category = data.get("category", 'None')
        return (isbn, newRating, intro, category)

    def get_review_list(self, bookId):
        """获取笔记"""
        params = dict(bookId=bookId, listType=11, mine=1, syncKey=0)
        r = self.session.get(self.WEREAD_REVIEW_LIST_URL, params=params)
        reviews = r.json().get("reviews")
        summary = list(filter(lambda x: x.get("review").get("type") == 4, reviews))
        reviews = list(filter(lambda x: x.get("review").get("type") == 1, reviews))
        reviews = list(map(lambda x: x.get("review"), reviews))
        reviews = list(map(lambda x: {**x, "markText": x.pop("content")}, reviews))
        return summary, reviews

    def get_read_info(self, bookId):
        params = dict(bookId=bookId, readingDetail=1,
                      readingBookIndex=1, finishedDate=1)
        r = self.session.get(self.WEREAD_READ_INFO_URL, params=params)
        if r.ok:
            return r.json()
        return None

    def _transform_id(self, book_id):
        id_length = len(book_id)

        if re.match("^\d*$", book_id):
            ary = []
            for i in range(0, id_length, 9):
                ary.append(format(int(book_id[i:min(i + 9, id_length)]), 'x'))
            return '3', ary

        result = ''
        for i in range(id_length):
            result += format(ord(book_id[i]), 'x')
        return '4', [result]

    def calculate_book_str_id(self, book_id):
        md5 = hashlib.md5()
        md5.update(book_id.encode('utf-8'))
        digest = md5.hexdigest()
        result = digest[0:3]
        code, transformed_ids = self._transform_id(book_id)
        result += code + '2' + digest[-2:]

        for i in range(len(transformed_ids)):
            hex_length_str = format(len(transformed_ids[i]), 'x')
            if len(hex_length_str) == 1:
                hex_length_str = '0' + hex_length_str

            result += hex_length_str + transformed_ids[i]

            if i < len(transformed_ids) - 1:
                result += 'g'

        if len(result) < 20:
            result += digest[0:20 - len(result)]

        md5 = hashlib.md5()
        md5.update(result.encode('utf-8'))
        result += md5.hexdigest()[0:3]
        return result

    def get_chapter_info(self, bookId):
        """获取章节信息"""
        body = {
            'bookIds': [bookId],
            'synckeys': [0],
            'teenmode': 0
        }
        r = self.session.post(self.WEREAD_CHAPTER_INFO, json=body)
        if r.ok and "data" in r.json() and len(r.json()["data"]) == 1 and "updated" in r.json()["data"][0]:
            update = r.json()["data"][0]["updated"]
            return {item["chapterUid"]: item for item in update}
        return None

    def get_notebooklist(self):
        """获取笔记本列表"""
        # params = dict(userVid=self.session.cookies.get("wr_vid"))
        r = self.session.get(self.WEREAD_NOTEBOOKS_URL)
        if not r.ok:
            error(f'获取图书失败,{r.text}')
            raise RuntimeError(f'获取图书失败,{r.text}')
        data = r.json()
        books = data.get("books")
        books.sort(key=lambda x: x["sort"])
        return books

    def parse_cookie_string(self, cookie_string):
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        cookies_dict = {}
        cookiejar = None
        for key, morsel in cookie.items():
            cookies_dict[key] = morsel.value
            cookiejar = cookiejar_from_dict(
                cookies_dict, cookiejar=None, overwrite=True
            )
        return cookiejar
