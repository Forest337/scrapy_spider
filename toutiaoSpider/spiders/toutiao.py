# -*- coding: utf-8 -*-
import scrapy
import json
import re
import html
import time
from toutiaoSpider.items import ToutiaospiderItem
from scrapy.http import Request


class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['www.toutiao.com']
    max_behot_time = 0
    start_urls = ['https://www.toutiao.com/api/pc/feed/?category=news_game&utm_source=toutiao&widen=1&max_behot_time=0']

    def parse(self, response):

        # 获取返回数据
        rs = json.loads(response.text)
        if rs.get('message') == 'success':
            # 数据返回成功获取下一个标识
            next = rs.get('next')
            self.max_behot_time = next.get('max_behot_time')

            # 获取当前页json数据，并循环获取对应详情数据。
            data = rs.get('data')
            # for循环遍历数据
            for dz in data:
                item_id = dz.get('item_id')
                ##print(item_id)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.3",
                    "Accept": "text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8",
                    "Referer": "https://www.toutiao.com/a" + item_id + "/"}
                if len(item_id):
                    # 循环取得完文章详情数据
                    yield Request('https://www.toutiao.com/a' + item_id, callback=self.detial_parse, headers=headers)
            # 程序暂停3秒钟,获取下一页内容
            time.sleep(3)
            yield Request(
                'https://www.toutiao.com/api/pc/feed/?category=news_game&utm_source=toutiao&widen=1&max_behot_time=' + str(
                    self.max_behot_time) + '&max_behot_time_tmp=' + str(self.max_behot_time) + '&tadrequire=true',
                callback=self.parse)

    def detial_parse(self, response):

        resp_data = response.text
        item = ToutiaospiderItem()
        title = re.findall(r"title:(.+)", resp_data)
        items = []
        if len(title):
            content = re.findall(r"content:(.+)", resp_data)
            content = html.unescape(content[0])
            title = title[0].replace('\'', '').replace(',', '')
            item['title'] = str(title)
            item['content'] = content.replace('\'', '')
            items.append(item)
        return items
