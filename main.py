# TODO
# Validate and add default to input

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
from tkcalendar import DateEntry

import httpx
import asyncio


@dataclass(order=True)
class CalorieData:
    sort_index: int = field(init=False, repr=False)
    date_object: datetime
    calories: int = 0

    def __post_init__(self):
        self.sort_index = self.date_object


class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calorie Scraper")
        self.geometry("200x350+800+300")

        self.date_frame = tk.LabelFrame(self, text="Select dates")
        self.date_frame.pack(ipadx=10, ipady=10)
        self.date_selector = DateEntry(self.date_frame, selectmode="day")
        self.date_selector.pack(pady=10)
        self.days_entry = tk.Entry(self.date_frame)
        self.days_entry.pack()

        self.scrape_button = ttk.Button(
            self,
            text="Scrape",
            command=lambda: threading.Thread(target=self.scrape).start(),
        )
        self.scrape_button.pack(pady=[5, 15])
        self.calorie_frame = tk.LabelFrame(self)

    async def fetch_and_parse(self, client, date):
        url = f"https://www.myfitnesspal.com/food/diary/Switesir?date={date}"
        html = await client.get(url, follow_redirects=True)
        soup = BeautifulSoup(html.content, "html.parser")
        calories = soup.find("tr", class_="remaining").contents[3].get_text()
        format_calories = int(calories.replace(",", ""))
        return CalorieData(date, format_calories)

    async def scrape_urls(self, dates):
        async with httpx.AsyncClient() as client:
            self.data_list = await asyncio.gather(
                *(self.fetch_and_parse(client, date) for date in dates)
            )
        self.data_list.sort()

    def scrape(self):
        selected_date = self.date_selector.get_date()
        num_days = int(self.days_entry.get())
        dates = [selected_date + timedelta(days=day) for day in range(num_days)]
        asyncio.run(self.scrape_urls(dates))

        self.calorie_frame.destroy()
        self.calorie_frame = tk.LabelFrame(self, text="Result")
        self.calorie_frame.pack(ipadx=10, ipady=10)
        self.display_totals()
        for calorie_data in self.data_list:
            self.display_calories(calorie_data)

    def display_totals(self):
        total_frame = tk.Frame(self.calorie_frame)
        total_frame.pack()
        ttk.Label(total_frame, text="Total:", width=10, font="Helvetica 14 bold").pack(
            side="left"
        )
        calorie_list = [data.calories for data in self.data_list]
        calorie_total = sum(calorie_list)
        ttk.Label(
            total_frame,
            text=calorie_total,
            font="Helvetica 14 bold",
            width=4,
            foreground=self.get_color(calorie_total),
        ).pack(side="right", anchor="e")

        average_frame = tk.Frame(self.calorie_frame)
        average_frame.pack()
        average = calorie_total // len(calorie_list)
        ttk.Label(
            average_frame, text="Average:", font="Helvetica 14 bold", width=10
        ).pack(side="left")
        ttk.Label(
            average_frame,
            text=average,
            font="Helvetica 14 bold",
            width=4,
            foreground=self.get_color(average),
        ).pack(side="right", anchor="e")
        sep = ttk.Separator(self.calorie_frame, orient="horizontal")
        sep.pack(fill="x", pady=10)

    def display_calories(self, calorie_data):
        calorie_frame = tk.Frame(self.calorie_frame)
        calorie_frame.pack()
        date_text = calorie_data.date_object.strftime("%b %d - ")
        date_label = ttk.Label(
            calorie_frame, text=date_text, font="Helvetica 10", width=7
        )
        date_label.pack(side="left", anchor="e")

        calories = calorie_data.calories
        calorie_label = ttk.Label(
            calorie_frame,
            text=calories,
            font="Helvetica 10",
            foreground=self.get_color(calories),
            width=5,
        )
        calorie_label.pack(side="right", anchor="e")

    def get_color(self, num):
        return "red" if num < 0 else "green"


if __name__ == "__main__":
    gui = Gui()
    gui.mainloop()
