# coding:utf-8    ctrl+/  注释
import urllib2
import time
import bs4
from bs4 import BeautifulSoup
import sys
import pymongo
import requests

def geocode(address):
    parameters = {'address': address, 'key': '8ac4f59c23c73f503f350494ff9310d3','city':'上海'}
    base = 'http://restapi.amap.com/v3/geocode/geo'
    try:
        response = requests.get(base, parameters,timeout=1)
    except:
        return {}
    print response.elapsed.microseconds
    answer = response.json()
    return answer


reload(sys)
sys.setdefaultencoding("utf-8")

connection = pymongo.MongoClient()
tdb = connection.program
post_info = tdb.house


# 链家网d
def find_data(tmp_url, tmp_district, lists):
    count = 0
    # 每个区的最大显示页数为100页
    for page_Num in range(1, 100):
        f_url = tmp_url + tmp_district + "/d" + str(page_Num)
        print f_url
        # print f_url
        f_page = urllib2.urlopen(f_url)
        f_soup = BeautifulSoup(f_page, "html.parser")

        page_soup = f_soup.find(class_="m-list")
        # print page_soup
        ul_soup = page_soup.find('ul')
        # print ul_soup
        li_list = ul_soup.findAll('li')[0:]
        # print page_Num
        for tr in li_list:
            info = tr.findAll(class_="info-row")[0:]
            row1 = info[0].find(class_="info-col row1-text").text

            row1 = row1.strip()
            row1 = row1.replace(' ', '')
            # print row1
            cut_1 = row1.index('|')
            # 几室几厅
            house_type = row1[0:cut_1]
            #print house_type
            cut_2 = row1[cut_1 + 1:].index('平')
            # 房屋大小
            house_size = float(row1[cut_1 + 1:cut_1 + cut_2 + 1])
            #print house_size
            try:
                cut_3 = row1.index('/')
            except ValueError:
                continue
            cut_4 = row1.index('层')
            # 建筑总层高
            building_height = float(row1[cut_3 + 1:cut_4])
            #print building_height
            cut_5 = row1.index('区')
            # 房屋层高
            house_height = row1[cut_5 - 1:cut_5]
            #print house_height

            row2 = info[1].find(class_="info-col row2-text")
            # 均价
            average_price = info[1].find(class_="info-col price-item minor").text.strip()
            print average_price
            # 位置
            location = row2.findAll('a')[0:]

            try:
                year_1 = row2.text.index('年建')
                year = row2.text[year_1 - 4:year_1]
            except ValueError:
                continue

            print year
            # 小区
            housing_estate = location[0].text
            #print housing_estate
            # 区县
            house_district = location[1].text
            #print house_district
            count = count + 1
            # print count
            #
            #
            #整理出room和parlour数量
            room_1=house_type.index('室')
            room_number=int(house_type[0:room_1])
            parlour_1=house_type.index('厅')
            parlour_number=int(house_type[room_1+1:parlour_1])

            #判断房子的具体高度
            if(house_height=='中'):
                house_height_inlist=building_height*0.5
            elif(house_height=='高'):
                house_height_inlist = building_height * 0.88
            elif(house_height == '低'):
                house_height_inlist = building_height * 0.23

            #整理出具体房价
            price_1=average_price.index('价')
            price_2=average_price.index('元')
            average_price_inlist=float(average_price[price_1+1:price_2])

            #计算地址经纬度
            address = house_district+housing_estate
            print address

            house_first_location=geocode(address)

            if "geocodes" not in house_first_location.keys():
                print "no geocodes"
                continue
            house_first_location=house_first_location["geocodes"]

            #print house_first_location
            if(house_first_location==[]):
                continue

            house_location=house_first_location[0]['location'].encode('utf-8')
            print house_location
            house_location_1=house_location.index(',')
            house_location_longtitude=float(house_location[0:house_location_1])
            print house_location_longtitude
            house_location_latitude=float(house_location[house_location_1+1:])
            print house_location_latitude
            #house_location_latitude,house_location_longtitude,
            list_use = [room_number,parlour_number, house_size, building_height, house_height_inlist,float(year),house_location_longtitude,house_location_latitude,house_district,address,
                        average_price_inlist]

            #print list_use
            lists.extend([list_use])

            print "{\"户型\":\"%s\", \"大小\":\"%s\",\"楼高\":\"%s\",\"层高\":\"%s\",\"小区名\":\"%s\",\"市区\":\"%s\",\"均价\":\"%s\"}" % (
                house_type, house_size, building_height, house_height, housing_estate, house_district, average_price)
            data = {"room_number": room_number, "parlour_number": parlour_number,"house_size":house_size,"building_height": building_height,"house_height_inlist": house_height_inlist,"year": float(year),"house_location_longtitude": house_location_longtitude,"house_location_latitude":house_location_latitude,"house_district":house_district,"address":address,"average_price_inlist": average_price_inlist}
            post_info.save(data)
            # print "end"
            # print "all_end"


def use(district):
    lists = []
    for i in district:
        find_data('http://sh.lianjia.com/ershoufang/', i, lists)
    return lists

b=["jinshan"]
a = ["pudongxinqu", "minhang", "baoshan", "xuhui", "putuo", "yangpu", "changning", "songjiang", "jiading", "huangpu",
     "jingan", "zhabei", "hongkou", "qingpu", "fengxian", "jinshan", "chongming"]

dataset = use(a)







