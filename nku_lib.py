from selenium import webdriver
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from datetime import datetime, timedelta
import json
import argparse
import send_email

def get_seatid(room):
    f = open('seat_ids.json', 'r')
    content = f.read()
    seat_ids = json.loads(content)
    seat_id = seat_ids[room.upper()]
    return seat_id

def reserve_time(date,hour='9',minute='30'):

    date_time = datetime.now()
    hour = int(hour)
    minute = int(minute)
    if date == 'a':                # 今天
        start_time = date_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if date_time.weekday() != 5:
            end_time = date_time.replace(hour=23, minute=30, second=0, microsecond=0)
        else:
            end_time = date_time.replace(hour=17, minute=30, second=0, microsecond=0)
    else:                          # 明天
        start_time = date_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        start_time += timedelta(days=1)
        if date_time.weekday() != 4:
            end_time = date_time.replace(hour=23, minute=30, second=0, microsecond=0)
        else:
            end_time = date_time.replace(hour=17, minute=30, second=0, microsecond=0)
        end_time += timedelta(days=1)
    # 打印结果
    return str(start_time),str(end_time)

def reserve(start_time, end_time, seat):
    username = '***'
    password = '***'

    options = webdriver.EdgeOptions()  # 创建一个配置对象
    options.add_argument("--headless")  # 开启无界面模式
    options.add_argument("--disable-gpu")
    options.add_argument('--no-sandbox')
    browser = webdriver.Edge(options=options)

    url = 'https://webvpn.nankai.edu.cn/'
    # url = 'https://libic.nankai.edu.cn/'
    browser.get(url=url)
    wait = WebDriverWait(browser, 20)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # 填写表单

    input = browser.find_elements(By.TAG_NAME, 'input')
    input[0].send_keys(username)
    input[1].send_keys(password)

    # 通过验证码
    btn = browser.find_element(By.ID, 'btn')
    action = ActionChains(browser)
    action.click_and_hold(btn).perform()
    action.move_by_offset(xoffset=260, yoffset=0).perform()
    action.release().perform()

    browser.find_element(By.ID, 'submitRole').click()

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                               '#__layout > div > div > div.portal-content > div > div.portal-content__block > div > div.el-scrollbar__wrap > div > div:nth-child(1) > div > div:nth-child(1) > a > div.block-group__item__content > div')))

    cookies = browser.get_cookies()
    cookie = {}

    for item in cookies:
        # print(item['name']+' '+item['value'])
        cookie[item['name']] = item['value']

    browser.find_element(By.CSS_SELECTOR,
                         '#__layout > div > div > div.portal-content > div > div.portal-content__block > div > div.el-scrollbar__wrap > div > div:nth-child(1) > div > div:nth-child(1) > a > div.block-group__item__content > div').click()

    handles = browser.window_handles  # 获取当前浏览器的所有窗口句柄
    browser.switch_to.window(handles[-1])

    with open('cookies.txt', 'w', encoding='utf-8') as f:
        # 将dic dumps json 格式进行写入
        f.write(json.dumps(cookie))

    file = open('cookies.txt', 'r')
    js = file.read()
    cookies = json.loads(js)

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        # 'Cookie': 'show_vpn=0; show_fast=0; heartbeat=1; show_faq=0; wengine_vpn_ticketwebvpn_nankai_edu_cn=3c56fa62b5fd7657; refresh=0',
        'Origin': 'https://webvpn.nankai.edu.cn',
        'Referer': 'https://webvpn.nankai.edu.cn/https/77726476706e69737468656265737421fcfe4395247e6651700388a5d6502720c6dba7/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'lan': '1',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'token': '752dc896c6b84655a3474da1e7bcf659',
    }

    json_data = {
        'sysKind': 8,
        'appAccNo': 41239,
        'memberKind': 1,
        'resvMember': [
            41239,
        ],
        'resvBeginTime': start_time,
        'resvEndTime': end_time,
        'testName': '',
        'captcha': '',
        'resvProperty': 0,
        'resvDev': [
            seat
        ],
        'memo': '',
    }

    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#app > div.container > div.wrap > div.navigation > ul > li.menu-title.el-submenu.is-opened.bg-blue > div > span')))
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div[1]/div[3]/div[1]/ul/li[1]/div/span')))
    print('success')
    requests.packages.urllib3.disable_warnings()
    response = requests.post(
        'https://webvpn.nankai.edu.cn/https/77726476706e69737468656265737421fcfe4395247e6651700388a5d6502720c6dba7/ic-web/reserve?vpn-12-o2-libic.nankai.edu.cn',
        cookies=cookies,
        headers=headers,
        json=json_data,
        verify=False
    )

    print(response.text)
    browser.close()
    return response.json()


def lib(date='a',hour='8',minute='30', seatid = 'wzg4f030'):
    start, end = reserve_time(date, hour, minute)
    seat = get_seatid(seatid)
    result = reserve(start,end,seat)
    return result['message']

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="TEST:")  # )#然后创建一个解析对象

    parser.add_argument('-d', '--date', type=str, help='input date: a for today or b for tomorrow')
    parser.add_argument('-t', '--time', type=str, help='input time: eg 8:30')
    parser.add_argument('-s', '--seat', type=str, help='input seat: eg wzg3f001 or 501-003')
    args = parser.parse_args()

    # 初始化
    date = 'a'
    hour = '8'
    minute = '30'
    seat = 'wzg4f030'

    if args.date:
        date = args.date
    if args.time:
        start_time = args.time.split(':')
        hour = start_time[0]
        minute = start_time[1]
    if args.seat:
        seat = args.seat
    start = time.time()
    message = lib(date, hour, minute, seat)
    end = time.time()
    print(end-start)
    print(message)
    msg = f"{message}\n seat: {seat}"
    send_email.send_email(msg)
