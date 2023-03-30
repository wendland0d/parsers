import requests
from bs4 import BeautifulSoup
import steam.webauth as wa
import requests
import random
from fake_useragent import UserAgent
import json


def steam_login(LOGIN: str, PASSWORD: str) -> requests.Session:
    user = wa.WebAuth(LOGIN)

    try:
        session = user.login(PASSWORD)

    except wa.EmailCodeRequired:
        email_code = input(f'EMail code: ')
        session = user.login(email_code=email_code)
    except wa.TwoFactorCodeRequired:
        twoFA = input(f'{LOGIN} 2FA: ')
        session = user.login(twofactor_code=twoFA)
    

    return session

def buff_login(session: requests.Session) -> requests.Session:
    deff_headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        'accept': '*/*',
    }
    temp_html = session.get('https://steamcommunity.com/openid/login?openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.realm=https%3A%2F%2Fbuff.163.com%2F&openid.sreg.required=nickname%2Cemail%2Cfullname&openid.assoc_handle=None&openid.return_to=https%3A%2F%2Fbuff.163.com%2Faccount%2Flogin%2Fsteam%2Fverification%3Fback_url%3D%252Faccount%252Fsteam_bind%252Ffinish&openid.ns.sreg=http%3A%2F%2Fopenid.net%2Fextensions%2Fsreg%2F1.1&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select', headers=deff_headers).content
    soup = BeautifulSoup(temp_html, features='html.parser')
    openid = {
        'action': (None, soup.find('input', {'id': 'actionInput'})['value']),
        'openid.mode': (None, soup.find('input', {'name': 'openid.mode'})['value']),
        'openidparams': (None, soup.find('input', {'name': 'openidparams'})['value']),
        'nonce': (None, soup.find('input', {'name': 'nonce'})['value'])
    }
    session.post('https://steamcommunity.com/openid/login', files=openid, headers=deff_headers)
    return session

def buff_pages_count() -> int:
    buff_headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36',
        'accept': '*/*',
        'host': 'buff.163.com',
        'referer': 'https://buff.163.com/'
    }

    count = requests.get('https://buff.163.com/api/market/goods?game=csgo&page_num=1&use_suggestion=0&_=1680098328746', headers=buff_headers).json()['data']['total_page']
    return count

def buff_parse(session: requests.Session, pages: int, proxy: list = None):
    
    data = {}

    for i in range(1, pages):
        
        """if proxy and (i == 1 or i == 50):
            session.proxies.update(proxy.pop(random.random))"""
        ua = UserAgent.random
        buff_headers = {
        'user-agent': f'{ua}',
        'accept': '*/*',
        'host': 'buff.163.com',
        'referer': 'https://buff.163.com/'
        }
        response = session.get(url=f'https://buff.163.com/api/market/goods?game=csgo&page_num={i}&use_suggestion=0&_=1680170306951', headers=buff_headers).json()
        if response['code'] != 'OK':
            return 'Proxy is over!'
        for j in range(len(response['data']['items'])):
            _ = response['data']['items'][j]
            print(f"{response['code']} - {i} - {i*j}")
            data.update({f'{i}': _})
            with open('buff.json', 'a') as f:
                json.dump(data, f)
    
    return data


def buff163(proxy: dict = None, s_login: str = None, s_password: str = None, pages: int = 1000):
    """
    :param: session = request.Session - param gets Steam logged-in session (by steam_login() or essential request.Session)
    :param: proxy = dict - param gets dict-like object with proxy/es 
            like with auth {"https":"https://123.123.123.123:8080@root:pass"} or without auth{"https":"https://232.321.313.312:8000"}
    """
    if not s_login or not s_password:
        return 'Login or password is not define'
    data = {}

    #pages = buff_pages_count()
    data.update(
        buff_parse(
        session=buff_login(
            session=steam_login(LOGIN=s_login, PASSWORD=s_password), 
            ),
        pages=pages,
        proxy = proxy
       ))
    


    

if __name__ == '__main__':
    buff163(s_login='', s_password='', pages=250)