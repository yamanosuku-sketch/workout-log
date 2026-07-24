from flask import Flask, render_template, request, redirect, url_for
from base import WorkoutManager, WorkoutLog, CardioManager, CardioLog, BodyWeightManager, BodyWeightLog, DB_PATH, init_db
from datetime import datetime, timedelta

app = Flask(__name__)
init_db()
manager = WorkoutManager(DB_PATH)
cardio_manager = CardioManager(DB_PATH)
body_weight_manager = BodyWeightManager(DB_PATH)

def get_input_options():
    default_exercise = [
        'ベンチプレス',
        'インクラインベンチプレス',
        'ダンベルプレス',
        'チェストプレス',
        'ペックフライ',
        'スクワット',
        'レッグプレス',
        'レッグエクステンション',
        'レッグカール',
        'デッドリフト',
        'ルーマニアンデッドリフト',
        'ラットプルダウン',
        'シーテッドロウ',
        'ワンハンドロウ',
        'ショルダープレス',
        'サイドレイズ',
        'リアレイズ',
        'アームカール',
        'ハンマーカール',
    ]

    default_cardio_machines = [
        'クロストレーナー',
        'トレッドミル',
        'アサルトバイク'
        'ステアクライマー',
        'ローイングマシン',
        'ウォーキング',
        'ジョギング',
        'サイクリング',
        '水泳'
    ]

    saved_exercises = manager.get_exercise_names()
    saved_cardio_machines = cardio_manager.get_machine_names()

    exercise_options = list(
        dict.fromkeys(default_exercise + saved_exercises)
    )

    cardio_options = list(
        dict.fromkeys(default_cardio_machines + saved_cardio_machines
        )
    )

    return exercise_options, cardio_options

def parse_body_weight(body_weight_text):
    if body_weight_text:
        return float(body_weight_text)
    return None

@app.route('/')
def index():
    logs = manager.get_all()
    cardio_logs = cardio_manager.get_all()

    body_weight_logs = body_weight_manager.get_all()

    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
             for i in range(90)]
    date_list = sorted(dates)

    daily_data = {}

    for body_weight_log in body_weight_logs:
        date = body_weight_log[1]
        body_weight = body_weight_log[2]
        daily_data[date] = {
            "body_weight": body_weight,
            "exercises": {},
            "cardios": []
        }

    for log in logs:
        date = log[1]
        body_weight = log[2]
        exercise = log[3]

        if date not in daily_data:
            daily_data[date] = {
                "body_weight": None,
                "exercises": {},
                "cardios": []
            }
        
        if exercise not in daily_data[date]["exercises"]:
            daily_data[date]["exercises"][exercise] = 0

        daily_data[date]["exercises"][exercise] += 1

    for cardio in cardio_logs:
        date = cardio[1]
        machine = cardio[2]
        mins = cardio[3]

        if date not in daily_data:
            daily_data[date] = {
                "body_weight": None,
                "exercises": {},
                "cardios": []
            }

        if "cardios" not in daily_data[date]:
            daily_data[date]["cardios"] = []

        daily_data[date]["cardios"].append({
            "machine": machine,
            "mins": mins
        })

    return render_template(
        'index.html',
        date_list=date_list,
        daily_data=daily_data,
        active_page='index'
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        workout_date = request.form.get('date')
        if not workout_date:
            workout_date = datetime.now().strftime('%Y-%m-%d')

        body_weight_text = request.form.get('body_weight')
        body_weight = parse_body_weight(body_weight_text)

        if body_weight is not None:
            body_weight_log = BodyWeightLog(
                date=workout_date,
                body_weight=body_weight
            )
            body_weight_manager.save(body_weight_log)

        exercise_for_sets = request.form.getlist('exercise_for_set[]')
        weights = request.form.getlist('weight[]')
        reps = request.form.getlist('reps[]')


        set_counts = {}
        for i in range(len(weights)):
            if (
                 weights[i] == '' or reps[i] == '' or exercise_for_sets[i].strip() == ''
            ):
                continue

            exercise = exercise_for_sets[i]

            if exercise not in set_counts:
                set_counts[exercise] = 1
            else:
                set_counts[exercise] += 1

            log = WorkoutLog(date=workout_date,
                             body_weight=body_weight,
                             exercise=exercise,
                             weight=float(weights[i]), 
                             reps=int(reps[i]),
                             sets=set_counts[exercise]
            )
            manager.add(log)

        cardio_machine = request.form.get('cardio_machine')
        cardio_mins = request.form.get('cardio_mins')

        if cardio_mins:
            cardio_log = CardioLog(
                machine=cardio_machine or "未指定",
                mins=int(cardio_mins),
                date=workout_date
            )
            cardio_manager.add(cardio_log)

        return redirect(url_for('index'))
    selected_date = request.args.get('date')

    exercise_options, cardio_options = get_input_options()

    return render_template('add.html', date=selected_date, exercise_options=exercise_options, cardio_options=cardio_options, active_page='index')


@app.route('/update_by_date/<date>', methods=['GET', 'POST'])
def update_by_date(date):
    if request.method == 'POST':
        body_weight_text = request.form.get('body_weight')
        body_weight = parse_body_weight(body_weight_text)
        
        exercise_for_sets = request.form.getlist('exercise_for_set[]')
        weights = request.form.getlist('weight[]')
        reps = request.form.getlist('reps[]')

        if body_weight is not None:
            body_weight_log = BodyWeightLog(
                date=date,
                body_weight=body_weight
            )
            body_weight_manager.save(body_weight_log)
        else:
            body_weight_manager.delete_by_date(date)

        manager.delete_by_date(date)
        cardio_manager.delete_by_date(date)

        set_counts = {}
        for i in range(len(weights)):
            if (
                 weights[i] == '' or reps[i] == '' or exercise_for_sets[i].strip() == ''
            ):
                continue

            exercise = exercise_for_sets[i]

            if exercise not in set_counts:
                set_counts[exercise] = 1
            else:
                set_counts[exercise] += 1

            log = WorkoutLog(
                date=date,
                body_weight=body_weight,
                exercise=exercise,
                weight=float(weights[i]),
                reps=int(reps[i]),
                sets=set_counts[exercise]
            )
            manager.add(log)

        cardio_machine = request.form.get('cardio_machine')
        cardio_mins = request.form.get('cardio_mins')

        if cardio_mins:
            cardio_log =CardioLog(
                machine=cardio_machine or "未指定",
                mins=int(cardio_mins),
                date=date,
            )
            cardio_manager.add(cardio_log)

        return redirect(url_for('index'))

    logs = manager.get_by_date(date)
    cardio_logs = cardio_manager.get_by_date(date)

    body_weight_log = body_weight_manager.get_by_date(date)

    if body_weight_log:
        body_weight = body_weight_log[2]
    else:
        body_weight = ''

    exercise_options, cardio_options = get_input_options()

    grouped_logs = {}
    for log in logs:
        exercise = log[3]

        if exercise not in grouped_logs:
            grouped_logs[exercise] = []

        grouped_logs[exercise].append(log)

    return render_template(
        'update.html',
        date=date,
        body_weight=body_weight,
        grouped_logs=grouped_logs,
        cardio_logs=cardio_logs,
        exercise_options=exercise_options,
        cardio_options=cardio_options
    )


@app.route('/delete_by_date/<date>', methods=['POST'])
def delete_by_date(date):
    manager.delete_by_date(date)
    cardio_manager.delete_by_date(date)
    body_weight_manager.delete_by_date(date)

    return redirect(url_for('index'))

def get_body_weight_graph_data(selected_days):
    body_weight_logs = body_weight_manager.get_all()
    body_weight_by_date = {}
    for body_weight_log in body_weight_logs:
        date = body_weight_log[1]
        body_weight = body_weight_log[2]

        if date and date != 'None' and body_weight is not None:
            body_weight_by_date[date] = body_weight

    graph_dates = [
        (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(selected_days -1, -1, -1)
    ]

    graph_labels = []
    body_weights = []
    last_weight = None

    for date in graph_dates:
        if date in body_weight_by_date:
            last_weight = body_weight_by_date[date]

        graph_labels.append(
            datetime.strptime(date, "%Y-%m-%d").strftime("%m/%d")
        )

        body_weights.append(last_weight)
    return graph_labels, body_weights

def get_cardio_graph_data(selected_year, selected_half):
    cardio_logs = cardio_manager.get_all()
    cardio_by_month = {}

    for cardio_log in cardio_logs:
        date = cardio_log[1]
        mins = cardio_log[3]
        if not date or date == 'None':
            continue

        month = date[:7]

        if month not in cardio_by_month:
            cardio_by_month[month] = 0

        cardio_by_month[month] += mins
    
    if selected_half == 1:
        start_month = 1
    else:
        start_month = 7

    cardio_months = []

    for month_number in range(start_month, start_month + 6):
        cardio_months.append(
            f"{selected_year}-{month_number:02d}"
        )

    cardio_month_labels = [
        datetime.strptime(month, "%Y-%m").strftime("%m月")
        for month in cardio_months
    ]
    
    cardio_minutes = [
        cardio_by_month.get(month, 0)
        for month in cardio_months
    ]

    return cardio_month_labels, cardio_minutes

@app.route('/graph')
def graph():
    current_year = datetime.now().year
    current_month = datetime.now().month

    selected_year = request.args.get(
        'year',
        default=current_year,
        type=int
    )

    selected_half = request.args.get(
        'half',
        default=1 if current_month <= 6 else 2,
        type=int
    )

    selected_days = request.args.get(
        'days',
        default=30,
        type=int
    )
    graph_labels, body_weights = get_body_weight_graph_data(
        selected_days
    )

    cardio_month_labels, cardio_minutes = get_cardio_graph_data(
        selected_year,
        selected_half
    )

    return render_template(
        'graph.html',
        graph_labels=graph_labels,
        body_weights=body_weights,
        cardio_months=cardio_month_labels,
        cardio_minutes=cardio_minutes,
        current_year=current_year,
        selected_year=selected_year,
        selected_half=selected_half,
        selected_days=selected_days,
        active_page='graph'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)