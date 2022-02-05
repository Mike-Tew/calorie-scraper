from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests


DAYS_TO_SCRAPE = 5
calories_list = []

for day in range(DAYS_TO_SCRAPE, 0, -1):
    date = datetime.today() - timedelta(days=day)
    formatted_date = date.strftime("%Y-%m-%d")

    page = requests.get(
        f"https://www.myfitnesspal.com/food/diary/Switesir?date={formatted_date}"
    )
    soup = BeautifulSoup(page.content, "html.parser")
    calories = soup.find("tr", class_="remaining").contents[3].get_text()

    format_calories = int(calories.replace(",", ""))
    calories_list.append(format_calories)

    print(calories_list)

prev_list = [500, 700, 1001, 1050, 875]
