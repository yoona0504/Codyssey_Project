import time
import json

class DummySensor:
    def get_internal_temperature(self):
        return 21.5

    def get_external_temperature(self):
        return -63.0

    def get_internal_humidity(self):
        return 40.0

    def get_external_illuminance(self):
        return 1000.0

    def get_internal_co2(self):
        return 0.03

    def get_internal_oxygen(self):
        return 20.8

class MissionComputer:
    def __init__(self):
        # 화성 기지 환경값 저장용 딕셔너리
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

        # 최근 5분 간 데이터 기록용 (최대 60개씩 저장)
        self.history = {key: [] for key in self.env_values}

        # 더미 센서 인스턴스 생성
        self.ds = DummySensor()

    def get_sensor_data(self):
        """
        센서 데이터를 5초마다 수집하여 출력하고,
        5분마다 평균값을 출력하는 메서드.
        """
        start_time = time.time()
        print('Ctrl+C 를 눌러 출력을 멈추세요.')

        try:
            while True:
                # 센서로부터 값을 읽어 env_values에 저장
                self.env_values['mars_base_internal_temperature'] = self.ds.get_internal_temperature()
                self.env_values['mars_base_external_temperature'] = self.ds.get_external_temperature()
                self.env_values['mars_base_internal_humidity'] = self.ds.get_internal_humidity()
                self.env_values['mars_base_external_illuminance'] = self.ds.get_external_illuminance()
                self.env_values['mars_base_internal_co2'] = self.ds.get_internal_co2()
                self.env_values['mars_base_internal_oxygen'] = self.ds.get_internal_oxygen()

                # 각 항목별로 history에 추가 60개 초과 시 가장 오래된 항목 제거
                for key in self.env_values:
                    self.history[key].append(self.env_values[key])
                    if len(self.history[key]) > 60:
                        self.history[key].pop(0)

                # 현재 센서 데이터를 JSON 형식으로 출력
                print(json.dumps(self.env_values, indent=2))

                # 경과 시간이 5분(=300초)에 가까우면 평균값 출력
                elapsed = time.time() - start_time
                if int(elapsed) % 300 < 5:
                    print('[5분 평균값]')
                    avg_values = {}
                    for key in self.history:
                        avg = sum(self.history[key]) / len(self.history[key])
                        avg_values[key] = round(avg, 2)
                    print(json.dumps(avg_values, indent=2))

                # 5초 대기 후 반복
                time.sleep(5)

        except KeyboardInterrupt:
            # Ctrl+C 입력 시 종료 메시지 출력
            print('System stopped…')

if __name__ == '__main__':
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()
