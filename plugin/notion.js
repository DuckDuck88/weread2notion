const {Client} = require('@notionhq/client');

class NotionClient {
    constructor(token, databaseId) {
        this.client = new Client({auth: token});
        this.databaseId = databaseId;
    }

    async testApi() {
        const response = await this.client.search({
            query: '收藏夹'
        });
        console.log(response.results);
    }

    async check(bookId) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        console.log(`开始检查${bookId}是否已经插入`);
        const filter = {
            property: 'BookId',
            rich_text: {
                equals: bookId
            }
        };
        const response = await this.client.databases.query({
            database_id: this.databaseId,
            filter: filter
        });
        for (const result of response.results) {
            await new Promise((resolve) => setTimeout(resolve, 300));
            await this.client.blocks.delete({
                block_id: result.id
            });
        }
    }

    getTableOfContents() {
        return {
            type: 'table_of_contents',
            table_of_contents: {
                color: 'default'
            }
        };
    }

    getHeading(level, content) {
        let heading;
        if (level === 1) {
            heading = 'heading_1';
        } else if (level === 2) {
            heading = 'heading_2';
        } else {
            heading = 'heading_3';
        }
        return {
            type: heading,
            [heading]: {
                rich_text: [{
                    type: 'text',
                    text: {
                        content: content
                    }
                }],
                color: 'default',
                is_toggleable: false
            }
        };
    }

    getQuote(content) {
        return {
            type: 'quote',
            quote: {
                rich_text: [{
                    type: 'text',
                    text: {
                        content: content
                    }
                }],
                color: 'default'
            }
        };
    }

    getCallout(content, style, colorStyle, reviewId) {
        let emoji = '🌟';
        if (style === 0) {
            emoji = '💡';
        } else if (style === 1) {
            emoji = '⭐';
        }
        if (reviewId !== null) {
            emoji = '✍️';
        }
        let color = 'default';
        if (colorStyle === 1) {
            color = 'red';
        } else if (colorStyle === 2) {
            color = 'purple';
        } else if (colorStyle === 3) {
            color = 'blue';
        } else if (colorStyle === 4) {
            color = 'green';
        } else if (colorStyle === 5) {
            color = 'yellow';
        }
        return {
            type: 'callout',
            callout: {
                rich_text: [{
                    type: 'text',
                    text: {
                        content: content
                    }
                }],
                icon: {
                    emoji: emoji
                },
                color: color
            }
        };
    }

    getChildren(chapter, summary, bookmarkList) {
        const children = [];
        const grandchild = {};
        if (chapter !== null) {
            children.push(this.getTableOfContents());
            const d = {};
            for (const data of bookmarkList) {
                const chapterUid = data.chapterUid || 1;
                if (!(chapterUid in d)) {
                    d[chapterUid] = [];
                }
                d[chapterUid].push(data);
            }
            for (const [key, value] of Object.entries(d)) {
                if (key in chapter) {
                    children.push(this.getHeading(
                        chapter[key].level,
                        chapter[key].title
                    ));
                }
                for (const i of value) {
                    const callout = this.getCallout(
                        i.markText,
                        i.style,
                        i.colorStyle,
                        i.reviewId
                    );
                    children.push(callout);
                    if (i.abstract !== null && i.abstract !== "") {
                        const quote = this.getQuote(i.abstract);
                        grandchild[children.length - 1] = quote;
                    }
                }
            }
        } else {
            for (const data of bookmarkList) {
                children.push(this.getCallout(
                    data.markText,
                    data.style,
                    data.colorStyle,
                    data.reviewId
                ));
            }
        }
        if (summary !== null && summary.length > 0) {
            children.push(this.getHeading(1, "点评"));
            for (const i of summary) {
                children.push(this.getCallout(
                    i.review.content,
                    i.style,
                    i.colorStyle,
                    i.review.reviewId
                ));
            }
        }
        return [children, grandchild];
    }

    async addChildren(id, children) {
        const results = [];
        for (let i = 0; i < Math.ceil(children.length / 100); i++) {
            await new Promise((resolve) => setTimeout(resolve, 300));
            const response = await this.client.blocks.children.append({
                block_id: id,
                children: children.slice(i * 100, (i + 1) * 100)
            });
            results.push(...response.results);
        }
        return results.length === children.length ? results : null;
    }

    async addGrandchild(grandchild, results) {
        for (const [key, value] of Object.entries(grandchild)) {
            await new Promise((resolve) => setTimeout(resolve, 300));
            const id = results[key].id;
            await this.client.blocks.children.append({
                block_id: id,
                children: [value]
            });
        }
    }

    async insertToNotion(
        bookName,
        bookId,
        bookStrId,
        cover,
        sort,
        author,
        isbn,
        rating,
        readInfo = null
    ) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        const parent = {
            database_id: this.databaseId,
            type: 'database_id'
        };
        const properties = {
            BookName: {
                title: [{type: 'text', text: {content: bookName}}]
            },
            BookId: {
                rich_text: [{type: 'text', text: {content: bookId}}]
            },
            ISBN: {
                rich_text: [{type: 'text', text: {content: isbn}}]
            },
            URL: {
                url: `https://weread.qq.com/web/reader/${bookStrId}`
            },
            Author: {
                rich_text: [{type: 'text', text: {content: author}}]
            },
            Sort: {
                number: sort
            },
            Rating: {
                number: rating
            },
            Cover: {
                files: [{
                    type: 'external',
                    name: 'Cover',
                    external: {url: cover}
                }]
            }
        };
        if (readInfo !== null) {
            const markedStatus = readInfo.markedStatus || 0;
            const readingTime = readInfo.readingTime || 0;
            let formatTime = '';
            const hour = Math.floor(readingTime / 3600);
            if (hour > 0) {
                formatTime += `${hour}时`;
            }
            const minutes = Math.floor((readingTime % 3600) / 60);
            if (minutes > 0) {
                formatTime += `${minutes}分`;
            }
            properties.Status = {
                select: {
                    name: markedStatus === 4 ? '读完' : '在读'
                }
            };
            properties.ReadingTime = {
                rich_text: [
                    {
                        type: 'text',
                        text: {content: formatTime}
                    }
                ]
            };
            if ('finishedDate' in readInfo) {
                properties.Date = {
                    date: {
                        start: moment.unix(readInfo.finishedDate).format('YYYY-MM-DD HH:mm:ss'),
                        time_zone: 'Asia/Shanghai'
                    }
                };
            }
        }

        const icon = {
            type: 'external',
            external: {
                url: cover
            }
        };
        const response = await this.client.pages.create({
            parent,
            icon,
            properties
        });
        const id = response.id;
        return id;
    }

    async getSort() {
        const filter = {
            property: 'Sort',
            number: {
                is_not_empty: true
            }
        };
        const sorts = [
            {
                property: 'Sort',
                direction: 'descending'
            }
        ];
        const response = await this.client.databases.query({
            database_id: this.databaseId,
            filter,
            sorts,
            page_size: 1
        });
        if (response.results.length === 1) {
            return response.results[0].properties.Sort.number;
        }
        return 0;
    }
}

module.exports = {
    NotionClient
};