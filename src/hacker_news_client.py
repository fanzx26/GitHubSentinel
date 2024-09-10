import os
import requests
from bs4 import BeautifulSoup
import datetime
from logger import LOG  # 导入日志模块

class HackerNewsClient:
    def __init__(self, url='https://news.ycombinator.com/'):
        self.url = url

    def fetch_news(self):
        try:
            # 请求 Hacker News 的 URL
            response = requests.get(self.url, verify=False, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
        except requests.RequestException as e:
            LOG.error(f"获取Hacker News新闻失败: {e}")
            return []

        # 使用 BeautifulSoup 解析 HTML 内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有热点新闻条目
        news_items = soup.find_all('tr', class_='athing')

        news_list = []
        for item in news_items:
            title_tag = item.find('span', class_='titleline')  # 查找包含标题的 span
            if title_tag:
                link_tag = title_tag.find('a')  # 查找 a 标签来获取标题和链接
                if link_tag:
                    title = link_tag.get_text()
                    link = link_tag['href']
                    news_list.append({'title': title, 'link': link})
                else:
                    LOG.warning("获取Hacker News未找到链接")
            else:
                LOG.warning("获取Hacker News未找到标题")
        LOG.info(f"获取并成功解析Hacker News {len(news_list)}条。")
        return news_list

    def display_news(self):
        news_list = self.fetch_news()
        if news_list:
            for news in news_list:
                print(f"标题: {news['title']}\n链接: {news['link']}\n")
        else:
            print("未找到新闻条目。")

    def export_hour_news(self):
        news_list = self.fetch_news()

        # 获取当前的日期和时间
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y_%m_%d_%H")  # 格式化为 年_月_日_小时

        # 设置文件夹路径和文件名
        folder_path = 'hackernews'
        file_name = f"{formatted_time}.md"
        file_path = os.path.join(folder_path, file_name)

        # 如果文件夹不存在，则创建文件夹
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            LOG.info(f"已创建文件夹: {folder_path}")

        # 写入数据到 md 文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Hacker News {formatted_time}\n\n")
                for idx, news in enumerate(news_list, 1):
                    f.write(f"{idx}. {news['title']}\n")
                    f.write(f"Link: {news['link']}\n\n")
            LOG.info(f"新闻成功保存至 {file_path}")
        except Exception as e:
            LOG.error(f"保存新闻到文件失败: {e}")
        return file_path

# 使用示例
if __name__ == '__main__':
    client = HackerNewsClient()
    client.export_hour_news()
