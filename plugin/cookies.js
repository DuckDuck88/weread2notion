chrome.cookies.getAll({url: "http://www.example.com"}, function (cookies) {
    // 处理获取到的 Cookie
    console.log(cookies);
});
