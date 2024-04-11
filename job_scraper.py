import csv
import requests
import itertools
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


#Scraping data
def get_url(position, location, page):
    template = 'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords={}&txtLocation={}&pageNum={}'
    url = template.format(position, location, page)
    return url


def get_record(card, soup):
    company = card.find('h3', class_='joblist-comp-name').text.strip()
    ultag = card.find('ul', class_='top-jd-dtl clearfix')
    exptag_content = ultag.find('li').get_text().strip()
    experience = exptag_content[11:]
    location_tag = soup.find('i', class_='material-icons', string='location_on').find_next('span')
    location = location_tag.get_text(strip=True)
    skills = card.find('span', class_='srp-skills').text.strip()
    job_url = card.header.h2.a['href']
    published_dates = card.select('span.sim-posted > span')

    if len(published_dates) > 0:
        published_date = published_dates[-1].text

    record = (company, experience, location, skills, job_url, published_date)
    return record


def scrape_jobs():
    positions = position_var.get().split(',') 
    locations = location_var.get().split(',')  
    pages = 7

    records = []
    for position, location in itertools.product(positions, locations):
        for page in range(1, pages + 1):
            url = get_url(position.strip(), location.strip(), page) 
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            cards = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

            if not cards:
                break

            for card in cards:
                record = get_record(card, soup)
                if record not in records:
                    records.append(record)

    update_status('Scraping complete.')
    return records


#Output format
def save_to_csv(records):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            csvfile = csv.writer(f)
            csvfile.writerow(['Company', 'Experience', 'Location', 'Skills', 'Job URL', 'Published Date'])
            for record in records:
                csvfile.writerow(record)
        update_status(f'Data saved to {file_path}')


def save_to_excel(records):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df = pd.DataFrame(data=records)
        df.to_excel(file_path, index=False, header=False)
        update_status(f'Data saved to {file_path}')

def save_data(records):
    file_type = file_format_var.get()
    if file_type == 'csv':
        save_to_csv(records)
    elif file_type == 'excel':
        save_to_excel(records)

def update_status(message):
    status_label.config(text=message)


# User interface
def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    root.geometry(f"{width}x{height}+{x}+{y}")

def style_gui():
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 12), padding=5)
    style.configure('TButton', font=('Arial', 12), padding=5)

root = tk.Tk()
root.title("Job Scraping App")

window_width = 600
window_height = 400

center_window(root, window_width, window_height)

style_gui()

position_label = ttk.Label(root, text="Enter Job Role:")
position_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

position_var = tk.StringVar()
position_entry = ttk.Entry(root, textvariable=position_var)
position_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

location_label = ttk.Label(root, text="Enter Location:")
location_label.grid(row=1, column=0, padx=10, pady=10, sticky='e')

location_var = tk.StringVar()
location_entry = ttk.Entry(root, textvariable=location_var)
location_entry.grid(row=1, column=1, padx=10, pady=10, sticky='w')

file_format_label = ttk.Label(root, text="Select Format:")
file_format_label.grid(row=2, column=0, padx=10, pady=10, sticky='e')

file_format_var = tk.StringVar()
file_format_combobox = ttk.Combobox(root, textvariable=file_format_var, values=['csv', 'excel'])
file_format_combobox.grid(row=2, column=1, padx=10, pady=10, sticky='w')
file_format_combobox.set('csv')  # Set default value

scrape_button = ttk.Button(root, text="Scrape Jobs", command=lambda: save_data(scrape_jobs()))
scrape_button.grid(row=3, column=0, columnspan=2, pady=10)


status_label = ttk.Label(root, text="")
status_label.grid(row=3, column=0, columnspan=2, pady=10)

root.mainloop()




