import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import re

def parse_mca():
    url = "https://mca.lv/sezonas-kalendars/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        cal = Calendar()
        cal.add('prodid', '-//MCA Calendar//mca.lv//')
        cal.add('version', '2.0')

        # Извлекаем текст и чистим от лишних пробелов
        text = soup.get_text(separator='|')
        lines = [l.strip() for l in text.split('|') if len(l.strip()) > 5]

        found_events = False
        for line in lines:
            # Ищем диапазон (напр. 17.07. - 19.07.2026) или одну дату (25.04.2026)
            dates = re.findall(r'(\d{2})\.(\d{2})\.(?:(\d{4})|)', line)
            
            if dates:
                try:
                    # Пытаемся определить год (берем последний найденный или 2026 по умолчанию)
                    year = next((d[2] for d in reversed(dates) if d[2]), "2026")
                    
                    # Дата начала
                    start_date = datetime(int(year), int(dates[0][1]), int(dates[0][0]))
                    # Дата конца (если это диапазон)
                    if len(dates) > 1:
                        end_date = datetime(int(year), int(dates[-1][1]), int(dates[-1][0]))
                    else:
                        end_date = start_date

                    # Чистим название мероприятия
                    summary = line
                    for d_part in re.findall(r'\d{2}\.\d{2}\.?\d{0,4}', line):
                        summary = summary.replace(d_part, "")
                    
                    # Убираем лишние слова
                    for noise in ["Biļetes", "Lasīt vairāk", "Ses.", "Pie.", "Svē.", "–", "-", "|"]:
                        summary = summary.replace(noise, "")
                    
                    summary = " ".join(summary.split()).strip()

                    if not summary: summary = "Moto Pasākums"

                    event = Event()
                    event.add('summary', summary)
                    event.add('dtstart', start_date.date())
                    # В iCal дата конца не включительна, поэтому добавляем 1 день
                    event.add('dtend', (end_date + timedelta(days=1)).date())
                    event.add('description', f'Источник: {url}')
                    
                    cal.add_component(event)
                    found_events = True
                except Exception as e:
                    print(f"Ошибка парсинга строки {line}: {e}")
                    continue

        if found_events:
            with open('mca_events.ics', 'wb') as f:
                f.write(cal.to_ical())
            print("Календарь успешно обновлен под новый формат сайта!")
        else:
            print("Не удалось найти события. Проверьте структуру сайта.")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    parse_mca()
