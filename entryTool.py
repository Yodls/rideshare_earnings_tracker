from flask import render_template, request
from flask_login import login_required, current_user
from config import app, load_user, create_connection
from datetime import date, timedelta, datetime

# Get the current date
current_date = date.today()

# Subtract a day from the current date
previous_date = current_date - timedelta(days=1)


#Daily Entry Tab
@app.route('/daily', methods=['GET', 'POST'])
@login_required
def daily():
    if request.method == 'POST':
        # Process the data for the daily page
        prompt_date = request.form['prompt_date']
        TE = float(request.form['TE'])
        GA = float(request.form['GA'])
        TM = float(request.form['TM'])
        H = float(request.form['H'])
        
        # Check for division by zero
        if H == 0 or TM == 0:
            return "Error: Hours and TM should be non-zero values."

        TH = TE - ((GA/25) * TM)
        THH = TH/H
        THTM = TH/TM
        
        user_id = current_user.id

        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO "public"."Daily"
            (id, date_value, gross_earnings, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate, gas_average) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, prompt_date, TE, TH, TM, H, THTM, THH, GA)
        )
                       
        conn.commit()
        cursor.close()
        conn.close()

        processed_data = {
            'prompt_date': prompt_date,
            'TE': round(TE, 2),
            'TH': round(TH, 2),
            'TM': round(TM, 2),
            'H': round(H, 2),
            'THH': round(THH, 2),
            'THTM': round(THTM, 2)
        }
                
            
        return render_template('daily.html', data=processed_data)
    
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username

    return render_template('daily.html', username=username)



@app.route('/weekly', methods=['GET', 'POST'])
@login_required
def weekly():
    if request.method == 'POST':
        # Process the data for the daily page
        week_number = request.form['week_number']
        my_reference = request.form['my_reference']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        Insurance = request.form['Insurance']

        user_id = current_user.id

        conn = create_connection()
        cursor = conn.cursor()
        query = f"""
        SELECT take_home_earnings, miles, hours
        FROM "public"."Daily"
        WHERE date_value >= '{start_date}' AND date_value <= '{end_date}'
        AND id = %s;  -- Add a condition to fetch data for the current user only
        """
        
        cursor.execute(query, (user_id,))
        take_home_earnings_list = []
        miles_list = []
        hours_list = []
        
        for row in cursor.fetchall():
            take_home_earnings, miles, hours = row
            take_home_earnings_list.append(take_home_earnings)
            miles_list.append(miles)
            hours_list.append(hours)
             
        first_gross_earnings = take_home_earnings_list[0]
        first_miles = miles_list[0]
        first_hours = hours_list[0]
        
        TH = float(sum(take_home_earnings_list))
        H = float(sum(hours_list))
        TM = float(sum(miles_list))
        I = float(Insurance * 10)
        THH = TH / H
        THTM = TH / TM
        
        cursor.execute(
        """
        INSERT INTO "public"."Weekly"
        (id, week_number, my_reference, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        (user_id, week_number, my_reference, TH, TM, H, THTM, THH)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        processed_data = {
            'TH': round(TH, 2),
            'TM': round(TM, 2),
            'H': round(H, 2),
            'THH': round(THH, 2),
            'THTM': round(THTM, 2)
        }                 
        
        return render_template('weekly.html', data=processed_data)
    
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username

    return render_template('weekly.html', username=username)


@app.route('/autoweekly', methods=['GET', 'POST'])
@login_required
def autoWeekly():
    if request.method == 'GET':
        current_date = datetime.today()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        reference_start = start_of_week.strftime("%b%d")
        reference_end = end_of_week.strftime("%b%d")
        my_reference = f"{reference_start}-{reference_end}"
        start_date = current_date - timedelta(days=8)
        end_date = current_date - timedelta(days=1)


        user_id = current_user.id

        conn = create_connection()
        cursor = conn.cursor()

        query2 = f"""
        SELECT MAX(week_number)
        FROM "public"."Weekly"
        WHERE id = %s;
        """
        cursor.execute(query2, (user_id,))
        result2 = cursor.fetchone()
        week_number = (result2[0] if result2[0] is not None else 0) + 1

        query = """
        SELECT take_home_earnings, miles, hours
        FROM "public"."Daily"
        WHERE date_value::date >= %s AND date_value::date <= %s
        AND id = %s; 
        """
        cursor.execute(query, (start_date.date(), end_date.date(), user_id))
        results = cursor.fetchall()
        Insurance = len(results)
        take_home_earnings_list = []
        miles_list = []
        hours_list = []

        for row in results:
            take_home_earnings, miles, hours = row
            take_home_earnings_list.append(take_home_earnings)
            miles_list.append(miles)
            hours_list.append(hours)

        TH = sum(take_home_earnings_list)
        H = sum(hours_list)
        TM = sum(miles_list)
        I = Insurance * 10
        THH = TH / H if H else 0
        THTM = TH / TM if TM else 0

        cursor.execute(
        """
        INSERT INTO "public"."Weekly"
        (id, week_number, my_reference, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, 
        (user_id, week_number, my_reference, TH, TM, H, THTM, THH)
        )

        conn.commit()
        cursor.close()
        conn.close()

        processed_data = {
            'TH': round(TH, 2),
            'TM': round(TM, 2),
            'H': round(H, 2),
            'THH': round(THH, 2),
            'THTM': round(THTM, 2)
        }                 

        return render_template('weekly.html', data=processed_data)

    user_id = current_user.get_id()  # Note: You need to define 'load_user' function elsewhere in your code
    user = load_user(user_id)
    username = user.username

    return render_template('weekly.html', username=username)

@app.route('/monthly', methods=['GET', 'POST'])
@login_required
def monthly():
    if request.method == 'POST':
        prompt_date = request.form['prompt_date']
        my_reference = request.form['my_reference']
        Expenses = request.form['Expenses']
        start_week_number = request.form['start_week_number']
        end_week_number = request.form['end_week_number']

        user_id = current_user.id

        conn = create_connection()
        cursor = conn.cursor()

        # Select data from the "Weekly" table
        select_query = f"""
        SELECT take_home_earnings, miles, hours
        FROM Weekly
        WHERE week_number >= {start_week_number} AND week_number <= {end_week_number}
        AND id = ?; -- Add a condition to fetch data for the current user only
        """

        cursor.execute(select_query, (user_id,))
        take_home_earnings_list = []
        miles_list = []
        hours_list = []

        for row in cursor.fetchall():
            take_home_earnings, miles, hours = row
            take_home_earnings_list.append(take_home_earnings)
            miles_list.append(miles)
            hours_list.append(hours)
        
        TH = sum(take_home_earnings_list)
        TM = sum(miles_list)
        H = sum(hours_list)
        
        TH = float(TH)
        TM = float(TM)
        H = float(H)
        Expenses =float(Expenses)
        
        THE = TH - Expenses
        THH = THE/H
        THTM = THE/TM

        insert_query = """
        INSERT INTO Monthly 
        (id, month_prompt, my_reference, take_home_earnings, expenses, real_take_home_after_expenses, miles, hours, per_mile_rate, per_hour_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (user_id, prompt_date, my_reference, TH, Expenses, THE, TM, H, THTM, THH))
        conn.commit()
        cursor.close()
        conn.close()       
        
        processed_data = {
            'TH': round(TH, 2),
            'TM': round(TM, 2),
            'H': round(H, 2),
            'THH': round(THH, 2),
            'THTM': round(THTM, 2)
        }      
        
        return render_template('monthly.html', data=processed_data)
    
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    return render_template('monthly.html', username=username)