from logger import info, debug, warning
from notion.notion import NotionClient
from settings.settings import WEREAD_COOKIE, DATABASE_ID, BOOK_BLACKLIST
from weread.weread import WeRead
from settings.settings import NOTION_TOKEN


def weread_2_notion():
    weread = WeRead(WEREAD_COOKIE)
    notion = NotionClient(NOTION_TOKEN, DATABASE_ID)
    # 书籍列表
    books = weread.get_notebooklist()
    if books is not None:
        for book in books:
            sort = book["sort"]  # 更新时间
            book = book.get("book")
            title = book.get("title")
            if book.get("title") != '黄金时代':
                continue
            if title in BOOK_BLACKLIST:
                debug(f'《{title}》在黑名单中，跳过')
                continue
            # if sort <= notion.get_sort():
            #     warning(f'当前图书《{title}》没有更新划线、书评等信息，暂不处理')
            #     continue
            cover = book.get("cover")
            bookId = book.get("bookId")
            author = book.get("author")
            info(f'开始处理《{title}》, bookId={bookId}, sort={sort}')
            notion.check(bookId)  # TODO 如果自行在 notion 修改，这里会删除重新插入，规避这个逻辑
            chapter = weread.get_chapter_info(bookId)
            bookmark_list = weread.get_bookmark_list(bookId)
            summary, reviews = weread.get_review_list(bookId)
            bookmark_list.extend(reviews)
            bookmark_list = sorted(bookmark_list, key=lambda x: (
                x.get("chapterUid", 1), 0 if (x.get("range", "") == "" or x.get("range").split("-")[0] == "") else int(
                    x.get("range").split("-")[0])))
            isbn, rating, intro, category = weread.get_bookinfo(bookId)
            children, grandchild = notion.get_children(
                chapter, summary, bookmark_list)
            block_id = notion.insert_to_notion(bookName=title,
                                               bookId=bookId,
                                               book_str_id=weread.calculate_book_str_id(bookId),
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


if __name__ == '__main__':
    weread_2_notion()
