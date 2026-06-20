import urllib.request
import xml.etree.ElementTree as ET
import trafilatura

# ==================== 请确认你的 GitHub 信息 ====================
GITHUB_USER = "zukuxi"            
GITHUB_REPO = "x3-bbc-news"       # 确保这里和你新建的仓库名一致
# ==============================================================

# BBC World News 官方源
url = "http://feeds.bbci.co.uk/news/world/rss.xml"
req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

try:
    print("正在连接 BBC 获取最新国际新闻...")
    with urllib.request.urlopen(req) as response:
        rss_data = response.read()

    root = ET.fromstring(rss_data)

    # 创建适合墨水屏的骨架
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "BBC World News (x3 Direct)"
    ET.SubElement(channel, "link").text = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"
    ET.SubElement(channel, "description").text = "BBC 全文内嵌版，专为纯粹阅读打造"

    # BBC 是标准 RSS 2.0，直接提取 item
    items = root.findall('.//item')
    print(f"成功获取列表！共 {len(items)} 条新闻。开始提取 BBC 网页正文...")

    for i, item_node in enumerate(items):
        title = item_node.find('title').text
        link = item_node.find('link').text

        print(f"[{i+1}/{len(items)}] 正在抓取: {title[:20]}...")

        # 核心：抓取纯文本
        article_text = ""
        if link:
            try:
                downloaded = trafilatura.fetch_url(link)
                if downloaded:
                    article_text = trafilatura.extract(downloaded)
            except Exception as e:
                print(f"提取失败: {e}")

        if not article_text:
            article_text = "【正文抓取失败。该页面可能是交互式图表、纯视频，或被 BBC 服务器拦截。】"

        full_display_content = f"【原文链接】：{link}\n\n========================================\n\n{article_text}"

        # 写入包含长篇正文的新节点
        new_item = ET.SubElement(channel, "item")
        ET.SubElement(new_item, "title").text = title
        ET.SubElement(new_item, "link").text = link
        ET.SubElement(new_item, "description").text = full_display_content

    # 生成最终文件
    tree = ET.ElementTree(rss)
    tree.write("bbc_world.xml", encoding="utf-8", xml_declaration=True)
    print("✨ 大功告成！BBC 长篇正文已成功注入 XML！")

except Exception as e:
    print(f"运行发生崩溃: {e}")
