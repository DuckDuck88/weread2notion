const crypto = require('crypto');
// const fetch = require('node-fetch');
const fetch = require('isomorphic-fetch');

class WeRead {
    constructor(weread_cookie) {
        // this.session = fetch;
        this.cookie = this.parse_cookie_string(weread_cookie);
        this.options = {
            method: 'GET',
            headers: {
                'Cookie': 'session=your_session_cookie_value',  // 设置 Cookie
                'Content-Type': 'application/json',  // 设置请求的内容类型
                'Authorization': 'Bearer your_token',  // 设置授权头部信息
            },
        };
    }

    async get_bookmark_list(bookId) {
        const params = {bookId: bookId};
        const response = await fetch(this.WEREAD_BOOKMARKLIST_URL, this.options, {params: params});
        if (response.ok) {
            const updated = response.json().updated;
            return updated.sort((a, b) => {
                const chapterUidA = a.chapterUid || 1;
                const chapterUidB = b.chapterUid || 1;
                const rangeA = parseInt(a.range.split("-")[0]);
                const rangeB = parseInt(b.range.split("-")[0]);
                return chapterUidA - chapterUidB || rangeA - rangeB;
            });
        }
        return null;
    }

    async get_bookinfo(bookId) {
        const params = {bookId: bookId};
        const response = await this.session.get(this.WEREAD_BOOK_INFO, {params: params});
        let isbn = "";
        let newRating = 0;
        if (response.ok) {
            const data = response.json();
            isbn = data.isbn;
            newRating = data.newRating / 1000;
        }
        return [isbn, newRating];
    }

    async get_review_list(bookId) {
        const params = {bookId: bookId, listType: 11, mine: 1, syncKey: 0};
        const response = await this.session.get(this.WEREAD_REVIEW_LIST_URL, {params: params});
        const reviews = response.json().reviews || [];
        const summary = reviews.filter(x => x.review.type === 4);
        const filteredReviews = reviews.filter(x => x.review.type === 1);
        const mappedReviews = filteredReviews.map(x => ({
            ...x.review,
            markText: x.review.content
        }));
        return [summary, mappedReviews];
    }

    async get_read_info(bookId) {
        const params = {bookId: bookId, readingDetail: 1, readingBookIndex: 1, finishedDate: 1};
        const response = await this.session.get(this.WEREAD_READ_INFO_URL, {params: params});
        if (response.ok) {
            return response.json();
        }
        return null;
    }

    _transform_id(book_id) {
        const id_length = book_id.length;

        if (/^\d*$/.test(book_id)) {
            const ary = [];
            for (let i = 0; i < id_length; i += 9) {
                ary.push(parseInt(book_id.substr(i, Math.min(i + 9, id_length)), 10).toString(16));
            }
            return ['3', ary];
        }

        let result = '';
        for (let i = 0; i < id_length; i++) {
            result += book_id.charCodeAt(i).toString(16);
        }
        return ['4', [result]];
    }

    calculate_book_str_id(book_id) {
        const md5_hash = crypto.createHash('md5');
        md5_hash.update(book_id, 'utf-8');
        const digest = md5_hash.digest('hex');
        let result = digest.substr(0, 3);
        const [code, transformed_ids] = this._transform_id(book_id);
        result += code + '2' + digest.substr(-2);

        transformed_ids.forEach((id, i) => {
            const hex_length_str = id.length.toString(16).padStart(2, '0');
            result += hex_length_str + id;

            if (i < transformed_ids.length - 1) {
                result += 'g';
            }
        });

        if (result.length < 20) {
            result += digest.substr(0, 20 - result.length);
        }

        const md5 = crypto.createHash('md5');
        md5.update(result, 'utf-8');
        result += md5.digest('hex').substr(0, 3);
        return result;
    }

    async get_chapter_info(bookId) {
        const body = {
            bookIds: [bookId],
            synckeys: [0],
            teenmode: 0
        };
        const response = await this.session.post(this.WEREAD_CHAPTER_INFO, {json: body});
        if (response.ok && response.json().data.length === 1 && 'updated' in response.json().data[0]) {
            const updated = response.json().data[0].updated;
            return updated.reduce((acc, item) => {
                acc[item.chapterUid] = item;
                return acc;
            }, {});
        }
        return null;
    }

    async get_notebooklist() {
        const response = await fetch(this.WEREAD_NOTEBOOKS_URL, this.options);
        if (response.ok) {
            const data = response.json();
            const books = data.books || [];
            books.sort((a, b) => a.sort - b.sort);
            return books;
        } else {
            console.error(`获取图书失败, ${response.text}`);
        }
        return null;
    }

    parse_cookie_string(cookie_string) {
        const cookies = {};
        cookie_string.split(';').forEach(cookie => {
            const [key, value] = cookie.trim().split('=');
            cookies[key] = value;
        });
        return cookies;
    }
}

module.exports = {
    WeRead
};