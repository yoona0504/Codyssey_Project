import random  # 랜덤 숫자를 생성 라이브러리
import datetime  # 시간과 날짜 라이브러리


# DummySensor 클래스 - 테스트용 센서 클래스
class DummySensor:
    def __init__(self):
        # 센서 값을 저장 딕셔너리
        self.env_values = {
            'mars_base_internal_temperature': 0.0,      
            'mars_base_external_temperature': 0.0,     
            'mars_base_internal_humidity': 0.0,        
            'mars_base_external_illuminance': 0.0,      
            'mars_base_internal_co2': 0.0,              
            'mars_base_internal_oxygen': 0.0           
        }

    def set_env(self):
        # 각 센서 값을 지정된 범위 내에서 랜덤하게 설정
        self.env_values['mars_base_internal_temperature'] = random.uniform(18.0, 30.0)
        self.env_values['mars_base_external_temperature'] = random.uniform(0.0, 21.0)
        self.env_values['mars_base_internal_humidity'] = random.uniform(50.0, 60.0)
        self.env_values['mars_base_external_illuminance'] = random.uniform(500.0, 715.0)
        self.env_values['mars_base_internal_co2'] = random.uniform(0.02, 0.1)
        self.env_values['mars_base_internal_oxygen'] = random.uniform(4.0, 7.0)

    def get_env(self):
        # 날짜와 시간을 문자열로 저장
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 로그 한 줄을 문자열로 작성 (센서 정보 + 시간)
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

        print('로그 생성 완료')

        return self.env_values

if __name__ == '__main__':
    ds = DummySensor()       
    ds.set_env()             
    env_data = ds.get_env()  
    for key, value in env_data.items():
        print(f'{key}: {value:.4f}')