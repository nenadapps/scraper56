from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
import re
'''
from fake_useragent import UserAgent
import os
import sqlite3
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks

controller = Controller.from_port(port=9051)
controller.authenticate()'''
req = requests.Session()

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)
    
#UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')

base_url = 'https://www.noernbergstamps.com'

hdr = {
'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0', #UA.random,
'Host': 'www.noernbergstamps.com',
'Accept-Language': 'en-US,en;q=0.5',
'Upgrade-Insecure-Requests': '1',
'Cache-Control': 'max-age=0'
}

def get_html(url):
    
    html_content = ''
    try:
        page = req.get(url, headers=hdr)
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('#productName')[0].get_text().strip()
        title = title.replace('\n', ' ').strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      
    
    try:
        raw_text = ''
        raw_text_html = str(html.select('#productDescription')[0])
        if '<table' not in raw_text_html:
            raw_text = raw_text_html.replace('<br />', ' ').replace('<br>', ' ')
            raw_text = re.sub(r'<.*?>','',raw_text).strip()
            raw_text = re.sub(' +', ' ', raw_text)
            raw_text = raw_text.replace('\n', ' ').strip()
            raw_text = raw_text.replace(u'\xa0', u' ').strip()
            stamp['country']=''
            stamp['year']=''
            stamp['scott_num']=''
            stamp['sg']=''
            stamp['mi']=''
            stamp['stampworld_num']=''
            stamp['face_value']=''
            stamp['considerations']=''
            stamp['cat_price']=''
        else:
            country = ''  
            year = '' 
            scott_num = '' 
            sg = '' 
            mi = ''
            stampworld_num = ''
            face_value = ''
            considerations = ''
            cat_price = ''

            for info_item in html.select('#productDescription td'):
                info_heading = info_item.get_text().strip()
                if info_item.find_next():
                    info_value = info_item.find_next().get_text().strip()
                    if info_heading == 'Country:':
                        country = info_value 
                    elif info_heading == 'Year of Issue:':
                        year = info_value 
                    elif info_heading == 'Description:':
                        raw_text = info_value.replace('\n', ' ').strip()    
                    elif info_heading == 'Scott Catalogue #:':
                        scott_num = info_value 
                    elif info_heading == 'SG Catalogue #:':
                        sg = info_value   
                    elif info_heading == 'Michel Catalogue #:':
                        mi = info_value 
                    elif info_heading == 'StampWorld Cat. #:':
                        stampworld_num = info_value                   
                    elif info_heading == 'Denomination:':
                        face_value = info_value  
                    elif info_heading == 'Faults/Considerations:':
                        considerations = info_value    
                    elif 'Scott Cat. Value:' in info_heading:
                        cat_price = info_value   

            stamp['country'] = country     
            stamp['year'] = year     
            stamp['scott_num'] = scott_num   
            stamp['sg'] = sg     
            stamp['mi'] = mi     
            stamp['stampworld_num'] = stampworld_num     
            stamp['face_value'] = face_value     
            stamp['considerations'] = considerations     
            stamp['cat_price'] = cat_price  
        
        stamp['raw_text'] = raw_text.replace('"',"'")
    except:
        stamp['raw_text'] = None
        
    condition = ''     
    tags = ''
    type_value = ''
    
    attr_items = html.select('.optionName')
    for attr_item in attr_items:
        attr_heading = attr_item.get_text().strip()
        if attr_item.find_next():
             attr_value = attr_item.find_next().get_text().strip()
             if attr_heading == 'Condition':
                 condition = attr_value
             elif attr_heading == 'Format':
                 type_value = attr_value 
             elif attr_heading == 'Type:':
                 tag_items_cont = str(attr_item.find_next())
                 tag_items = tag_items_cont.split('<br>')
                 for tag_item in tag_items:
                     if tags:
                         tags = tags + ', '
                     tags = tags + tag_item   
                     
    stamp['condition'] = condition
    stamp['tags'] = tags
    stamp['type_value'] = type_value
    
    number = ''
    try:
        for item2 in html.select('#productDetailsList li'):
            item2_text = item2.get_text().strip()
            if 'Units in Stock' in item2_text:
                number = item2_text.replace('Units in Stock', '').strip()
    except:
        pass

    stamp['number'] = number  
    
    post_date = ''
    try:
        post_date = html.select('#productDateAdded')[0].get_text().strip()
        post_date = post_date.replace('This product was added to our catalog on ', '').strip()
        stamp['post_date'] = post_date
    except:
        pass
    
    stamp['post_date'] = post_date
    
    try:
        base_category = html.select('#navBreadCrumb a')[1].get_text().strip()
        stamp['base_category'] = base_category
    except:
        stamp['base_category'] = None     
  
    try:
        category = html.select('#navBreadCrumb a')[2].get_text().strip()
        stamp['category'] = category
    except:
        stamp['category'] = None
        
    try:
        subcategory = html.select('#navBreadCrumb a')[3].get_text().strip()
        stamp['subcategory'] = subcategory
    except:
        stamp['subcategory'] = None        
        
    try:
        if html.select('#productGeneral .productSpecialPrice'):
            price = html.select('#productGeneral .productSpecialPrice')[0].get_text().strip()
        else:
            price = html.select('#productPrices')[0].get_text().strip()
        price = price.replace('$', '').replace(',', '').strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
        
    stamp['currency'] = 'USD'
    
    # image_urls should be a list
    images = []                    
    try:
        
        img_src = html.select('#productMainImage img')[0].get('src')
        img = base_url + '/' + img_src
        if img not in images:
             images.append(img)
             
        for img_item in html.select('#productAdditionalImages img'):
            img = base_url + '/' + img_item.get('src')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('.itemTitle a'):
            item_link_temp = item.get('href')
            item_link_parts = item_link_temp.split('&zenid')
            item_link = item_link_parts[0]
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_items = html.select('.forward a')
        for next_item in next_items:
            next_text = next_item.get('title').strip()
            next_href = next_item.get('href').replace('&amp;', '&')
            if 'Next Page' in next_text:
                next_url = next_href
    except:
        pass 
    
    shuffle(items)
    
    return items, next_url

def get_main_categories():
    
    items = {}

    try:
        html = get_html(base_url)
    except:
        return items

    try:
        for item in html.select('#categories a.category-top'):
            item_link = item.get('href')
            item_text = item.get_text().strip()
            item_text = item_text.replace('->', '').strip()
            if item_link not in items: 
                items[item_text] = item_link
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

def get_page_item_details(page_url):
	count = 0
	start_page_url = page_url
	while(page_url):
		page_items, page_url = get_page_items(page_url)
		if len(page_items):
			for page_item in page_items:
				'''count += 1
				if count > randint(40, 256):
					print('Sleeping...')
					sleep(randint(600, 4000))
					hdr['User-Agent'] = UA.random
					renew_tor()
					connectTor()
					count = 0
				else:
					pass'''
				stamp = get_details(page_item)
				'''if stamp['price']==None or stamp['price']=='':
				    sleep(randint(500,700))
				    continue
				next_step = query_for_previous(stamp)
				if next_step == 'continue':
					print('Only updating price')
					continue
				elif next_step == 'pass':
					print('Inserting the item')
					pass
				else:
					break
				db_update_image_download(stamp)'''
		else:
			subcategories = get_subcategories(start_page_url)
			for subcategory in subcategories:
				get_page_item_details(subcategory)
            
def get_subcategories(url):
   
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        subcategory_items = html.select('.categoryListBoxContents a')
        for subcategory_item in subcategory_items:
            item = subcategory_item.get('href')
            if item not in items: 
                items.append(item)
    except: 
        pass
    
    shuffle(items)
    
    return items            
            
def get_categories(url):
   
    items = {}

    try:
        html = get_html(url)
    except:
        return items

    try:
        category_items = html.select('.subcategory a.category-products')
        if not len(category_items):
            category_items = html.select('.subcategory a.category-subs')
        for item in category_items:
            item_link = item.get('href')
            item_text = item.get_text().strip()
            item_text = item_text.replace('->', '').strip()
            item_text = item_text.replace('|_', '').strip()
            if item_link not in items: 
                items[item_text] = item_link
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items
'''
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    print (file_name)
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM noernbergstamps WHERE {cn} == "{un}" AND {cn2} == "{un2}"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency'],
    stamp['number']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency,number) VALUES(?,?,?,?,?,?)""", price_update)
        try:
            conn1.commit()
            conn1.close()
        except:
            conn1.commit()
            conn1.close()
        print (" ")
        sleep(randint(10,45))
        next_step = 'continue'
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency,number) VALUES(?,?,?,?,?,?)""", price_update)
        try:
            conn2.commit()
            conn2.close()
        except:
            conn2.commit()
            conn2.close()
        next_step = 'pass'
    print("Price Updated")
    return(next_step)

def db_update_image_download(stamp): 
    directory = "/Volumes/Stamps/stamps/noernbergstamps/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    names = file_names(stamp)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    image_paths = [directory + names[i] for i in range(len(names))]
    for item in range(0,len(names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=120, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=120, stream=True)
        if imgRequest1.status_code==200:
            with open(names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    database_update =[]
    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['country'],
        stamp['year'],
        stamp['scott_num'],
        stamp['sg'],
        stamp['mi'],
        stamp['stampworld_num'],
        stamp['face_value'],
        stamp['considerations'],
        stamp['cat_price'],
        stamp['post_date'],
        stamp['base_category'],
        stamp['category'],
        stamp['subcategory'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO noernbergstamps ('url','raw_text', 'title','country','year','scott_num','sg','mi','stampworld_num',
    'face_value','considerations','cat_price','post_date','base_category','category','subcategory','scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", database_update)
    try:
        conn.commit()
        conn.close()
    except:
        conn.commit()
        conn.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(60,140)) 

connectTor()'''

main_categories = get_main_categories()

for key in main_categories:
    print(key + ': ' + main_categories[key])   

selection = input('Choose category: ')

selected_main_category = main_categories[selection]

categories = get_categories(selected_main_category)  
if len(categories):
    for category in categories:
        if selection == "Worldwide Stamps":
            print(category)
            choice = input("Do you want to scrape this?")
            if choice.lower() == 'y':
                pass
            else:
                continue
            
        get_page_item_details(categories[category])    
else:        
    get_page_item_details(selected_main_category) 
print('Scrape Complete!')
