
BOT_NAME = 'cloud_scraper'
SPIDER_MODULES = ['cloud_scraper.spiders']
NEWSPIDER_MODULE = 'cloud_scraper.spiders'

# 遵守 robots.txt 规则
ROBOTSTXT_OBEY = False

# Zyte 云端爬虫优化配置
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
RETRY_TIMES = 5
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 16
