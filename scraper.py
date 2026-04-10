import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import re

def parse_mca():
    url = "https://mca.lv/sezonas-kalendars/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка при загрузке сайта: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    cal = Calendar()
    cal.add('prodid', '-//MCA Calendar//mca.lv//')
    cal.add('version', '2.0')

    # Ищем текст во всем теле страницы
    text = soup.get_text(separator='\n')
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        # Ищем дату DD.MM.YYYY
        date_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', line)
        if date_match:
            d, m, y = date_match.groups()
            try:
                event_date = datetime(int(y), int(m), int(d))
                event = Event()
                # Название мероприятия — это вся строка
                event.add('summary', line) 
                event.add('dtstart', event_date.date())
                # Описание делаем пустым, чтобы не было лишнего
                event.add('description', f'Источник: {url}')
                cal.add_component(event)
            except ValueError:
                continue

    with open('mca_events.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    parse_mca()
