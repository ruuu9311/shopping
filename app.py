from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote, unquote
import random
import re

# ==========================================
# 🔥 Selenium 相關套件
# ==========================================
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# 🔥 設定：這裡控制每個平台最多抓幾筆 (設為 30)
SEARCH_LIMIT = 30 

# ==========================================

def get_headers(referer="https://www.google.com/"):
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': referer,
    }

def clean_price(price_str):
    if not price_str: return 0
    try:
        if '-' in str(price_str):
            price_str = price_str.split('-')[0]
        clean = ''.join(filter(str.isdigit, str(price_str)))
        return int(clean)
    except:
        return 0

# --- 🔴 PChome 爬蟲 (自動翻頁版) ---
def scrape_pchome(keyword):
    print(">>> 正在爬取 PChome...")
    results = []
    page = 1 # 從第一頁開始
    
    try:
        # 使用 while 迴圈：只要抓到的數量還沒滿 30 筆，就繼續抓下一頁
        while len(results) < SEARCH_LIMIT:
            url = f"https://ecshweb.pchome.com.tw/search/v3.3/all/results?q={quote(keyword)}&page={page}&sort=sale/dc"
            r = requests.get(url, headers=get_headers(), timeout=10)
            
            if r.status_code != 200: break

            data = r.json()
            if 'prods' not in data or not data['prods']:
                break # 如果沒資料了就停止

            for item in data['prods']:
                # 🔥 再次檢查：如果已經滿 30 筆，就馬上停止
                if len(results) >= SEARCH_LIMIT: break
                
                pic = item.get('picS')
                results.append({
                    'platform': 'PChome',
                    'name': item.get('name'),
                    'price': float(item.get('price', 0)),
                    'link': f"https://24h.pchome.com.tw/prod/{item.get('Id')}",
                    'img': f"https://cs-a.ecimg.tw{pic}" if pic else "",
                    'sales': '24h到貨',
                    'rating': 4.5
                })
            
            page += 1 # 準備抓下一頁
            
        print(f"✅ PChome 成功: 抓到 {len(results)} 筆")
        return results
    except Exception as e:
        print(f"❌ PChome 錯誤: {e}")
        return []

# --- 🩷 MOMO 爬蟲 (Selenium 全能版) ---
def scrape_momo(keyword):
    print(">>> 正在爬取 MOMO (Selenium 全能版)...")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})

        url = f"https://www.momoshop.com.tw/search/{quote(keyword)}?viewport=desktop&_isFuzzy=0&searchType=1&cateLevel=0"
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(2)
        except: pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = []

        products = soup.select('li.listAreaLi')
        if not products: products = soup.select('.goodsItemLi')
        if not products: products = soup.select('.goods-mobile-panel__item-content')

        if not products:
            print("🔄 MOMO 初次抓取失敗，嘗試重新整理...")
            driver.refresh()
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            products = soup.select('li.listAreaLi') or soup.select('.goodsItemLi') or soup.select('.goods-mobile-panel__item-content')

        for p in products:
            # 🔥 MOMO 煞車機制
            if len(results) >= SEARCH_LIMIT: break

            try:
                name, price, link, img_src = "未知", 0, "#", ""
                
                if 'listAreaLi' in str(p.get('class', [])):
                    name_tag = p.select_one('.prdName') or p.select_one('h3')
                    price_tag = p.select_one('.price') or p.select_one('.money')
                    link_tag = p.select_one('a.goods-img-url') or p.select_one('a')
                    img_tag = p.select_one('img.goods-img') or p.select_one('img')
                elif 'goods-mobile-panel' in str(p.get('class', [])):
                    name_tag = p.select_one('.content-info__goods-name') or p.select_one('h3')
                    price_tag = p.select_one('.price-group__current-value') or p.select_one('.price')
                    link_tag = p.select_one('a')
                    img_tag = p.select_one('img')
                else:
                    name_tag = p.select_one('.prdName') or p.select_one('h3')
                    price_tag = p.select_one('.price') or p.select_one('.money')
                    link_tag = p.select_one('a')
                    img_tag = p.select_one('img')

                if name_tag and price_tag:
                    name = name_tag.text.strip()
                    price = clean_price(price_tag.text)
                    if price == 0: continue

                    if link_tag and link_tag.has_attr('href'):
                        link = link_tag['href']
                        if not link.startswith('http'): link = "https://www.momoshop.com.tw" + link
                    
                    if img_tag:
                        img_src = img_tag.get('src')
                        if not img_src or 'blank' in img_src or 'loading' in img_src: 
                            img_src = img_tag.get('data-original') or img_tag.get('data-src')

                    results.append({'platform': 'MOMO', 'name': name, 'price': price, 'link': link, 'img': img_src if img_src else "", 'sales': '熱銷', 'rating': 4.0})
            except: continue
            
        print(f"✅ MOMO 成功: 抓到 {len(results)} 筆")
        return results
    except Exception as e:
        print(f"❌ MOMO 錯誤: {e}")
        return []
    finally:
        if driver: driver.quit()

# --- 📚 博客來 爬蟲 (Regex 原始圖還原版) ---
def scrape_books(keyword):
    print(">>> 正在爬取 博客來 (圖片強制還原版)...")
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})

        url = f"https://search.books.com.tw/search/query/key/{quote(keyword)}/cat/all"
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".table-td, .item")))
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
        except: pass

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = []
        
        candidates = soup.select('.table-td')
        if not candidates: candidates = soup.select('.item')
        if not candidates:
             box_divs = soup.select('div.box')
             candidates = [div.parent for div in box_divs]

        for tag in candidates:
            # 🔥 博客來 煞車機制
            if len(results) >= SEARCH_LIMIT: break

            try:
                name_tag = tag.select_one('h4 a') or tag.select_one('h3 a') or tag.select_one('a[title]')
                
                # 價格處理
                price = 0
                price_row = tag.select_one('ul.price') or tag.select_one('.price')
                if price_row:
                    price_text = price_row.get_text()
                    matches = re.findall(r'(\d+(?:,\d+)*)\s*元', price_text)
                    if matches: price = clean_price(matches[-1])
                    else:
                        all_nums = re.findall(r'\d+', price_text)
                        valid = [int(n) for n in all_nums if int(n) > 10]
                        if valid: price = valid[-1]
                if price == 0:
                    pt = tag.select_one('ul.price li b') or tag.select_one('.price strong')
                    if pt: price = clean_price(pt.text)

                img_tag = tag.select_one('div.box img') or tag.select_one('img')

                if name_tag and price > 0:
                    name = name_tag.get('title') or name_tag.text.strip()
                    link = name_tag.get('href')
                    if link:
                        if link.startswith('//'): link = "https:" + link
                        elif not link.startswith('http'): link = "https://search.books.com.tw" + link

                    img_src = ""
                    if img_tag:
                        raw_html = str(img_tag)
                        decoded_html = unquote(raw_html)
                        match = re.search(r'(https?://(?:www\.|im1\.)?books\.com\.tw/img/[^"\']+\.(?:jpg|png|jpeg))', decoded_html)
                        
                        if match:
                            img_src = match.group(1)
                        else:
                            img_src = img_tag.get('data-original') or img_tag.get('src')
                            if img_src:
                                img_src = unquote(img_src)
                                if 'getImage' in img_src:
                                    try:
                                        img_src = img_src.split('i=')[1].split('&')[0]
                                    except: pass

                        if img_src:
                            if img_src.startswith('//'): img_src = "https:" + img_src
                            if 'blank' in img_src or 'loading' in img_src: img_src = ""

                    if not img_src:
                        img_src = "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/no-image.jpg"

                    results.append({'platform': '博客來', 'name': name, 'price': price, 'link': link, 'img': img_src, 'sales': '推薦', 'rating': 4.2})
            except: continue
            
        print(f"✅ 博客來 成功: 抓到 {len(results)} 筆")
        return results
    except Exception as e:
        print(f"❌ 博客來 錯誤: {e}")
        return []
    finally:
        if driver: driver.quit()

@app.route('/')
def home():
    return render_template('shop.html')

@app.route('/api/search')
def api_search():
    keyword = request.args.get('q', '')
    if not keyword: return jsonify([])

    print(f"\n🚀 [開始搜尋] 關鍵字: {keyword}")
    results = []
    
    results.extend(scrape_pchome(keyword))
    results.extend(scrape_momo(keyword))
    results.extend(scrape_books(keyword))

    results.sort(key=lambda x: x['price'])
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)