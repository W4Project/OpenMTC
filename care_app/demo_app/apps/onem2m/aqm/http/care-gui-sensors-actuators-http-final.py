# notes:
# Air Quality Monitoring System
# GUI - Sensors and Actuators


from openmtc_app.onem2m import XAE


class TestGUI(XAE):
    remove_registration = True
    remote_cse = '/mn-cse-1/onem2m'

    def _on_register(self):
        # init variables
        self.actuators = []
        # start periodic discovery of 'measurements' containers
        self.periodic_discover(
            self.remote_cse,                    # start directory inside cse for discovery
            {'labels': ['measurements']},       # filter criteria (what to discover)
            1,                                  # frequency of repeated discovery (in Hz)
            self.handle_discovery_measurements  # callback function to return the result of the discovery to)
        )
        # start periodic discovery of 'commands' containers
        self.periodic_discover(
            self.remote_cse,                # start directory inside cse for discovery
            {'labels': ['commands']},       # filter criteria (what to discover)
            1,                              # frequency of repeated discovery (in Hz)
            self.handle_discovery_commands  # callback function to return the result of the discovery to)
        )

    def handle_discovery_measurements(self, discovery):
        # for each device container discovered
        for uri in discovery:
            # subscribe to device container with handler function
            print('Subscribing to Resource: %s' % uri)
            self.add_container_subscription(uri, self.handle_measurements)

    def handle_discovery_commands(self, discovery):
        # for every 'commands' container discovered
        for uri in discovery:
            print('discovered commands container: %s' % uri)
            # add discovered commands container to known actuators list
            self.actuators.append(uri)
            print('')

    def handle_measurements(self, container, data):
        print('handle_measurements...')
        print('container: %s' % container)
        print('data: %s' % data)
        # extract information from data set
        value = data['value']
        type_ = data['type']

        # simple logic to control the Fan
        if type_ == 'temperature':
            if value > 30:
                data = {'Power': 'ON'}
                print('Temperature = %s > 30. Turning Fan ON' % value)
            elif value < 18:
                data = {'Power': 'OFF'}
                print('Temperature = %s < 18. Turning Fan OFF' % value)

            # push the new command based on temperature measurements to all known AirCon actuators
            for actuator in self.actuators:
                if 'Fan' in actuator:
                    self.push_content(actuator, data)

        print('')


if __name__ == '__main__':
    from openmtc_app.runner import AppRunner as Runner

    host = 'mqtt://localhost:1883#in-cse-1'
    app = TestGUI(
        poas=['mqtt://localhost:1883'],          # adds poas in order to receive notifications
        # SSL options
        originator_pre='//openmtc.org/in-cse-1',  # originator_pre, needs to match value in cert
        ca_certs='../../openmtc-gevent/certs/ca-chain.cert.pem',
        cert_file='certs/test-gui.cert.pem',      # cert file, pre-shipped and should match name
        key_file='certs/test-gui.key.pem'
    )
    Runner(app).run(host)
