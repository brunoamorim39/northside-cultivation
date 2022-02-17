import time
import datetime
import board
import adafruit_dht
import mh_z19

from ..application.__init__ import db
from ..application.models import DataLog, DataLogHistorical

# Initialize runtime parameters
dht_device = adafruit_dht.DHT22(board.D4)
sampling_frequency = 100.0

def trim_samples(sample_id):
    if sample_id > 25920:
        present_first_sample = DataLog.query.first()
        historical_sample = DataLogHistorical(present_first_sample)
        db.session.add(historical_sample)
        db.session.delete(present_first_sample)
        db.session.commit()

while True:
    try:
        # Retrieve current latest sample number from database
        sample_num = DataLog.query.order_by(DataLog.id.desc()).first().id
        sample_num += 1

        # Collect data points from DHT22 and MH-Z19B sensors
        current_time = datetime.datetime.now()
        temperature = dht_device.temperature * (9 / 5) + 32
        humidity = dht_device.humidity
        carbon_dioxide = mh_z19.read()
        print(f'Sample Number: {sample_num} | Time of Sample: {current_time} | Temperature: {temperature} | Humidity: {humidity} | Carbon Dioxide: {carbon_dioxide}')

        sample = DataLog(sample_num, current_time, temperature, humidity, carbon_dioxide)
        db.session.add(sample)
        db.session.commit()

        trim_samples(sample_num)

        time.sleep(sampling_frequency)

    except RuntimeError as error:
        print(error.args[0])
        time.sleep(sampling_frequency)
        continue
    except Exception as error:
        dht_device.exit()
        raise error