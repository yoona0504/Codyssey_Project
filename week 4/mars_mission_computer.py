import time
import json

class DummySensor:
    def read_internal_temperature(self):
        return 21.5  # 고정된 내부 온도

    def read_external_temperature(self):
        return -63.0  # 고정된 외부 온도

    def read_internal_humidity(self):
        return 40.0  # 고정된 내부 습도

    def read_external_illuminance(self):
        return 1000.0  # 고정된 외부 광량

    def read_internal_co2(self):
        return 0.03  # 고정된 이산화탄소 농도

    def read_internal_oxygen(self):
        return 20.8  # 고정된 산소 농도


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
        self.history = {key: [] for key in self.env_values}
        self.ds = DummySensor()

    def get_sensor_data(self):
        start_time = time.time()
        print('Press Ctrl+C to stop.')
        try:
            while True:
                # 센서 데이터 수집
                self.env_values['mars_base_internal_temperature'] = self.ds.read_internal_temperature()
                self.env_values['mars_base_external_temperature'] = self.ds.read_external_temperature()
                self.env_values['mars_base_internal_humidity'] = self.ds.read_internal_humidity()
                self.env_values['mars_base_external_illuminance'] = self.ds.read_external_illuminance()
                self.env_values['mars_base_internal_co2'] = self.ds.read_internal_co2()
                self.env_values['mars_base_internal_oxygen'] = self.ds.read_internal_oxygen()

                # 값 기록 (5분 평균용 최대 60개 저장)
                for key in self.env_values:
                    self.history[key].append(self.env_values[key])
                    if len(self.history[key]) > 60:
                        self.history[key].pop(0)

                # JSON 형태로 출력
                print(json.dumps(self.env_values, indent=2))

                # 5분 평균 출력 (5분에 한 번)
                elapsed = time.time() - start_time
                if int(elapsed) % 300 < 5:
                    print('[5분 평균값]')
                    avg_values = {}
                    for key in self.history:
                        avg = sum(self.history[key]) / len(self.history[key])
                        avg_values[key] = round(avg, 2)
                    print(json.dumps(avg_values, indent=2))

                time.sleep(5)
        except KeyboardInterrupt:
            print('System stopped...')


if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()