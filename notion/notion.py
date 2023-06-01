import os
import sys
import time
from datetime import datetime

from retrying import retry

from logger import info, debug

o_path = os.getcwd()
sys.path.append(o_path)

from notion_client import Client


class NotionClient(object):

    def __init__(self, token, database_id):
        self.client = Client(auth=token)
        self.database_id = database_id

    def test_api(self):
        res = self.client.search(query="收藏夹").get("results")
        info(res)

    def check(self, bookId):
        """检查是否已经插入过 如果已经插入了就删除"""
        time.sleep(0.3)
        debug(f"开始检查{bookId}是否已经插入")
        filter = {
            "property": "BookId",
            "rich_text": {
                "equals": bookId
            }
        }
        response = self.client.databases.query(database_id=self.database_id, filter=filter)
        for result in response["results"]:
            time.sleep(0.3)
            self.client.blocks.delete(block_id=result["id"])

    def get_table_of_contents(self):
        """获取目录"""
        return {
            "type": "table_of_contents",
            "table_of_contents": {
                "color": "default"
            }
        }

    def get_heading(self, level, content):
        if level == 1:
            heading = "heading_1"
        elif level == 2:
            heading = "heading_2"
        else:
            heading = "heading_3"
        return {
            "type": heading,
            heading: {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": content,
                    }
                }],
                "color": "default",
                "is_toggleable": False
            }
        }

    def get_quote(self, content):
        return {
            "type": "quote",
            "quote": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": content
                    },
                }],
                "color": "default"
            }
        }

    def get_callout(self, content, style, colorStyle, reviewId):
        # 根据不同的划线样式设置不同的emoji 直线type=0 背景颜色是1 波浪线是2
        emoji = "🌟"
        if style == 0:
            emoji = "💡"
        elif style == 1:
            emoji = "⭐"
        # 如果reviewId不是空说明是笔记
        if reviewId != None:
            emoji = "✍️"
        color = "default"
        # 根据划线颜色设置文字的颜色
        if colorStyle == 1:
            color = "red"
        elif colorStyle == 2:
            color = "purple"
        elif colorStyle == 3:
            color = "blue"
        elif colorStyle == 4:
            color = "green"
        elif colorStyle == 5:
            color = "yellow"
        return {
            "type": "callout",
            "callout": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": content,
                    }
                }],
                "icon": {
                    "emoji": emoji
                },
                "color": color
            }
        }

    def get_children(self, chapter, summary, bookmark_list):
        children = []
        grandchild = {}
        if chapter != None:
            # 添加目录
            children.append(self.get_table_of_contents())
            d = {}
            for data in bookmark_list:
                chapterUid = data.get("chapterUid", 1)
                if (chapterUid not in d):
                    d[chapterUid] = []
                d[chapterUid].append(data)
            for key, value in d.items():
                if key in chapter:
                    # 添加章节
                    children.append(self.get_heading(
                        chapter.get(key).get("level"), chapter.get(key).get("title")))
                for i in value:
                    callout = self.get_callout(
                        i.get("markText"), data.get("style"), i.get("colorStyle"), i.get("reviewId"))
                    children.append(callout)
                    if i.get("abstract") != None and i.get("abstract") != "":
                        quote = self.get_quote(i.get("abstract"))
                        grandchild[len(children) - 1] = quote

        else:
            # 如果没有章节信息
            for data in bookmark_list:
                children.append(self.get_callout(data.get("markText"),
                                                 data.get("style"), data.get("colorStyle"), data.get("reviewId")))
        if summary != None and len(summary) > 0:
            children.append(self.get_heading(1, "点评"))
            for i in summary:
                children.append(self.get_callout(i.get("review").get("content"), i.get(
                    "style"), i.get("colorStyle"), i.get("review").get("reviewId")))
        return children, grandchild

    def add_children(self, id, children):
        results = []
        for i in range(0, len(children) // 100 + 1):
            time.sleep(0.3)
            response = self.client.blocks.children.append(
                block_id=id, children=children[i * 100:(i + 1) * 100])
            results.extend(response.get("results"))
        return results if len(results) == len(children) else None

    def add_grandchild(self, grandchild, results):
        for key, value in grandchild.items():
            time.sleep(0.3)
            id = results[key].get("id")
            self.client.blocks.children.append(block_id=id, children=[value])

    def insert_to_notion(self, bookName, bookId, book_str_id, cover, sort, author, isbn, rating, intro, category,
                         read_info=None):
        """插入到notion"""
        time.sleep(0.3)
        parent = {
            "database_id": self.database_id,
            "type": "database_id"
        }
        properties = {
            "BookName": {"title": [{"type": "text", "text": {"content": bookName}}]},
            "BookId": {"rich_text": [{"type": "text", "text": {"content": bookId}}]},
            "ISBN": {"rich_text": [{"type": "text", "text": {"content": isbn}}]},
            "URL": {"url": f"https://weread.qq.com/web/reader/{book_str_id}"},
            "Author": {"rich_text": [{"type": "text", "text": {"content": author}}]},
            "Sort": {"number": sort},
            "Rating": {"number": rating},
            "Cover": {"files": [{"type": "external", "name": "Cover", "external": {"url": cover}}]},
            "intro": {"rich_text": [{"type": "text", "text": {"content": intro}}]},
            "category": {"select": {"name": category}}
        }
        if read_info != None:
            markedStatus = read_info.get("markedStatus", 0)
            readingTime = read_info.get("readingTime", 0)
            format_time = ""
            hour = readingTime // 3600
            if hour > 0:
                format_time += f"{hour}时"
            minutes = readingTime % 3600 // 60
            if minutes > 0:
                format_time += f"{minutes}分"
            properties["Status"] = {"select": {
                "name": "读完" if markedStatus == 4 else "在读"}}
            properties["ReadingTime"] = {"rich_text": [
                {"type": "text", "text": {"content": format_time}}]}
            if "finishedDate" in read_info:
                properties["Date"] = {"date": {"start": datetime.utcfromtimestamp(read_info.get(
                    "finishedDate")).strftime("%Y-%m-%d %H:%M:%S"), "time_zone": "Asia/Shanghai"}}

        icon = {
            "type": "external",
            "external": {
                "url": cover
            }
        }
        # notion api 限制100个block
        response = self.client.pages.create(
            parent=parent, icon=icon, properties=properties)
        id = response["id"]
        return id

    @retry(stop_max_attempt_number=3, wait_fixed=1000)
    def get_sort(self):
        """获取database中的上次编辑时间"""
        filter = {
            "property": "Sort",
            "number": {
                "is_not_empty": True
            }
        }
        sorts = [
            {
                "property": "Sort",
                "direction": "descending",
            }
        ]
        response = self.client.databases.query(
            database_id=self.database_id, filter=filter, sorts=sorts, page_size=1)
        if (len(response.get("results")) == 1):
            return response.get("results")[0].get("properties").get("Sort").get("number")
        return 0
