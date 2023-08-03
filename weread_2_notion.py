import time

from pywebio.output import put_text, put_info

from logger import info, debug, warning, error, exception
from notion.notion import NotionClient
from weread.weread import WeRead

try:
    from settings.settings import WEREAD_COOKIE, DATABASE_ID, BOOK_BLACKLIST, NOTION_TOKEN
except Exception as e:
    error(f'导入配置文件失败，{e} Web 无伤大雅')


def weread_2_notion(notion_token=NOTION_TOKEN,
                    weread_cookie=WEREAD_COOKIE,
                    database_id=DATABASE_ID,
                    book_blacklist=BOOK_BLACKLIST,
                    is_web=True):
    try:
        weread_ = WeRead(weread_cookie)
    except Exception as e:
        raise Exception(f'微信读书登录失败，{e}')
    try:
        notion = NotionClient(notion_token, database_id)
    except Exception as e:
        raise Exception(f'notion 登录失败，{e}')
    # 书籍列表
    try:
        books = weread_.get_notebooklist()
    except Exception as e:
        raise Exception(f'获取书籍列表失败，请检查微信读书 cookies 是否正确 {e.__str__()}')
    all_book = []
    handled_book = []
    ignore_book = []
    err_book = {}
    info(f'书籍目录：{books}')
    if books is not None:
        for book in books:
            try:
                sort = book["sort"]  # 更新时间
                book = book.get("book")
                title = book.get("title")
                info(f' 正在同步：《{title}》, 当前进度 {len(handled_book) + len(ignore_book)}/{len(books)}')
                if is_web:
                    put_text(f' 正在同步：《{title}》, 当前进度 {len(handled_book) + len(ignore_book)}/{len(books)}')
                all_book.append(title)
                if title in book_blacklist:
                    info(f'《{title}》在黑名单中，跳过')
                    ignore_book.append(title)
                    continue
                # 调试用途代码
                # if book.get("title") != '黄金时代':
                #     ignore_book.append(title)
                #     continue
                # print(book['123'])
                # print(book)
                if sort <= notion.get_sort():
                    warning(f'当前图书《{title}》没有更新划线、书评等信息，暂不处理')
                    ignore_book.append(title)
                    continue
                handled_book.append(title)
                cover = book.get("cover", '没有封面')
                bookId = book.get("bookId", '-1')
                author = book.get("author", '没有作者信息')
                info(f'开始处理《{title}》, bookId={bookId}, sort={sort}')
                notion.check(bookId)  # TODO 如果自行在 notion 修改，这里会删除重新插入，规避这个逻辑
                chapter = weread_.get_chapter_info(bookId)
                bookmark_list = weread_.get_bookmark_list(bookId)
                summary, reviews = weread_.get_review_list(bookId)
                bookmark_list.extend(reviews)
                bookmark_list = sorted(bookmark_list, key=lambda x: (
                    x.get("chapterUid", 1),
                    0 if (x.get("range", "") == "" or x.get("range").split("-")[0] == "") else int(
                        x.get("range").split("-")[0])))
                isbn, rating, intro, category = weread_.get_bookinfo(bookId)
                children, grandchild = notion.get_children(
                    chapter, summary, bookmark_list)
                block_id = notion.insert_to_notion(bookName=title,
                                                   bookId=bookId,
                                                   book_str_id=weread_.calculate_book_str_id(bookId),
                                                   cover=cover,
                                                   sort=sort,
                                                   author=author,
                                                   isbn=isbn,
                                                   rating=rating,
                                                   intro=intro,
                                                   category=category)
                results = notion.add_children(block_id, children)
                if (len(grandchild) > 0 and results != None):
                    notion.add_grandchild(grandchild, results)
                debug(f'结束处理《{title}》, bookId={bookId}, sort={sort}')
            except Exception as e:
                exception(f'处理书籍《{title}》失败')
                err_book[title] = [str(e), book]
                continue
        return all_book, handled_book, ignore_book, err_book


if __name__ == '__main__':
    weread_2_notion(is_web=False)
    # weread = WeRead(WEREAD_COOKIE)
    # print(weread.session.cookies.get_dict())
    # res = weread.session.get(
    #     'https://i.weread.qq.com/users/info')
    # weread.session.
    # print(weread.get_notebooklist())
