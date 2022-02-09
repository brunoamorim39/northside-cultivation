import csv
import random
import datetime
import time

data_log = []

for i in range(1000):
    sample = i
    current_time = datetime.datetime.now()
    temp = round(random.uniform(60.00, 70.00), 2)
    humidity = round(random.uniform(85.00, 100.00), 2)
    co2 = round(random.uniform(100.00, 800.00), 2)
    print(f'{sample} | {current_time} | {temp} | {humidity} | {co2}')
    time.sleep(1)

    data_log.append((sample, current_time, temp, humidity, co2))

with open('test_set.csv', 'w', newline='') as csvfile:
    fieldnames = ['sample', 'current time', 'temperature', 'humidity', 'carbon dioxide content']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    for item in data_log:
        writer.writerow({
            'sample': item[0],
            'current time': item[1],
            'temperature': item[2],
            'humidity': item[3],
            'carbon dioxide content': item[4]
            })