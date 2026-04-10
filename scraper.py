import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import re

def parse_mca():
    url = "https://mca.lv/sezonas-kalendars/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    cal = Calendar()
    cal.add('prodid', '-//MCA Calendar//mca.lv//')
    cal.add('version', '2.0')

    # Ищем контент на странице
    content = soup.find('main') or soup.find('article') or soup.find('body')
    text_lines = content.get_text(separator='\n').split('\n')

    for line in text_lines:
        line = line.strip()
        # Ищем дату формата DD.MM.YYYY
        date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', line)
        if date_match:
            d, m, y = date_match.groups()
            try:
                event_date = datetime(int(y), int(m), int(d))
                event = Event()
                event.add('summary', line) 
                event.add('dtstart', event_date.date())
                # Оставляем только ссылку на источник
                event.add('description', f'Источник: {url}')
                cal.add_component(event)
            except ValueError:
                continue

    with open('mca_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    parse_mca()
