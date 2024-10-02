import requests
from bs4 import BeautifulSoup
import datetime

def get_data_all(ticker):
    proxies = {
        "http": "http://bplecvbo-rotate:afno4uqpkf8g@p.webshare.io:80/",
        "https": "http://bplecvbo-rotate:afno4uqpkf8g@p.webshare.io:80/"
    }

    headers = {
        'authority': 'hotcopper.com.au',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    url = f'https://hotcopper.com.au/asx/{ticker}/'
    print(f'Scraping {url}')
    
    try:
        response = requests.get(url, headers=headers)#, proxies=proxies)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.select('tr[class^="thread-tr"]:not([class*="list-detail"])')

    dict_list = []
    
    for row in rows:
        try:
            id = row.select_one('[class]').a.attrs['href'].split('/')[-1]
        except:
            id = -1

        try:
            subject = row.select_one('td[class^="subject-td"]').select_one('a').text.strip()
        except:
            subject = 'N/A'

        try:
            comments = row.select_one('[class^="replies-td"]').text.strip()
        except:
            comments = 'N/A'

        try:
            views = row.select('td[class^="stats-td"]')[1].text.strip()
        except:
            views = 'N/A'

        try:
            start_date = row.select_one('td[class^="stats-td is-hidden-touch"]').attrs['title']
        except:
            start_date = 'N/A'

        single_dict = {
            "id": id,
            "ticker": ticker,
            "subject": subject,
            "datetime": datetime.datetime.now(),
            "comments": comments,
            "views": views,
            "start_date": start_date
        }
        dict_list.append(single_dict)

    return dict_list



