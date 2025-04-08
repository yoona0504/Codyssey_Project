import time
import json
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

    def get_sensor_data(self):
        start_time = datetime.now()
        print('Mission Computer started. Press "q" to stop.')

        while True:
            if self.check_for_exit():
                print('System stopped…')
                break

            # 센서 데이터 수집
            self.ds.set_env()
            new_data = self.ds.get_env()
            self.env_values = new_data

            # JSON 출력
            print(json.dumps(self.env_values, indent=4))

            # 로그 기록
            timestamp = datetime.now()
            self.log_history.append((timestamp, new_data))

            # 5분 평균 출력
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


if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()
