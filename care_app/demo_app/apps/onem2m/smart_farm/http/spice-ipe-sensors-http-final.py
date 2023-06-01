# notes:
# Smart Farm Monitoring System
# IPE - Sensors only
# using HTTP protocol


from random import random

from openmtc_app.onem2m import XAE
from openmtc_onem2m.model import Container

from pymongo import MongoClient


class TestIPE(XAE):
    remove_registration = True

    # sensors to create
    sensors = [
        'HTTP_Sol_Temp',
        'HTTP_Env_Temp',
        'HTTP_Humi',
        'HTTP_pH'
    ]

    # settings for random sensor data generation
    threshold = 0.2

    sol_temp_range = 50
    sol_temp_offset = 0

    env_temp_range = 10
    env_temp_offset = 20

    humi_range = 50
    humi_offset = 40

    pH_range = 20
    pH_offset = 55     # to be divided by 10 later in getting the value


    def _on_register(self):

        self.client = MongoClient('mongodb+srv://onem2mCARE1:onem2mCARE1diliman@onem2m.up2wghs.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client["oneM2M_HTTP_Sensors"]

        # init variables
        self._recognized_sensors = {}
        self._recognized_measurement_containers = {}

        # init base structure
        label = 'devices_http'
        container = Container(resourceName=label)
        self._devices_container = self.create_container(None,
                                                        container,
                                                        labels=[label],
                                                        max_nr_of_instances=0)

        # trigger periodically new data generation
        # every 5 seconds
        self.run_forever(0.5, self.get_random_data)

        # log message
        self.logger.debug('registered')

    def get_random_data(self):

        # at random time intervals
        if random() > self.threshold:

            # select a random sensor
            sensor = self.sensors[int(random() * len(self.sensors))]

            # set parameters depending on sensor type
            if sensor.startswith('HTTP_Sol_Temp'):
                value_range = self.sol_temp_range
                value_offset = self.sol_temp_offset
            elif sensor.startswith('HTTP_Env_Temp'):
                value_range = self.env_temp_range
                value_offset = self.env_temp_offset
            elif sensor.startswith('HTTP_Humi'):
                value_range = self.humi_range
                value_offset = self.humi_offset
            else:
                value_range = self.pH_range
                value_offset = self.pH_offset


            # generate random sensor data
            if sensor.startswith('pH'):
                value = int(random() * value_range + value_offset)/10
            else:
                value = int(random() * value_range + value_offset)
            
            self.handle_sensor_data(sensor, value)

    def handle_sensor_data(self, sensor, value):

        # initialize sensor structure if never done before
        if sensor not in self._recognized_sensors:
            self.create_sensor_structure(sensor)
        self.push_sensor_data(sensor, value)

    def create_sensor_structure(self, sensor):
        print('initializing sensor: %s' % sensor)

        # create sensor container
        device_container = Container(resourceName=sensor)
        device_container = self.create_container(self._devices_container.path,
                                                 device_container,
                                                 labels=['sensor'],
                                                 max_nr_of_instances=0)

        # add sensor to _recognized_sensors
        self._recognized_sensors[sensor] = device_container


        # create measurements container
        labels = ['measurements']
        if sensor.startswith('HTTP_Sol_Temp'):
            labels.append('nutrient solution temperature')

            self.solTemp = self.db[sensor]

        elif sensor.startswith('HTTP_Env_Temp'):
            labels.append('environmental temperature')

            self.envTemp = self.db[sensor]

        elif sensor.startswith('HTTP_Humi'):
            labels.append('humidity')

            self.humi = self.db[sensor]

        else:
            labels.append('pH value')

            self.ph = self.db[sensor]

        measurements_container = Container(resourceName='measurements')
        measurements_container = self.create_container(device_container.path,
                                                       measurements_container,
                                                       labels=labels,
                                                       max_nr_of_instances=3)

        # add measurements_container from sensor to _recognized_measurement_containers
        self._recognized_measurement_containers[sensor] = measurements_container


    def push_sensor_data(self, sensor, value):

        # build data set with value and metadata
        if sensor.startswith('HTTP_Sol_Temp'):
            data = {
                'value': value,
                'type': 'nutrient solution temp',
                'unit': 'degreeC'
            }

            self.solTemp.insert_one(data.copy())

        elif sensor.startswith('HTTP_Env_Temp'):
            data = {
                'value': value,
                'type': 'environmental temperature',
                'unit': 'degreeC'
            }

            self.envTemp.insert_one(data.copy())

        elif sensor.startswith('HTTP_Humi'):
            data = {
                'value': value,
                'type': 'humidity',
                'unit': 'percentage'
            }

            self.humi.insert_one(data.copy())

        else:
            data = {
                'value': value,
                'type': 'pH value',
                'unit': ''
            }

            self.ph.insert_one(data.copy())

        # print the new data set
        print ("%s: %s" % (sensor, data))

        # finally, push the data set to measurements_container of the sensor
        self.push_content(self._recognized_measurement_containers[sensor], data)
        



if __name__ == "__main__":
    from openmtc_app.runner import AppRunner as Runner


    #host = "mqtts://upCARE1_onem2m:updilimanCARE1@29c49bdf585f4e6d8e93e1522dc5e23f.s1.eu.hivemq.cloud:8883#mn-cse-1"
    #host = "http://29c49bdf585f4e6d8e93e1522dc5e23f.s1.eu.hivemq.cloud:8883#mn-cse-1"
    host = "http://localhost:8000#mn-cse-1"
    app = TestIPE(
        # SSL options
        name = 'OneM2M_HTTP',                       # specify name so we can send simultaneously send data to the same cluster
        originator_pre='//openmtc.org/mn-cse-1',  # originator_pre, needs to match value in cert
        ca_certs='../../openmtc-gevent/certs/ca-chain.cert.pem',
        cert_file='certs/test-ipe.cert.pem',      # cert file, pre-shipped and should match name
        key_file='certs/test-ipe.key.pem'
    )
    Runner(app).run(host)
