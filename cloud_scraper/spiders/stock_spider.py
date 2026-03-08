
import scrapy
import json
import time

class StockSpider(scrapy.Spider):
    name = 'stock_spider'
    # 东方财富实时行情接口 (由 Zyte 云端执行，不限流)
    start_urls = ['https://66.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5000&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:1+t:80&fields=f12,f14,f2,f3,f6,f8']

    def parse(self, response):
        data = json.loads(response.text)
        items = data.get('data', {}).get('diff', [])
        
        for item in items:
            yield {
                '代码': item.get('f12'),
                '名称': item.get('f14'),
                '最新价': item.get('f2'),
                '涨跌幅': item.get('f3'),
                '成交额': item.get('f6'),
                '换手率': item.get('f8'),
                'timestamp': int(time.time())
            }
