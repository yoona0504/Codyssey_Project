import csv
import mysql.connector
import os


class MySQLHelper:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def insert_weather(self, mars_date, temp, storm):
        query = (
            'INSERT INTO mars_weather (mars_date, temp, storm) '
            'VALUES (%s, %s, %s)'
        )
        values = (mars_date, temp, storm)
        self.cursor.execute(query, values)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()


def read_csv(file_path):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        return [(row[0], int(row[1]), int(row[2])) for row in reader]


def insert_csv_data(file_path, db_helper):
    data = read_csv(file_path)
    for row in data:
        db_helper.insert_weather(row[0], row[1], row[2])


def main():
    file_path = 'mars_weathers_data.csv'
    if not os.path.exists(file_path):
        print('CSV 파일이 존재하지 않습니다:', file_path)
        return

    db_helper = MySQLHelper(
        host='localhost',
        user='root',
        password='yoona',
        database='mars'
    )
    insert_csv_data(file_path, db_helper)
    db_helper.close()
    print('CSV 데이터 삽입 완료')


if __name__ == '__main__':
    main()
