# TODO
# Calculate data
# Validate and add default to input
# Display data in the GUI

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from tkinter import END, Entry, Tk, LabelFrame, Label, Button
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
from tkcalendar import DateEntry


@dataclass(order=True)
class CalorieData:
    sort_index: int = field(init=False, repr=False)
    date_object: datetime
    calories: int = 0

    def __post_init__(self):
        self.sort_index = self.date_object


class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.calorie_data_list = []
        self.title("Calorie Scraper")
        self.geometry("200x300+1000+300")

        self.date_frame = LabelFrame(self, text="Select dates")
        self.date_frame.pack()
        self.date_selector = DateEntry(self.date_frame, selectmode="day")
        self.date_selector.pack()
        self.days_entry = Entry(self.date_frame)
        self.days_entry.pack()

        self.calorie_frame = LabelFrame(self, text="Calories")
        self.calorie_frame.pack()
        self.scrape_button = Button(
            self.calorie_frame,
            text="Scrape",
            command=lambda: threading.Thread(target=self.scrape).start(),
        )
        self.scrape_button.pack()

    def scrape(self):
        selected_date = self.date_selector.get_date()
        num_days = int(self.days_entry.get())
        for day in range(num_days):
            date_increment = selected_date + timedelta(days=day)
            page = requests.get(
                f"https://www.myfitnesspal.com/food/diary/Switesir?date={date_increment}"
            )
            soup = BeautifulSoup(page.content, "html.parser")
            calories = soup.find("tr", class_="remaining").contents[3].get_text()
            format_calories = int(calories.replace(",", ""))

            self.calorie_data_list.append(CalorieData(date_increment, format_calories))
            print(format_calories)

        self.calorie_data_list.sort()

        for calorie_data in self.calorie_data_list:
            self.create_display_label(calorie_data)

    def create_display_label(self, calorie_data):
        calorie_frame = ttk.Frame(self.calorie_frame)
        calorie_frame.pack()
        date_text = calorie_data.date_object.strftime("%b %d:")
        date_label = ttk.Label(calorie_frame, text=date_text)
        date_label.pack(side="left")
        text_color = "green"
        if calorie_data.calories < 0: text_color = "red"
        calorie_label = ttk.Label(
            calorie_frame, text=calorie_data.calories, foreground=text_color
        )
        calorie_label.pack(side="right")


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
