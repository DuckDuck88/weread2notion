# wereadtonotion

微信读书笔记、划线等信息同步到notion数据库
> 效果如下：
> ![同步效果](https://markdown-mac-work-1306720256.cos.ap-guangzhou.myqcloud.com/png/AzRZUp.png)

## 使用方法

### 1. 本地脚本运行

1. 配置 settings/settings.py 文件中的信息
   > 1. 获取 **Notion token**
   > - 打开[此页面](https://www.notion.so/my-integrations)并登录
   > - 点击New integration 输入 name 提交.(如果已有，则点击 view integration)
   > - 点击show，然后copy
   > 2. 从微信读书中获取 cookie
   > - 在浏览器中打开 weread.qq.com 并登录
   > - 打开开发者工具(按 F12)，点击 network(网络)，刷新页面, 点击第一个请求，复制 cookie 的值。
   > 3. 准备 Noiton Database ID
   > - 复制[此页面](https://www.notion.so/yayya/a9b3a8dfcc0543559005a263103fc81c)到你的
       Notion 中，点击右上角的分享按钮，将页面分享为公开页面
   >- 点击页面右上角三个点，在 connections 中找到选择你的 connections。第一步中创建的 integration 的 name
   >- 通过 URL 找到你的 Database ID 的值。
      >  > 例如：页面 https://www.notion.so/yayya/d92bb4b8434745baa2061caf67d6ef7a?v=b4a5bfb89e8e44868a473179ee60x851 的
      ID 为d92bb4b8434745baa2061caf67d6ef7a
2. 打开文件 weread_2_notion.py
3. 运行 `python weread_2_notion.py`

### 2. 网页端部署运行

#### docker 部署(推荐)
执行脚本: `bash deploy.sh`

#### 直接部署
`python3 install -r requirement.txt`
`python3 app.py`

## PS
- 借鉴了大佬的[项目](https://github.com/malinkang/weread_to_notion)，优化了代码结构、增加了web 端。
- 后续增加功能
   - [ ] 考虑支持自定义 Noiton 数据库结构
   - [ ] 单独导出功能。
   - [ ] 支持 Notion 增量读写

- 配合 NoitonNext 构建 Blog [效果](https://yaya.run/article/1c51da0f-757a-47e5-8296-cc37798b8211)非常好

## 免责申明
本工具仅作技术研究之用，请勿用于商业或违法用途，由于使用该工具导致的侵权或其它问题，该本工具不承担任何责任！
