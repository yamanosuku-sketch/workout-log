import sqlite3
from datetime import datetime
import os

DB_FILE = "workout_log.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILE)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            body_weight REAL,
            exercise TEXT NOT NULL,
            weight REAL,
            reps INTEGER,
            sets INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cardio_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            machine TEXT NOT NULL,
            mins INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS body_weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            body_weight REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("テーブルの作成が完了しました")


class WorkoutLog:
    def __init__(self, body_weight, exercise, weight, reps, sets, date=None, record_id=None):
        self.body_weight = body_weight
        self.exercise = exercise
        self.weight = weight
        self.reps = reps
        self.sets = sets
        if date is None:
            self.date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.date = date
        self.id = record_id

class WorkoutManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def add(self, log):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO workout_logs (date, body_weight, exercise, weight, reps, sets)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (log.date, log.body_weight, log.exercise, log.weight, log.reps, log.sets))
        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM workout_logs ORDER BY id ASC')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_one(self, log_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM workout_logs WHERE id =?', (log_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update(self, log):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE workout_logs
            SET date = ?, exercise = ?, weight = ?, reps = ?, sets = ?
            WHERE id = ?
        ''', (log.date, log.exercise, log.weight, log.reps, log.sets, log.id))
        conn.commit()
        conn.close()
        print(f"ID {log.id}の記録を更新しました")

    def delete(self, record_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM workout_logs WHERE id =?', (record_id,))
        conn.commit()
        conn.close()
        print(f"ID {record_id} の記録を削除しました。")

    def get_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM workout_logs WHERE date = ? ORDER BY id ASC',
            (date,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'DELETE FROM workout_logs WHERE date = ?',
            (date,)
        )
        conn.commit()
        conn.close()

    def get_exercise_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT exercise
            FROM workout_logs
            WHERE exercise IS NOT NULL
                AND TRIM(exercise) != ''
            ORDER BY exercise
        ''')

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

class CardioLog:
    def __init__(self, machine, mins, date=None, record_id=None):
        self.machine = machine
        self.mins = mins
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.id = record_id

class CardioManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def add(self, log):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cardio_logs (date, machine, mins)
            VALUES (?, ?, ?)
        ''', ( log.date, log.machine, log.mins))
        conn.commit()
        conn.close()
        print(f"{log.machine} の記録を {log.mins} 分で保存しました！") 

    def get_all(self,):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cardio_logs ORDER BY date DESC')
        logs = cursor.fetchall()
        conn.close()
        return logs
    
    def update(self, log):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE cardio_logs
            SET machine = ?, mins = ?, date = ?
            WHERE id = ?
        ''', (log.machine, log.mins, log.date, log.id))
        conn.commit()
        conn.close()
        print(f"ID {log.id}の記録を更新しました")

    def delete(self, record_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cardio_logs WHERE id =?', (record_id,))
        conn.commit()
        conn.close()
        print(f"ID {record_id} の記録を削除しました。")

    def get_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM cardio_logs WHERE date = ? ORDER BY id ASC',
            (date,) 
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def delete_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()    
        cursor.execute(
            'DELETE FROM cardio_logs WHERE date = ?',
            (date,)
        )
        conn.commit()
        conn.close()

    def get_machine_names(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT machine
            FROM cardio_logs
            WHERE machine IS NOT NULL
            AND TRIM(machine) != ''
            AND machine != '未指定'
            ORDER BY machine
        ''')

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows]

class BodyWeightLog:
    def __init__(self, body_weight, date=None, record_id= None):
        self.body_weight = body_weight
        self.date = date or datetime.now().strftime('%Y-%m-%d')
        self.id = record_id


class BodyWeightManager:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def save(self, log):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO body_weight_logs (date, body_weight)
                       VALUES (?,?)
                       ON CONFLICT(date)
                       DO UPDATE SET body_weight = excluded.body_weight
        ''', (log.date, log.body_weight))

        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM body_weight_logs
            ORDER BY date DESC
        ''')

        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def get_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM body_weight_logs WHERE date = ?',
            (date,)
        )

        row = cursor.fetchone()
        conn.close()
        return row

    def delete_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'DELETE FROM body_weight_logs WHERE date = ?',
            (date,)
        )

        conn.commit()
        conn.close()
    

if __name__ == '__main__':
    init_db()