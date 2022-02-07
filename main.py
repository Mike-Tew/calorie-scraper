# TODO
# Create Tkinter GUI
# Scrape calorie data
# Calculate data

import requests
import threading
from tkinter import END, Tk, LabelFrame, Label, Button
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


DAYS_TO_SCRAPE = 5
calories_list = []


# prev_list = [500, 700, 1001, 1050, 875]


class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.title("Calorie Scraper")
        self.geometry("+1000+300")

        self.calorie_frame = LabelFrame(self, text="Calories")
        self.calorie_frame.pack()
        self.text_box = Label(self.calorie_frame)
        self.text_box.pack()
        self.scrape_button = Button(
            self.calorie_frame,
            text="Scrape",
            command=threading.Thread(target=self.scrape).start
        )
        self.scrape_button.pack()

    def scrape(self):
        self.text_box["text"] = "Calories"
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
            print(format_calories)

        print(calories_list)


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
