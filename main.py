# TODO
# Convert to executable

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import ttk

import asyncio
from bs4 import BeautifulSoup
import httpx
from tkcalendar import DateEntry


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
        self.geometry("300x500+800+300")

        self.date_frame = tk.LabelFrame(self, text="Select Dates")
        self.date_frame.pack(ipadx=10)

        self.username_label = ttk.Label(
            self.date_frame, text="Username", font="Helvetica 10 bold"
        )
        self.username_label.grid(pady=10, row=0, column=0)
        self.username_entry = ttk.Entry(self.date_frame)
        self.username_entry.grid(row=0, column=1)

        self.date_selector_label = ttk.Label(
            self.date_frame, text="Start Date", font="Helvetica 10 bold"
        )
        self.date_selector_label.grid(row=1, column=0)
        self.date_selector = DateEntry(
            self.date_frame,
            width=7,
            font="Ariel 10",
            selectmode="day",
            showweeknumbers=False,
            background="black",
            borderwidth=5,
        )
        self.date_selector.grid(row=1, column=1)

        self.day_dropdown_label = ttk.Label(
            self.date_frame, text="Number Of Days", font="Helvetica 10 bold"
        )
        self.day_dropdown_label.grid(padx=10, pady=10, row=2, column=0)
        self.day_dropdown = ttk.Combobox(self.date_frame, width=5)
        self.day_dropdown.grid(row=2, column=1)
        self.day_dropdown["values"] = list(range(1, 15))
        self.day_dropdown.current(6)

        self.scrape_button = ttk.Button(
            self,
            text="Calculate",
            command=lambda: threading.Thread(target=self.run).start(),
        )
        self.scrape_button.pack(pady=10)
        self.calorie_frame = tk.LabelFrame(self)

    def run(self):
        self.calorie_frame.destroy()
        selected_date = self.date_selector.get_date()
        self.calorie_frame = tk.LabelFrame(self, text="Results")
        self.calorie_frame.pack(ipadx=10, ipady=10)
        num_days = int(self.day_dropdown.get())
        dates = [selected_date + timedelta(days=day) for day in range(num_days)]
        asyncio.run(self.scrape_urls(dates))

        self.display_totals()
        for calorie_data in self.data_list:
            self.display_calories(calorie_data)

    async def scrape_urls(self, dates):
        async with httpx.AsyncClient() as client:
            self.data_list = await asyncio.gather(
                *(self.fetch_html(client, date) for date in dates)
            )
        self.data_list.sort()

    async def fetch_html(self, client, date):
        username = self.username_entry.get()
        url = f"https://www.myfitnesspal.com/food/diary/{username}?date={date}"
        html = await client.get(url, follow_redirects=True)
        return CalorieData(date, self.parse_calories(html))

    def parse_calories(self, html):
        soup = BeautifulSoup(html.content, "html.parser")
        calories = soup.find("tr", class_="remaining").contents[3].get_text()
        format_calories = int(calories.replace(",", ""))
        return format_calories

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
