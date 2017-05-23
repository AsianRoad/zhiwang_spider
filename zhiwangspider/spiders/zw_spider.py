# coding=utf-8
import urllib
from urlparse import urljoin

import requests
from PIL import Image
from selenium import webdriver
from scrapy import Spider
from scrapy.http import Request, FormRequest, request

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

formdata4 = urllib.urlencode(
    {
        'curpage':'16',
        'RecordsPerPage':'10',
        'QueryID':'3',
        'ID':'',
        'turnpage':'1',
        'tpagemode':'L',
        'dbPrefix':'CJFQ',
        'Fields':'',
        'DisplayMode':'listmode',
        'PageName':'ASP.brief_result_aspx'
    }
)

# 验证码表单
#
formdata3 = {
    'rurl':'',
    'vericode':''
}



class zwspider(Spider):
    name = 'zw'
    allowed_domains = []
    start_urls = ['http://kns.cnki.net/kns/brief/result.aspx?dbprefix=CJFQ']

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'kns.cnki.net',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Upgrade-Insecure-Requests':'1',
        # 'Cookie':{
        #           }
    }

    cookies = {
        'Ecp_ClientId': '2170516135301619463',
        'cnkiUserKey': '28cb43cb-113e-f055-4c21-efcadff6d792',
        'RsPerPage': '10',
        'ASP.NET_SessionId': 'hsivsyikm0cqut1j2z0wenqg',
        'Ecp_IpLoginFail': '17052258.211.96.227',
        'SID_kns': '123109',
        'SID_klogin': '125143',
        'SID_kinfo': '125104',
        'SID_kredi': '125143',
        'SID_krsnew' : '125131',
    }

    def __init__(self, query='', time=''):
        # 第一次链接
        # http://kns.cnki.net/kns/request/SearchHandler.ashx?
        self.formdata = urllib.urlencode(
            {'magazine_value1': '数学学报中文版', 'year_from': '2014', 'year_to': '2016', 'NaviCode': '*', 'ua': '1.21',
             'PageName': 'ASP.brief_result_aspx',
             'DbPrefix': 'CJFQ', 'DbCatalog': '中国学术期刊网络出版总库', 'ConfigFile': 'CJFQ.xml', 'db_opt': 'CJFQ',
             'db_value': '中国学术期刊网络出版总库', 'magazine_special1': '=', 'year_type': 'echar', 'his': '0',
             '__': 'Mon Feb 27 2017 16:37:42 GMT+0800 (中国标准时间)', 'action': ''
             })

    # 处理response，并返回处理的数以及跟进的url,但是在response 没有指定函数的情况下的默认处理方法
    def parse(self, response):
        return Request("http://epub.cnki.net//kns/request/SearchHandler.ashx?"+self.formdata,
                       headers=self.headers,
                       # meta={'cookiejar':1},
                       cookies=self.cookies,
                       callback=self.Search1
                       )

    def Search1(self,response):
        filename = 'search1.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://epub.cnki.net/kns/brief/brief.aspx?"+formdata1,
                       headers=self.headers,
                       # meta={'cookiejar':response.meta['cookiejar']},
                       cookies=self.cookies,
                       callback=self.Search2
                       )
    def Search2(self,response):
        filename = 'search2.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://epub.cnki.net/kns/brief/brief.aspx?"+formdata2,
                       headers=self.headers,
                       cookies=self.cookies,
                       # cookies='Ecp_ClientId=2170516135301619463; cnkiUserKey=28cb43cb-113e-f055-4c21-efcadff6d792; RsPerPage=10; ASP.NET_SessionId=hsivsyikm0cqut1j2z0wenqg; Ecp_IpLoginFail=17052258.211.96.227; SID_kns=123109; SID_klogin=125143; SID_kinfo=125104; SID_kredis=125143',
                       # meta={'cookiejar':response.meta['cookiejar']},
                       callback=self.Search3)


    def Search3(self,response):
        filename = 'result.html'
        print response.url
        with open(filename, 'wb') as f:
            f.write(response.body)
        if 'CheckCodeImg' in response.body:
            print 'need check code!'
            img = requests.get('http://kns.cnki.net/kns/checkcode.aspx?t=%27+Math.random()',stream=True,headers=self.headers ,cookies = self.cookies)
            # 验证码图片截取
            # driver.get(response.url)
            # print response.url
            # rurl = 'http://kns.cnki.net'+ response.url.split('?')[1]
            rurl='%2fkns%2fbrief%2fbrief.aspx%3fcurpage%3d16%26RecordsPerPage%3d10%26QueryID%3d0%26ID%3d%26turnpage%3d1%26tpagemode%3dL%26dbPrefix%3dCJFQ%26Fields%3d%26DisplayMode%3dlistmode%26PageName%3dASP.brief_result_aspx'
            # captcha = driver.find_element_by_id('CheckCodeImg')
            # location = captcha.location
            # size = captcha.size
            # driver.save_screenshot('./cap.png')
            # img = Image.open('./cap.png')
            # left = location['x']
            # top = location['y']
            # right = left + size['width']
            # bottom = top + size['height']
            # img = img.crop((left,top,right,bottom))
            # img.show()
            # img.save('./cap.png')
            #
            # captcha = driver.find_element_by_id('CheckCodeImg')
            # location = captcha.location
            # size = captcha.size
            # driver.save_screenshot('./cap2.png')
            # img = Image.open('./cap2.png')
            # left = location['x']
            # top = location['y']
            # right = left + size['width']
            # bottom = top + size['height']
            # img = img.crop((left,top,right,bottom))
            # img.show()
            # img.save('./cap2.png')
            #
            # driver.get(response.url)
            # captcha = driver.find_element_by_id('CheckCodeImg')
            # location = captcha.location
            # size = captcha.size
            # driver.save_screenshot('./cap3.png')
            # img = Image.open('./cap3.png')
            # left = location['x']
            # top = location['y']
            # right = left + size['width']
            # bottom = top + size['height']
            # img = img.crop((left,top,right,bottom))
            # img.show()
            # img.save('./cap3.png')
            with open('1.gif', 'wb') as f:
                f.write(img.content)
            img = Image.open('1.gif')
            img.show()
            checkcode = distinguish_captcha(img)
            print checkcode
            formdata3['vericode'] = checkcode
            formdata3['rurl'] = rurl
            #self.headers['Referer'] = "http://kns.cnki.net/kns/brief/vericode.aspx?" + rurl
            self.headers['Referer'] = 'http://kns.cnki.net/kns/brief/vericode.aspx?rurl=%2fkns%2fbrief%2fbrief.aspx%3fcurpage%3d59%26RecordsPerPage%3d10%26QueryID%3d1%26ID%3d%26turnpage%3d1%26tpagemode%3dL%26dbPrefix%3dCJFQ%26Fields%3d%26DisplayMode%3dlistmode%26PageName%3dASP.brief_result_aspx&skey=CheckMaxTurnPageCount'
            veriform = urllib.urlencode(formdata3)
            print veriform
            yield Request(
                "http://kns.cnki.net/kns/brief/vericode.aspx?" + veriform,
                headers=self.headers,
                cookies=self.cookies,
                # meta={'cookiejar':response.meta['cookiejar']},
                callback=self.Search3)
        else:
            next_pages = response.xpath('//a[@id="Page_next"]/@href').extract_first()
            for tr in response.css('table.GridTableContent').xpath('tr[position()>1]'):
                paper = ZhiwangspiderItem()
                # paper['title'] = [tr.xpath('td[2]/a//text()').extract()[0].split('\'')[1]]
                paper['author'] = tr.xpath('td[3]/a/text()').extract()
                paper['journal'] = tr.xpath('td[4]/a/text()').extract()

                # print  paper
                yield  paper

            next_url = urljoin('http://epub.cnki.net/kns/brief/brief.aspx',next_pages)
            if next_url:
                yield  Request(next_url,
                               headers=self.headers,
                               cookies=self.cookies,
                               # meta={'cookiejar': response.meta['cookiejar']},
                               callback=self.Search3)

    # def Search4(self,response):
    #     filename = 'veri.html'
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)
    #     return Request("http://kns.cnki.net/kns/brief/brief.aspx?"+formdata4,
    #                    headers=self.headers,
    #                    meta={'cookiejar':response.meta['cookiejar']},
    #                    callback=self.Search3)

