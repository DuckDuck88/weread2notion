// const fetch = require('node-fetch');
const fetch = require('isomorphic-fetch');
const {WeRead} = require('./weread.js');
const {NotionClient} = require('./notion');

const WEREAD_COOKIE = 'uin=o1307317886; skey=@Q8MrVr0ER; RK=Dn35RmM4ef; ptcz=bc8fbc0bf0c2ff9ffa6fc1fccc5209246c7dc595183dfadfcbec558cb8560c2d; pgv_info=ssid=s5596440080; pgv_pvid=1180932580; midas_openid=89C1944462BF4A87C4C951878B816A12; midas_openkey=5BBE8339ECB7A44878A632E5D7ABE8AE; wr_fp=2533447432; wr_gid=262277338; pac_uid=1_1307317886; wr_vid=23683664; wr_pf=0; wr_rt=web%40AVEURyUiB24N6OmM1Q1_AL; wr_localvid=fb3325d071696250fb37ae2; wr_name=%E8%AF%B6%E9%B8%AD; wr_gender=1; wr_skey=zOSz_VvI; wr_avatar=https%3A%2F%2Fthirdwx.qlogo.cn%2Fmmopen%2Fvi_32%2FXpfWjDr8uAYiagxaSibFmnMh2LUJXTQrjJ8z2ve6X8J3w2CI79YSvQwic1icyHUoHVgoccckuoLxlt1cQOD87tZLfQ%2F132';
const DATABASE_ID = 'd92bb4b8434745baa2061caf67d6ef7a';
const BOOK_BLACKLIST = ['从红月开始',]; // Array of book titles to ignore
const NOTION_TOKEN = 'secret_kZMZkH95SLspBpZb0OPD49pTZ2JuGL2z9DeyoHpe3DG';

async function weread2notion() {
    const weread = new WeRead(WEREAD_COOKIE);
    const notion = new NotionClient(NOTION_TOKEN, DATABASE_ID);

    // Get the book list
    const books = await weread.get_notebooklist();

    if (books !== null) {
        for (const book of books) {
            const sort = book.sort; // Update time
            const {book: bookData} = book;
            const title = bookData.title;

            if (BOOK_BLACKLIST.includes(title)) {
                console.log(`《${title}》 is in the blacklist, skipping`);
                continue;
            }

            if (sort <= notion.getSort()) {
                console.log(`Current book 《${title}》 does not have updated underlines, reviews, etc., skipping`);
                continue;
            }

            const cover = bookData.cover;
            const bookId = bookData.bookId;
            const author = bookData.author;

            console.log(`Processing 《${title}》, bookId=${bookId}, sort=${sort}`);

            await notion.check(bookId); // TODO: If modified manually in Notion, this will delete and reinsert, avoid this logic

            const chapter = await weread.getChapterInfo(bookId);
            const bookmarkList = await weread.getBookmarkList(bookId);
            const {summary, reviews} = await weread.getReviewList(bookId);

            bookmarkList.push(...reviews);
            bookmarkList.sort((a, b) => {
                const aChapterUid = a.chapterUid || 1;
                const bChapterUid = b.chapterUid || 1;
                const aRange = a.range || '';
                const bRange = b.range || '';
                const aStart = aRange !== '' ? parseInt(aRange.split('-')[0]) : 0;
                const bStart = bRange !== '' ? parseInt(bRange.split('-')[0]) : 0;
                return aChapterUid - bChapterUid || aStart - bStart;
            });

            const {isbn, rating} = await weread.getBookInfo(bookId);
            const {children, grandchild} = await notion.getChildren(chapter, summary, bookmarkList);

            const blockId = await notion.insertToNotion({
                bookName: title,
                bookId,
                bookStrId: weread.calculateBookStrId(bookId),
                cover,
                sort,
                author,
                isbn,
                rating
            });

            const results = await notion.addChildren(blockId, children);

            if (grandchild.length > 0 && results !== null) {
                await notion.addGrandchild(grandchild, results);
            }

            console.log(`Finished processing 《${title}》, bookId=${bookId}, sort=${sort}`);
        }
    }
}

weread2notion().catch((error) => {
    console.log('An error occurred:', error);
});
