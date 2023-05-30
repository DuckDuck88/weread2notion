import os
import sys
import time
from datetime import datetime

from logger import info

o_path = os.getcwd()
sys.path.append(o_path)

from notion_client import Client

from settings.settings import NOTION_TOKEN


class NotionClient(object):

    def __init__(self):
        self.client = Client(auth=NOTION_TOKEN)

    def test_api(self):
        res = self.client.search(query="收藏夹").get("results")
        info(res)

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

    def insert_to_notion(self, database_id, bookName, bookId, book_str_id, cover, sort, author, isbn, rating,
                         read_info=None):
        """插入到notion"""
        time.sleep(0.3)
        parent = {
            "database_id": database_id,
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

    def get_sort(self, database_id):
        """获取database中的最新时间"""
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
            database_id=database_id, filter=filter, sorts=sorts, page_size=1)
        if (len(response.get("results")) == 1):
            return response.get("results")[0].get("properties").get("Sort").get("number")
        return 0


if __name__ == '__main__':
    notion = NotionClient()
    notion.test_api()

# try:
#     from dotenv import load_dotenv
# except ModuleNotFoundError:
#     print("Could not load .env because python-dotenv not found.")
# else:
#     load_dotenv()

# # Initialize the client
# notion = Client(auth=NOTION_TOKEN)


# # Search for an item
# print("\nSearching for the word 'People' ")
# results = notion.search(query="People").get("results")
# print(len(results))
# result = results[0]
# print("The result is a", result["object"])
# pprint(result["properties"])

# database_id = result["id"]  # store the database id in a variable for future use

# # Create a new page
# your_name = input("\n\nEnter your name: ")
# gh_uname = input("Enter your github username: ")
# new_page = {
#     "Name": {"title": [{"text": {"content": your_name}}]},
#     "Tags": {"type": "multi_select", "multi_select": [{"name": "python"}]},
#     "GitHub": {
#         "type": "rich_text",
#         "rich_text": [
#             {
#                 "type": "text",
#                 "text": {"content": gh_uname},
#             },
#         ],
#     },
# }
# notion.pages.create(parent={"database_id": database_id}, properties=new_page)
# print("You were added to the People database!")


# # Query a database
# name = input("\n\nEnter the name of the person to search in People: ")
# results = notion.databases.query(
#     **{
#         "database_id": database_id,
#         "filter": {"property": "Name", "text": {"contains": name}},
#     }
# ).get("results")

# no_of_results = len(results)

# if no_of_results == 0:
#     print("No results found.")
#     sys.exit()

# print(f"No of results found: {len(results)}")

# result = results[0]

# print(f"The first result is a {result['object']} with id {result['id']}.")
# print(f"This was created on {result['created_time']}")
