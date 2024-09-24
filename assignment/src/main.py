import requests
from lxml import html

import dotenv
import os
import random

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

# load the environment variables
dotenv.load_dotenv()

output_path = "./assignment/output/UK_Historic_Station_Data.html"
if os.path.exists(output_path):
    filename = output_path
else:
    filename = "UK_Historic_Station_Data.html"
climate_datas = defaultdict(dict)

# check if the page exists
if not os.path.exists(filename):

    # fetch the page if it doesn't exist
    page = requests.get(os.getenv('URL'))

    # save the page to a file
    with open(filename, 'w', encoding='UTF8') as f:
        f.write(page.text)

    page = page.text

else:
    # if the page exists, read it from the file
    with open(filename, 'r', encoding='UTF8') as f:
        page = f.read()
        
# parse the page to html
tree = html.fromstring(page)

# get the rows from the table
rows = tree.xpath(os.getenv('ROW_XPATH'))

station_num = int(os.getenv('STATION_NUM'))
total_rows = len(rows)
selected_station = random.sample(range(0,total_rows), station_num)

# print the rows
row_num = 0
for row in rows:
    columns = row.xpath(os.getenv('COL_XPATH'))
    columns_content = []
    for column in columns:
        data_link = column.xpath(os.getenv('DATA_XPATH'))
        if not data_link:
            columns_content.append(column.text_content())
        else:
            data_link = data_link[0]
            columns_content.append(data_link)
    row_string = "station name: " + columns_content[0] + "|station location: " + columns_content[1] + "|start year: " + columns_content[2] + "|data link: " + columns_content[3]

    # skip empty rows
    if row_string.strip() == "":
        continue

    if row_num in selected_station:
        station_data_page = requests.get(data_link)
        station_data = station_data_page.text
        data_lines = station_data.splitlines()
        start_index = 0
        for i, data_line in enumerate(data_lines):
            if data_line.startswith("   yyyy"):
                start_index = i + 2
                break
        station_data_lines = data_lines[start_index:]
        current_year = 0
        current_year_data = defaultdict(list)
        for data in station_data_lines:
            if data.startswith("Site"):
                continue
            if data.strip():
                record_data = data.split()
                data_year = int(record_data[0])
                if record_data[2].endswith('*'):
                    data_maxtem = float(record_data[2].strip('*'))
                elif record_data[2] == '---':
                    data_maxtem = float("-inf")
                else:
                    data_maxtem = float(record_data[2])
                if record_data[3].endswith('*'):
                    data_mintem = float(record_data[3].strip('*'))
                elif record_data[3] == '---':
                    data_mintem = float("inf")
                else:
                    data_mintem = float(record_data[3])
                if current_year != data_year:
                    if data_year - current_year == 1:
                        current_year_data[current_year].append(year_maxtem)
                        current_year_data[current_year].append(year_mintem)
                    year_maxtem = data_maxtem
                    year_mintem = data_mintem
                    current_year = data_year
                else:
                    year_maxtem = max(year_maxtem, data_maxtem)
                    year_mintem = min(year_mintem, data_mintem)
        climate_datas[columns_content[0]] = current_year_data
    
    row_num += 1

    print(f'Row {row_num}: {row_string}')
    
#show data picture
plt.figure(figsize=(25.6,9.6))
for key in climate_datas:
    station_name = key
    station_data_year = list(climate_datas[key].keys())
    station_data_maxtem = []
    station_data_mintem = []
    for subkey in climate_datas[key]:
        if climate_datas[key][subkey][0] == float("-inf"):
            station_data_maxtem.append(np.nan)
        else:
            station_data_maxtem.append(climate_datas[key][subkey][0])
        if climate_datas[key][subkey][1] == float("inf"):
            station_data_mintem.append(np.nan)
        else:
            station_data_mintem.append(climate_datas[key][subkey][1])
    plt.subplot(1,2,1)
    plt.plot(station_data_year, station_data_maxtem, label = station_name)
    plt.title('UK Climate Station Max Temperature')
    plt.xlabel('Year')
    plt.ylabel('Temperature/℃')
    plt.subplot(1,2,2)
    plt.plot(station_data_year, station_data_mintem, label = station_name)
    plt.title('UK Climate Station Min Temperature')
    plt.xlabel('Year')
    plt.ylabel('Temperature/℃')
plt.legend()
png_path = "./assignment/output/data.png"
if os.path.exists(png_path):
    plt.savefig(png_path)
else:
    plt.savefig("data.png")
plt.show()
