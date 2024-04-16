"""
**
Open terminal in this (WeatherDataScraping) directory (right-click the folder and select 'open in: terminal')
write(copy-paste): pip install -r requirements.txt
**
"""

import os
import time
import calendar
import pandas as pd
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

website = 'https://www.wunderground.com/history/daily/in/kolkata'
cwd = os.getcwd()
driver_path = os.path.join(cwd, 'chromedriver-win64', 'chromedriver.exe')

# For visual testing i.e. if you want to see what is happening then uncomment line 25 and comment line 28, 29, & 30,
# but it will use more resources
# driver = webdriver.Chrome(driver_path)

# you can only see what is happening in the output console. - Recommended
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=driver_path, options=options)

driver.get(website)

print("Data extraction procedure started...")
time.sleep(5)

years = []
for year in range(2024, 1995, -1):
    years.append(year)

months = list(calendar.month_name)[1:]
months_with_31_days = []
for month in months:
    num_days = calendar.monthrange(2024, list(calendar.month_name).index(month))[1]
    if num_days == 31:
        months_with_31_days.append(month)

days = []
for day in range(1, 32):
    days.append(day)


def is_leap_year(asked_year):
    return (asked_year % 4 == 0 and asked_year % 100 != 0) or (asked_year % 400 == 0)


def stop_program():
    print("\nProgram is being forcefully stopped.")
    os.system("taskkill /F /PID %d" % os.getpid())


def select_year(selected_year):
    try:
        year_selection = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'yearSelection')))
        year_selection.find_element_by_xpath(f'./option[{years.index(selected_year) + 1}]').click()
        time.sleep(1)
    except TimeoutException:
        print(f"Unable to select {selected_year}!")
        stop_program()


def select_month(selected_month):
    try:
        month_selection = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'monthSelection')))
        month_selection.find_element_by_xpath(f'./option[{months.index(selected_month) + 1}]').click()
        time.sleep(1)
    except TimeoutException:
        print(f"Unable to select {selected_month}!")
        stop_program()


def select_day(selected_day):
    try:
        day_selection = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'daySelection')))
        day_selection.find_element_by_xpath(f'./option[{days.index(selected_day) + 1}]').click()
        time.sleep(1)
    except TimeoutException:
        print(f"Unable to select {selected_day}!")
        stop_program()


def click_view_button():
    try:
        view_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'dateSubmit')))
        view_button.click()
        time.sleep(5)
    except TimeoutException:
        print("Unable to click view button!")
        stop_program()


def extract_data_to_csv(starting_year, ending_year, date):
    table_header_row = driver.find_elements_by_xpath('//thead[@role="rowgroup"]')
    titles = []
    for title in table_header_row:
        titles = title.text.split('\n')

    records = driver.find_elements_by_xpath('//tbody[@role="rowgroup"]/tr')
    data = []
    for i in range(len(titles)):
        temp_list = []
        for record in records:
            temp_list.append(record.find_element_by_xpath(f'./td[{i + 1}]').text)
        data.append(temp_list)

    if len(data) == 0:
        no_of_dates = 1
    else:
        no_of_dates = len(data[0])
    temp_date = []
    for i in range(no_of_dates):
        temp_date.append(date)

    titles.insert(0, 'date')
    data.insert(0, temp_date)

    table = {}
    for i in range(len(titles)):
        table[titles[i]] = tuple(data[i])
    temp_df = pd.DataFrame(table)

    final_csv_file_path = os.path.join(cwd, f'weather_data_{starting_year}-{ending_year}.csv')
    if os.path.exists(final_csv_file_path) and os.path.getsize(final_csv_file_path) > 0:
        final_df = pd.read_csv(final_csv_file_path)
    else:
        final_df = pd.DataFrame()

    final_df = pd.concat([final_df, temp_df], ignore_index=True)

    final_df.to_csv(f'weather_data_{starting_year}-{ending_year}.csv', index=False)

    print(f"Extracted data of {date}.")


start_date = '01-01-1996'
end_date = '31-03-2024'

start_day, start_month_index, start_year = start_date.split('-')
end_day, end_month_index, end_year = end_date.split('-')

if os.path.exists(f'weather_data_{start_year}-{end_year}.csv'):
    df = pd.read_csv(f'weather_data_{start_year}-{end_year}.csv')
    last_date_str = df['date'].iloc[-1]

    last_date = datetime.strptime(last_date_str, '%d-%m-%Y')
    next_date = last_date + timedelta(days=1)
    next_date_str = next_date.strftime('%d-%m-%Y')

    start_day, start_month_index, start_year = next_date_str.split('-')

year = int(start_year)
month = months[int(start_month_index)-1]
day = int(start_day)

'''Changing the date & Clicking view button, then extracting data'''
while True:
    day_of_current_date = f'{0 if len(str(day)) == 1 else ""}{day}'
    month_of_current_date = f'{0 if len(str(months.index(month)+1)) == 1 else ""}{months.index(month)+1}'
    current_date = f'{day_of_current_date}-{month_of_current_date}-{year}'

    select_year(year)

    select_month(month)

    select_day(day)

    click_view_button()

    '''Waiting for loading the page'''
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'thead')))
        time.sleep(1)
    except TimeoutException:
        print("Table is not found or took too much time to load table!")

    extract_data_to_csv(start_date[-4:], end_date[-4:], current_date)
    time.sleep(1)

    if year == int(end_year) and months.index(month)+1 == int(end_month_index) and day == int(end_day):
        break

    if month == 'February' and is_leap_year(year) and day == 29:
        select_day(day)
        month = 'March'
        day = 1
    elif month == 'February' and not is_leap_year(year) and day == 28:
        select_day(day)
        month = 'March'
        day = 1
    elif month not in months_with_31_days and day == 30:
        select_day(day)
        month = months[(months.index(month) + 1) % len(months)]
        day = 1
    elif month in months_with_31_days and day == 31:
        select_day(day)
        if month == 'December':
            year += 1
        month = months[(months.index(month) + 1) % len(months)]
        day = 1
    else:
        select_day(day)
        day += 1

time.sleep(5)

print("\nData extraction completed successfully.")

driver.quit()
