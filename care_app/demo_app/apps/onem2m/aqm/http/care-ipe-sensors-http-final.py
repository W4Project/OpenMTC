# notes:
# Air Quality Monitoring System
# IPE - Sensors only


from random import random

from openmtc_app.onem2m import XAE
from openmtc_onem2m.model import Container


class TestIPE(XAE):
    remove_registration = True

    # sensors to create
    sensors = [
        'Temp',
        'Humi',
        'PM2_5',
        'PM10',
        'H2S'
    ]

    # settings for random sensor data generation
    threshold = 0.2

    temp_range = 50
    temp_offset = 0

    humi_range = 30
    humi_offset = 30

    pm25_range = 400
    pm25_offset = 0

    pm10_range = 400
    pm10_offset = 0

    h2s_range = 199
    h2s_offset = 1


    def _on_register(self):

        # init variables
        self._recognized_sensors = {}
        self._recognized_measurement_containers = {}

        # init base structure
        label = 'devices'
        container = Container(resourceName=label)
        self._devices_container = self.create_container(None,
                                                        container,
                                                        labels=[label],
                                                        max_nr_of_instances=0)

        # trigger periodically new data generation
        self.run_forever(1, self.get_random_data)

        # log message
        self.logger.debug('registered')

    def get_random_data(self):

        # at random time intervals
        if random() > self.threshold:

            # select a random sensor
            sensor = self.sensors[int(random() * len(self.sensors))]

            # set parameters depending on sensor type
            if sensor.startswith('Temp'):
                value_range = self.temp_range
                value_offset = self.temp_offset
            elif sensor.startswith('Humi'):
                value_range = self.humi_range
                value_offset = self.humi_offset
            elif sensor.startswith('PM2_5'):
                value_range = self.pm25_range
                value_offset = self.pm25_offset
            elif sensor.startswith('PM10'):
                value_range = self.pm10_range
                value_offset = self.pm10_offset
            else:
                value_range = self.h2s_range
                value_offset = self.h2s_offset

            # generate random sensor data
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
        if sensor.startswith('Temp'):
            labels.append('temperature')
        elif sensor.startswith('Humi'):
            labels.append('humidity')
        elif sensor.startswith('PM2_5'):
            labels.append('PM2.5')
        elif sensor.startswith('PM10'):
            labels.append('PM10')
        else:
            labels.append('H2S')

        measurements_container = Container(resourceName='measurements')
        measurements_container = self.create_container(device_container.path,
                                                       measurements_container,
                                                       labels=labels,
                                                       max_nr_of_instances=3)

        # add measurements_container from sensor to _recognized_measurement_containers
        self._recognized_measurement_containers[sensor] = measurements_container

    def push_sensor_data(self, sensor, value):

        # build data set with value and metadata
        if sensor.startswith('Temp'):
            data = {
                'value': value,
                'type': 'temperature',
                'unit': 'degreeC'
            }
        elif sensor.startswith('Humi'):
            data = {
                'value': value,
                'type': 'humidity',
                'unit': 'percentage'
            }
        elif sensor.startswith('PM2_5'):
            data = {
                'value': value,
                'type': 'PM2.5',
                'unit': 'ug/m^3'
            }
        elif sensor.startswith('PM10'):
            data = {
                'value': value,
                'type': 'PM10',
                'unit': 'ug/m^3'
            }
        else:
            data = {
                'value': value,
                'type': 'H2S',
                'unit': 'ppm'
            }

        # print the new data set
        print ("%s: %s" % (sensor, data))

        # finally, push the data set to measurements_container of the sensor
        self.push_content(self._recognized_measurement_containers[sensor], data)


if __name__ == "__main__":
    from openmtc_app.runner import AppRunner as Runner

    host = "http://localhost:8000"
    app = TestIPE(
        # SSL options
        originator_pre='//openmtc.org/mn-cse-1',  # originator_pre, needs to match value in cert
        ca_certs='../../openmtc-gevent/certs/ca-chain.cert.pem',
        cert_file='certs/test-ipe.cert.pem',      # cert file, pre-shipped and should match name
        key_file='certs/test-ipe.key.pem'
    )
    Runner(app).run(host)
