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
# driver = webdriver.PhantomJS()
# driver.set_window_size(1366,768)


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
        'research':'off','recordsperpage':'50','t':'1488184668147','S':'1','queryid':'5','skuakuid':'5',
        'turnpage':'1','keyValue':''
    }
)



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
    }

    cookies = {
        'Ecp_ClientId': '2170516135301619463',
        'cnkiUserKey': '28cb43cb-113e-f055-4c21-efcadff6d792',
        'RsPerPage': '50',
        'ASP.NET_SessionId': 'yzv1ypazx4cbshsicvx1u01f',
        'Ecp_IpLoginFail': '17052258.211.96.227',
        'SID_kns': '123105',
        'SID_klogin': '125143',
        'SID_kinfo': '125105',
        'SID_kredi': '125142',
        'SID_krsnew' : '125131',
    }

    def __init__(self, query='', time=''):
        # 第一次链接
        # http://kns.cnki.net/kns/request/SearchHandler.ashx?
        self.formdata = urllib.urlencode(
            {'magazine_value1': '计算机学报', 'year_from': '2010', 'year_to': '2016', 'NaviCode': '*', 'ua': '1.21',
             'PageName': 'ASP.brief_result_aspx',
             'DbPrefix': 'CJFQ', 'DbCatalog': '中国学术期刊网络出版总库', 'ConfigFile': 'CJFQ.xml', 'db_opt': 'CJFQ',
             'db_value': '中国学术期刊网络出版总库', 'magazine_special1': '%', 'year_type': 'echar', 'his': '0',
             '__': 'Mon Feb 27 2017 16:37:42 GMT+0800 (中国标准时间)', 'action': ''
             })
        self.formdata_jingque=urllib.urlencode({'hidMagezineCode':'JSJX','year_from':'2010','year_to':'2016','NaviCode':'*','ua':'1.21','PageName':'ASP.brief_result_aspx',
                           'DbPrefix':'CJFQ','DbCatalog':'中国学术期刊网络出版总库','ConfigFile':'CJFQ.xml','db_opt':'CJFQ',
                           'db_value':'中国学术期刊网络出版总库','magazine_special1':'=','year_type':'echar','his':'0',
                             '__':'Mon Feb 27 2017 16:37:42 GMT+0800 (中国标准时间)', 'action':''
                                              })

    def parse(self, response):
        return Request("http://kns.cnki.net//kns/request/SearchHandler.ashx?"+self.formdata,
                       headers=self.headers,
                       cookies=self.cookies,
                       callback=self.Search1
                       )

    def Search1(self,response):
        filename = 'search1.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://kns.cnki.net/kns/brief/brief.aspx?"+formdata1,
                       headers=self.headers,
                       cookies=self.cookies,
                       callback=self.Search2
                       )
    def Search2(self,response):
        filename = 'search2.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        return Request("http://kns.cnki.net/kns/brief/brief.aspx?"+formdata2,
                       headers=self.headers,
                       cookies=self.cookies,
                       callback=self.Search3)

    def Search3(self,response):
        filename = 'result.html'
        print response.url
        with open(filename, 'wb') as f:
            f.write(response.body)
        if 'CheckCodeImg' in response.body:
            print 'need check code!'
            img = requests.get('http://kns.cnki.net/kns/checkcode.aspx?t=%2+Math.random()',stream=True,headers=self.headers ,
                               cookies = self.cookies)
            rurl = response.url.split('=')[1].split('&vericode')[0]
            # 验证码图片截取 无效
            # driver.get(response.url)
            # print response.url
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
            with open('1.gif', 'wb') as f:
                f.write(img.content)
            img = Image.open('1.gif')
            checkcode = distinguish_captcha(img)
            print checkcode
            veriform = 'rurl='+rurl+'&vericode='+checkcode
            print veriform
            yield Request(
                "http://kns.cnki.net/kns/brief/vericode.aspx?" + veriform,
                headers=self.headers,
                cookies=self.cookies,
                callback=self.Search3,
                dont_filter = True
            )
        else:
            next_pages = response.xpath('//a[@id="Page_next"]/@href').extract_first()
            for tr in response.css('table.GridTableContent').xpath('tr[position()>1]'):
                paper = ZhiwangspiderItem()
                paper['title'] = tr.xpath('td[2]/a//text()').extract()[0].split('\'')[0]
                paper['author'] = tr.xpath('td[3]/a/text()').extract()
                paper['journal'] = tr.xpath('td[4]/a//text()').extract()

                yield  paper

            next_url = urljoin('http://kns.cnki.net/kns/brief/brief.aspx',next_pages)
            if next_url:
                yield  Request(next_url,
                               headers=self.headers,
                               cookies=self.cookies,
                               callback=self.Search3)



