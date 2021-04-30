import corp_code_fn
import requests
from bs4 import BeautifulSoup
import json
import datetime
import pandas as pd
import time
import os

df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

def get_stock_code(api_key,corp_code):
    url = 'https://opendart.fss.or.kr/api/company.json?crtfc_key='+api_key+'&corp_code='+str(corp_code)
    html = requests.get(url).text
    result = str(BeautifulSoup(html, 'html.parser'))
    json_object = json.loads(result)
    stock_code=str(json_object['stock_code'])
    # if stock_code==None:
    #     df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0]

    return stock_code
def get_market_cap_and_price(stock_code):

    url = 'https://finance.naver.com/item/main.nhn?code=' + stock_code

    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    today = soup.select_one('#chart_area > div.rate_info > div')

    price = today.select_one('.blind')
    price = str(price.get_text())
    price = int(price.replace(',', ''))

    trading_volume = str(soup.findAll("span",{"class":"blind"})[18]).replace('<span class="blind">','').replace('</span>','')

    try:
        market_cap = int(
            str(soup.find('em', id='_market_sum')).replace('\t', '').replace('\n', '').replace('</em>', '').replace(
                '<em id="_market_sum">', '').replace(',', '')) * 100000000
    except:
        market_cap = int(
            str(soup.find('em', id='_market_sum')).replace('\t', '').replace('\n', '').replace('</em>', '').replace(
                '<em id="_market_sum">', '').replace(',', '').replace("조", '')) * 100000000

    return price, market_cap, trading_volume
def get_current_income_eps_total_cap(corp_code):
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=" + api_key + "&corp_code=" + corp_code + "&bsns_year=2020&reprt_code=11011&fs_div=CFS"
    html = requests.get(url).text
    result = str(BeautifulSoup(html, 'html.parser'))
    json_object = json.loads(result)
    if json_object['status'] == '013':
        url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=" + api_key + "&corp_code=" + corp_code + "&bsns_year=2020&reprt_code=11011&fs_div=OFS"
        html = requests.get(url).text
        result = str(BeautifulSoup(html, 'html.parser'))
        json_object = json.loads(result)

    count_curent_income=0
    count_eps = 0
    count_total_cap=0

    for i in range(len(json_object['list'])):
        if count_curent_income==0 and (json_object['list'][i]['account_nm'] == '당기순이익' or json_object['list'][i]['account_nm'] == '당기순이익(손실)' or json_object['list'][i]['account_nm'] == '계속영업당기순이익(손실)'):
            curnet_income = str(json_object['list'][i]['thstrm_amount'])
            if curnet_income.find('-')==0:
                curnet_income = curnet_income.replace('-','')
                curnet_income = -int(curnet_income)
            else:
                curnet_income = int(curnet_income)
            count_curent_income=1
        if count_eps==0 and (json_object['list'][i]['account_nm'] == '기본주당이익'
                              or json_object['list'][i]['account_nm'] == '기본주당이익(손실)'
                              or json_object['list'][i]['account_nm'] =='보통주 기본주당이익(손실)'
                              or json_object['list'][i]['account_nm'] =='계속영업기본주당이익(손실)'
                              or json_object['list'][i]['account_nm'] =='기본주당순이익'
                              or json_object['list'][i]['account_nm'] == '기본주당순이익(손실)'
                              or json_object['list'][i]['account_nm'] == '기본주당순손익'):
            eps = str(json_object['list'][i]['thstrm_amount'])
            if eps.find('-')==0:
                eps = eps.replace('-','')
                eps = -float(eps)
            else:
                eps = float(eps)
            count_eps=1
        if count_total_cap==0 and json_object['list'][i]['account_nm'] == '자본총계':
            total_cap = int(str(json_object['list'][i]['thstrm_amount']).replace(',', ''))

            count_total_cap=1
        # if json_object['list'][i]['account_nm']=='영업이익(손실)':
        #     print(json_object['list'][i]['account_nm'],':',json_object['list'][i]['thstrm_amount'])
        # if json_object['list'][i]['account_nm']=='감가상각비':
        #     depre_cost = json_object['list'][i]['thstrm_amount']
        #     print(json_object['list'][i]['account_nm'],':',depre_cost)
        # if json_object['list'][i]['account_nm'] == '부채총계':
        #     total_debt=json_object['list'][i]['thstrm_amount']
        #     print(json_object['list'][i]['account_nm'], ':',total_debt)
        # if json_object['list'][i]['account_nm'] == '현금및현금성자산':
        #     print(json_object['list'][i]['account_nm'], ':', json_object['list'][i]['thstrm_amount'])
        # if str(json_object['list'][i]['account_nm']).find("무형")>=0:
        #     print(json_object['list'][i]['account_nm'],':',json_object['list'][i]['thstrm_amount'])
        # if json_object['list'][i]['account_nm']== '이익잉여금(결손금)':
        #     retained_earn = int(json_object['list'][i]['thstrm_amount'])
    return curnet_income, eps, total_cap

with open(os.path.join(os.path.abspath(''), 'api_key.txt')) as f:
    api_key=str(f.read())


#api_key='3ce42ee675ce702d5b1467313be878324d5e6dfc'#DART에서 신청한 자신의 API 주소를 입력하세요

token = 0
print("[CADA], 종료는 q 입력")
while token == 0:
    try:
        corp_name = input("회사명을 입력하세요(예 : 삼성전자): ")

        if corp_name == 'q':
            token = 1
            print("프로그램을 종료합니다")
            break

        corp_code, stock_code = corp_code_fn.find(corp_name)
        is_in = df['회사명'] == corp_name
        if stock_code is '':
            stock_code = get_stock_code(api_key, corp_code)
            #stock_code = str(df[is_in]['종목코드'].item()).zfill(6)

        price, market_cap, trading_volume = get_market_cap_and_price(stock_code)
        curnet_income, eps, total_cap = get_current_income_eps_total_cap(corp_code)

        PER = (price/eps).__round__(2)
        PBR = (market_cap/total_cap).__round__(2)

        print(datetime.datetime.today().date(),'['+corp_name+']','분석 결과 입니다')
        print('=========================================')
        print('종목코드|',stock_code)
        print('시가총액|',int(market_cap/100000000),'억원')
        print('거래량  |', trading_volume)
        print('현재가  |',price,'원')
        print('EPS    |',eps,'원')
        print("PER    |",PER)
        print("PBR    |",PBR)
        print("ROE(%) |",((PBR/PER)*100).__round__(2),'%')
        print('=========================================')
    except:
        print("ERROR!")


