import time
import json
import platform
import os
import psutil
from datetime import datetime, timedelta
from dummy_sensor import DummySensor


class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.ds = DummySensor()
        self.log_history = []
        self.settings = self._load_settings()

    def _load_settings(self):
        settings = {
            'os': True,
            'os_version': True,
            'cpu_type': True,
            'cpu_cores': True,
            'memory': True,
            'cpu_usage': True,
            'memory_usage': True
        }
        try:
            with open('setting.txt', 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    settings[key.strip()] = value.strip().lower() == 'true'
        except FileNotFoundError:
            pass
        return settings

    def get_sensor_data(self):
        start_time = datetime.now()
        print('Mission Computer started. Press "q" to stop.')

        while True:
            if self.check_for_exit():
                print('System stopped…')
                break

            self.ds.set_env()
            new_data = self.ds.get_env()
            self.env_values = new_data

            print(json.dumps(self.env_values, indent=4))

            timestamp = datetime.now()
            self.log_history.append((timestamp, new_data))

            if (timestamp - start_time).seconds >= 60:
                self.print_5min_average()
                start_time = timestamp

            time.sleep(5)

    def check_for_exit(self):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 'q':
                return True
        return False

    def print_5min_average(self):
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)

        recent_data = [
            data for ts, data in self.log_history
            if five_minutes_ago <= ts <= now
        ]

        if not recent_data:
            print('No data available for 5-minute average.')
            return

        average_data = {}
        keys = self.env_values.keys()

        for key in keys:
            values = [d[key] for d in recent_data]
            average_data[key] = sum(values) / len(values)

        print('---- 5 Minute Average ----')
        print(json.dumps(average_data, indent=4))

    def get_mission_computer_info(self):
        info = {}
        try:
            if self.settings.get('os'):
                info['os'] = platform.system()
            if self.settings.get('os_version'):
                info['os_version'] = platform.version()
            if self.settings.get('cpu_type'):
                info['cpu_type'] = platform.processor()
            if self.settings.get('cpu_cores'):
                info['cpu_cores'] = os.cpu_count()
            if self.settings.get('memory'):
                info['memory'] = str(round(psutil.virtual_memory().total / (1024 ** 3), 2)) + ' GB'
        except Exception as e:
            info['error'] = str(e)

        print('---- System Info ----')
        print(json.dumps(info, indent=4))
        return info

    def get_mission_computer_load(self):
        load = {}
        try:
            if self.settings.get('cpu_usage'):
                load['cpu_usage'] = str(psutil.cpu_percent(interval=1)) + ' %'
            if self.settings.get('memory_usage'):
                memory = psutil.virtual_memory()
                load['memory_usage'] = str(memory.percent) + ' %'
        except Exception as e:
            load['error'] = str(e)

        print('---- System Load ----')
        print(json.dumps(load, indent=4))
        return load


if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_mission_computer_info()
    RunComputer.get_mission_computer_load()
    RunComputer.get_sensor_data()
