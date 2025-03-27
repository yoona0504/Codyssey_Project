import random
import datetime


class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        self.env_values['mars_base_internal_temperature'] = random.uniform(18.0, 30.0)
        self.env_values['mars_base_external_temperature'] = random.uniform(0.0, 21.0)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50.0, 60.0)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500.0, 715.0)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4.0, 7.0)

    def get_env(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = (
            f'{timestamp}, '
            f'Internal Temp: {self.env_values["mars_base_internal_temperature"]:.2f} C, '
            f'External Temp: {self.env_values["mars_base_external_temperature"]:.2f} C, '
            f'Internal Humidity: {self.env_values["mars_base_internal_humidity"]:.2f} %, '
            f'External Illuminance: {self.env_values["mars_base_external_illuminance"]:.2f} W/m2, '
            f'Internal CO2: {self.env_values["mars_base_internal_co2"]:.4f} %, '
            f'Internal O2: {self.env_values["mars_base_internal_oxygen"]:.2f} %\n'
        )

        with open('sensor_log.txt', 'a') as file:
            file.write(log_entry)

        return self.env_values


if __name__ == '__main__':
    ds = DummySensor()
    ds.set_env()
    env_data = ds.get_env()
    for key, value in env_data.items():
        print(f'{key}: {value:.4f}')
