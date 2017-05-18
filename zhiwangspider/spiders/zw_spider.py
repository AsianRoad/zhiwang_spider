# coding=utf-8
import urllib
import urllib2
from urlparse import urljoin
from selenium import webdriver
from PIL import Image, ImageGrab
from scrapy import Spider
from scrapy.http import Request, FormRequest

from zhiwangspider.captcha_recognition.recognition_img import distinguish_captcha
from zhiwangspider.items import ZhiwangspiderItem


# 设置网页截图
driver = webdriver.PhantomJS()
driver.set_window_size(1366,768)


# 第二次跳转
# http://kns.cnki.net/kns/brief/brief.aspx?
formdata1=urllib.urlencode({
    't':'1488268898493','S':'1','research':'off','pagename':'ASP.brief_result_aspx','dbPrefix':'CJFQ','dbCatalog':'中国学术期刊网络出版总库',
    'ConfigFile':'CJFQ.xml'
})

# 第三次跳转 结果页面
# http://kns.cnki.net/kns/brief/result.aspx?
formdata2=urllib.urlencode(
    {
        'pagename':'ASP.brief_result_aspx','dbPrefix':'CJFQ','dbCatalog':'中国学术期刊网络出版总库','ConfigFile':'CJFQ.xml',
        'research':'off','recordsperpage':'10','t':'1488184668147','S':'1','queryid':'5','skuakuid':'5',
        'turnpage':'1','keyValue':''
    }
)

# 验证码表单
ccform = {
'rurl':'/kns/brief/brief.aspx?curpage=16&RecordsPerPage=10&QueryID=5&ID=&turnpage=1&tpagemode=L&dbPrefix=CJFQ&Fields=&DisplayMode=listmode&PageName=ASP.brief_result_aspx'
}

class zwspider(Spider):
    name = 'zw'
    allowed_domains = []
    start_urls = ['http://kns.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ']

    def __init__(self, query='', time=''):
        # 第一次链接
        # http://kns.cnki.net/kns/request/SearchHandler.ashx?
        self.formdata = urllib.urlencode(
            {'magazine_value1': '数学学报中文版', 'year_from': 2014, 'year_to': 2016, 'NaviCode': '*', 'ua': '1.21',
             'PageName': 'ASP.brief_result_aspx',
             'DbPrefix': 'CJFQ', 'DbCatalog': '中国学术期刊网络出版总库', 'ConfigFile': 'CJFQ.xml', 'db_opt': 'CJFQ',
             'db_value': '中国学术期刊网络出版总库', 'magazine_special1': '=', 'year_type': 'echar', 'his': '0',
             '__': 'Mon Feb 27 2017 16:37:42 GMT+0800 (中国标准时间)', 'action': ''
             })

    # 处理response，并返回处理的数以及跟进的url,但是在response 没有指定函数的情况下的默认处理方法
    def parse(self, response):
        return Request("http://epub.cnki.net//kns/request/SearchHandler.ashx?"+self.formdata,
                       callback=self.Search1
                       )

    def Search1(self,response):
        filename = 'search1.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://epub.cnki.net/kns/brief/brief.aspx?"+formdata1,
                       callback=self.Search2
                       )
    def Search2(self,response):
        filename = 'search1.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://epub.cnki.net/kns/brief/brief.aspx?"+formdata2,
                       callback=self.Search3)


    def Search3(self,response):
        filename = 'result.html'
        print response.url
        with open(filename, 'wb') as f:
            f.write(response.body)
        if 'CheckCodeImg' in response.body:
            print 'need check code!'
            # 验证码图片截取
            driver.get(response.url)
            captcha = driver.find_element_by_id('CheckCodeImg')
            location = captcha.location
            size = captcha.size
            driver.save_screenshot('./cap.png')
            img = Image.open('./cap.png')
            left = location['x']
            top = location['y']
            right = left + size['width']
            bottom = top + size['height']
            img = img.crop((left,top,right,bottom))
            img.show()
            img.save('./cap.png')
            checkcode = distinguish_captcha(img)
            print checkcode
            ccform['vericode'] = checkcode
            formdata3 = urllib.urlencode(ccform)
            yield Request("http://kns.cnki.net/kns/brief/vericode.aspx?"+formdata3,
                           callback=self.Search3)

        next_pages = response.xpath('//a[@id="Page_next"]/@href').extract_first()
        for tr in response.css('table.GridTableContent').xpath('tr[position()>1]'):
            paper = ZhiwangspiderItem()
            paper['title'] = [tr.xpath('td[2]/a//text()').extract()[0].split('\'')[1]]
            paper['author'] = tr.xpath('td[3]/a/text()').extract()
            paper['journal'] = tr.xpath('td[4]/a/text()').extract()

            print  paper
            yield  paper

        next_url = urljoin('http://epub.cnki.net/kns/brief/brief.aspx',next_pages)
        if next_url:
            yield  Request(next_url,callback=self.Search3)