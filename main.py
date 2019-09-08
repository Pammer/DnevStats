import scrapy
import datefinder
import html
import re
from urllib.parse import unquote
from datetime import datetime
from dateutil import parser
import icu 
import locale
from scrapy.crawler import CrawlerProcess
import getDataFromPostPreviews
from argparse import ArgumentParser
from scrapy import signals
from scrapy.exceptions import CloseSpider
import os
import sys

class DnevnikSpider(scrapy.Spider):
    name = "dnevnik"
    #cookies = {'dle_user_id' : '113073', 'dle_password' : '215275d5745d070d0cf9fa4810a1d76c', 'idCookie' : 'c3e648c5582db60d455480bae1267b582292f6b4%26Mikula', 'dn_mobile' : 'false', 'JSESSIONID' : '1gq38auuiw9d0ed2uvilhdhp7' } 
    postsCount = 0
    postPreviews = []
    cookies = {}
    def start_requests(self):
        login = getattr(self, 'login', None)
        urls = [
            'https://dnevniki.ykt.ru/{}'.format(login)
        ]
        for url in urls:
            yield scrapy.Request(url=url , cookies= self.cookies, callback=self.parse)

    def parse(self, response):
        locale.setlocale(locale.LC_ALL, '')
        result_queue = getattr(self, 'result_queue', None)
        if response.status == 404:
            result_queue[0]=404
            self.log('result from parse: {}'.format(result_queue[0]))
            raise CloseSpider('Такого логина нет')
        next_page = response.css('li.next a::attr(href)').get()
        post_previews = response.css('div.post-item')
        self.postsCount += len(post_previews)
        for post_preview in post_previews:
            preview = PostPreview()
            preview['id'] = post_preview.css('div.post-item::attr(id)').get().split('-')[1]
            preview['title'] = unquote(post_preview.css('div.post-item__header a.post-item__title-link::text').get()).strip('\n').strip()
            preview['link'] =unquote(post_preview.css('div.post-item__header a.post-item__title-link::attr(href)').get())
            likesCountTmp = post_preview.css('span.post-item__counter span.ygls-likes-count::text').get()
            preview['likesCount'] = likesCountTmp is not None and likesCountTmp  if likesCountTmp else 0
            commentsCountTmp = post_preview.css('div.post-item__footer  span  a.gray::text').getall()
            #self.log( len(commentsCountTmp))
            if (len(commentsCountTmp) >  1) :
                preview['commentsCount'] =   commentsCountTmp[1].strip('\n').strip()  
            else:
                preview['commentsCount'] = 0
            preview['views'] = post_preview.css('span.post-item__counter span.post-views::text').get()
            date = post_preview.css('div.post-item__info::text').getall()[1]
            matches = datefinder.find_dates(date.strip())
            res = re.search(r'-(.+\d\s)', date)
            if (res and res.group(1).find('сегодня') == -1 and res.group(1).find('вчера') == -1 ) :
                strr = res.group(1)
                #self.log(strr)
                preview['creationDate'] = self.parse_date(strr) #datetime.datetime.strptime(res.group(1).strip(), '%d %B %Y г., %H:%M').date()
            else:
                preview['creationDate'] = '-'
            
            self.postPreviews.append(preview)
            #self.log(preview['creationDate'])

        self.log(next_page)
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, cookies= self.cookies, callback=self.parse)
        else:
            yield {
                'postsCount' : self.postsCount,
                'postPreviews' : self.postPreviews
            }
    def parse1(self, response):
        self.log(response)

    def parse_date(self, s_date, fmt='dd MMMM yyyy г., hh:mm'):
        f = icu.SimpleDateFormat(fmt, icu.Locale('ru'))
        return datetime.fromtimestamp(int(f.parse(s_date)))

class PostPreview(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    likesCount = scrapy.Field()
    commentsCount = scrapy.Field()
    views = scrapy.Field()
    creationDate = scrapy.Field()

def main():
    parser = ArgumentParser(description='Получение 10 самых облайканных, обкоменченных, обсмотренных постов')
    parser.add_argument('--login', help='Логин')
    args = parser.parse_args()
    login = args.login
    if login is None:
        print(u'Input login: ')
        login = input().strip()
    result_queue = [200]
    output_data_file ='data_{}.json'.format(login)
    if os.path.exists(output_data_file):
        os.remove(output_data_file)
    process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': output_data_file,
    'FEED_EXPORT_ENCODING' : 'utf-8',
    'HTTPCACHE_ENABLED' : True,
    'HTTPCACHE_EXPIRATION_SECS' : 0,
    'HTTPCACHE_DIR' : 'httpcache',
    'HTTPCACHE_IGNORE_HTTP_CODES' : [400, 500],
    'HTTPERROR_ALLOWED_CODES'  :[404],
    'AUTOTHROTTLE_ENABLED' : 'True',
    'AUTOTHROTTLE_START_DELAY' : '3',
    'AUTOTHROTTLE_MAX_DELAY' : '60',
    'AUTOTHROTTLE_TARGET_CONCURRENCY' : '3.0'
})
    process.crawl(DnevnikSpider, login = login, result_queue  = result_queue)
    process.start(True)
    print('result from main: {}'.format(result_queue[0]))
    if result_queue[0] != 404 :
        getDataFromPostPreviews.getData(login)
        print(u'Bingo! File : results_{}.xlsx'.format(login))
    else :
        print(u'Ouuups , wrong login, not found dnevnik')
    print(u'Want to close? Tap Enter...')
    input()
    os.remove(output_data_file)
def stop():
    return 'Stoped'


main()
