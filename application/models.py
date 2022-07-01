from __init__ import db

class DataLog(db.Model):
    '''
    Model creates the database table for collecting and storing of data logged from temperature, humidity, and CO2 sensors. Entries are classified with the following columns:
        - Sample #
        - Local time of collection
        - Realtime temperature in Fahrenheit
        - Realtime relative humidity as a percentage
        - Realtime CO2 content as parts per million (ppm)
    '''
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(45), unique=False, nullable=False)
    temperature = db.Column(db.Float, unique=False, nullable=False)
    humidity = db.Column(db.Float, unique=False, nullable=False)
    carbon_dioxide = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return f'''
            Sample collected at: {self.time}
            Temperature: {self.temperature}
            Humidity: {self.humidity}
            CO2 Content: {self.carbon_dioxide}
            '''