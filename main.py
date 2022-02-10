# TODO
# Scrape calorie data
# Calculate data

import requests
import threading
from dataclasses import dataclass, field
from tkinter import END, Tk, LabelFrame, Label, Button
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


DAYS_TO_SCRAPE = 5
calories_list = []


@dataclass(order=True)
class CalorieData:
    sort_index: int = field(init=False, repr=False)
    date_delta: int
    date_string: str
    calories: int = 0

    def __post_init__(self):
        self.sort_index = self.date_delta


class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.title("Calorie Scraper")
        self.geometry("200x300+1000+300")

        self.cal

        self.calorie_frame = LabelFrame(self, text="Calories")
        self.calorie_frame.pack()
        self.text_box = Label(self.calorie_frame)
        self.text_box.pack()
        self.scrape_button = Button(
            self.calorie_frame,
            text="Scrape",
            command=lambda: threading.Thread(target=self.scrape).start(),
        )
        self.scrape_button.pack()

    def scrape(self):
        self.scrape_button["state"] = "disabled"
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
            self.text_box["text"] += f"\n{format_calories}"

        print(calories_list)
        self.scrape_button["state"] = "normal"


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
