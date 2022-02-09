from __init__ import db

class Data_Log(db.Model):
    '''
    Model creates the database table for collecting and storing of data logged from temperature, humidity, and CO2 sensors. Entries are classified with the following columns:
        - Sample #
        - Local time of collection
        - Realtime temperature in Fahrenheit
        - Realtime relative humidity as a percentage
        - Realtime CO2 content as parts per million (ppm)
    '''
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(8), unique=False, nullable=False)
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

class Realtime_Data(db.Model):
    '''
    Model creates a small, one row database table whose sole purpose is to store the realtime information collected by the environment sensors for factors such as temperature, humidity, and CO2 content.
    '''
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(8), unique=False, nullable=False)
    temperature = db.Column(db.Float, unique=False, nullable=False)
    humidity = db.Column(db.Float, unique=False, nullable=False)
    carbon_dioxide = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return f'''
        REALTIME DATA:
            Sample collected at: {self.time}
            Temperature: {self.temperature}
            Humidity: {self.humidity}
            CO2 Content: {self.carbon_dioxide}
            '''