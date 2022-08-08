import os.path
from tokenize import cookie_re
import requests
from collections import defaultdict, namedtuple


requests.packages.urllib3.disable_warnings()
Book = namedtuple("Book", ["bookId", "title", "author", "cover"])


headers = """
Host: i.weread.qq.com
Connection: keep-alive
cookie: ptui_loginuin=1307317886; RK=ln3xBmMwZf; ptcz=a4011d7d71456e0c24d2f12237745f9c1a4569af063b701a05863cd858f13cfa; uin=o1307317886; skey=@cdW4bgKIq; wr_gid=260437236; wr_vid=23683664; wr_pf=0; wr_rt=web@bDzWNVf6cBn7Li9NhUN_WL; wr_localvid=fb3325d071696250fb37ae2; wr_name=诶鸭; wr_avatar=https://thirdwx.qlogo.cn/mmopen/vi_32/cc0hNnM5FAIianMn14icicKYiauvw2JOGriaDWUfqJHskQDOpwOZzVHka4bfKnUQ1aPiap6Kh0UkFeFsFZlf5TOicRx5g/132; wr_gender=1; wr_theme=dark; wr_skey=4XK0BKjB
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
""".encode("utf-8").decode("latin1")
headers = dict(x.split(": ", 1) for x in headers.splitlines() if x)


def get_bookmarklist(bookId):
    """获取某本书的笔记返回md文本"""
    url = "https://i.weread.qq.com/book/bookmarklist"
    params = dict(bookId=bookId)
    r = requests.get(url, params=params, headers=headers, verify=False)

    if r.ok:
        data = r.json()
    else:
        raise Exception(r.text)
    chapters = {c["chapterUid"]: c["title"] for c in data["chapters"]}
    contents = defaultdict(list)

    for item in sorted(data["updated"], key=lambda x: x["chapterUid"]):
        chapter = item["chapterUid"]
        text = item["markText"]
        create_time = item["createTime"]
        start = int(item["range"].split("-")[0])
        contents[chapter].append((start, text))

    chapters_map = {title: level for level,
                    title in get_chapters(int(bookId))}
    res = ""
    for c in sorted(chapters.keys()):
        title = chapters[c]
        res += "#" * chapters_map[title] + " " + title + "\n"
        for start, text in sorted(contents[c], key=lambda e: e[0]):
            res += "> " + text.strip() + "\n\n"
        res += "\n"

    return res


def get_chapters(bookId):
    """获取书的目录"""
    url = "https://i.weread.qq.com/book/chapterInfos"
    data = '{"bookIds":["%d"],"synckeys":[0]}' % bookId

    r = requests.post(url, data=data, headers=headers, verify=False)

    if r.ok:
        data = r.json()
        # clipboard.copy(json.dumps(data, indent=4, sort_keys=True))
    else:
        raise Exception(r.text)

    chapters = []
    for item in data["data"][0]["updated"]:
        if "anchors" in item:
            chapters.append((item.get("level", 1), item["title"]))
            for ac in item["anchors"]:
                chapters.append((ac["level"], ac["title"]))

        elif "level" in item:
            chapters.append((item.get("level", 1), item["title"]))

        else:
            chapters.append((1, item["title"]))

    return chapters




res = get_bookmarklist(40055543)
print(type(res))
with open('res_md.md', 'w') as f:
    f.write(res)
