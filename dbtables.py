from flask import render_template
from flask_login import login_required, current_user
from config import app, load_user, create_connection

@app.route('/daily_table')
@login_required
def daily_table():
    id = current_user.id
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        SELECT date_value, gross_earnings, take_home_earnings, miles, hours, 
            per_mile_rate, per_hour_rate, gas_average
        FROM "public"."Daily" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in result]
    return render_template('dbtables.html', data=data, columns=columns, username=username)

@app.route('/weekly_table')
@login_required
def weekly_table():
    id = current_user.id
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        SELECT week_number, my_reference, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate
        FROM "public"."Weekly" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in result]
    return render_template('dbtables.html', data=data, columns=columns, username=username)

@app.route('/monthly_table')
@login_required
def monthly_table():
    id = current_user.id
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    conn = create_connection()
    cursor = conn.cursor()
    query = """
        SELECT month_prompt, my_reference, take_home_earnings, expenses, real_take_home_after_expenses, miles, hours, per_mile_rate, per_hour_rate
        FROM "public"."Monthly" WHERE id = %s;
    """
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in result]
    return render_template('dbtables.html', data=data, columns=columns, username=username)
