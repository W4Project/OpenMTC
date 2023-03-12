# notes:
# Smart Farm Monitoring System
# IPE - Sensors only


from random import random

from openmtc_app.onem2m import XAE
from openmtc_onem2m.model import Container


class TestIPE(XAE):
    remove_registration = True

    # sensors to create
    sensors = [
        'Sol_Temp',
        'Env_Temp',
        'Humi',
        'Soil_pH'
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
            if sensor.startswith('Sol_Temp'):
                value_range = self.sol_temp_range
                value_offset = self.sol_temp_offset
            elif sensor.startswith('Env_Temp'):
                value_range = self.env_temp_range
                value_offset = self.env_temp_offset
            elif sensor.startswith('Humi'):
                value_range = self.humi_range
                value_offset = self.humi_offset
            else:
                value_range = self.pH_range
                value_offset = self.pH_offset


            # generate random sensor data
            if sensor.startswith('Soil_pH'):
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
        if sensor.startswith('Sol_Temp'):
            labels.append('nutrient solution temperature')
        elif sensor.startswith('Env_Temp'):
            labels.append('environmental temperature')
        elif sensor.startswith('Humi'):
            labels.append('humidity')
        else:
            labels.append('soil pH value')

        measurements_container = Container(resourceName='measurements')
        measurements_container = self.create_container(device_container.path,
                                                       measurements_container,
                                                       labels=labels,
                                                       max_nr_of_instances=3)

        # add measurements_container from sensor to _recognized_measurement_containers
        self._recognized_measurement_containers[sensor] = measurements_container

    def push_sensor_data(self, sensor, value):

        # build data set with value and metadata
        if sensor.startswith('Sol_Temp'):
            data = {
                'value': value,
                'type': 'nutrient solution temp',
                'unit': 'degreeC'
            }
        elif sensor.startswith('Env_Temp'):
            data = {
                'value': value,
                'type': 'environmental temperature',
                'unit': 'degreeC'
            }
        elif sensor.startswith('Humi'):
            data = {
                'value': value,
                'type': 'humidity',
                'unit': 'percentage'
            }
        else:
            data = {
                'value': value,
                'type': 'soil pH value',
                'unit': ''
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
