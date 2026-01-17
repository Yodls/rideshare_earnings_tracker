from flask import render_template
from flask_login import login_required, current_user
from datetime import datetime
import pandas as pd
import datetime
from plots import dailyPlot, weeklyPlot, monthlyPlot
from config import app, create_connection, load_user
from trends import (
    get_forecast,
    takehome_trend,
    hourly_rate_trend,
    mile_rate_trend,
    hours_rate_trend,
)

#Visual Refresh
@app.route('/visual')
@login_required
def visual():

    id = current_user.id
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    conn = create_connection()


    forecast_list, overall_trend = get_forecast(user_id)
    takeHome = takehome_trend(user_id)
    hourly = hourly_rate_trend(user_id)
    miles = mile_rate_trend(user_id)
    hours = hours_rate_trend(user_id)


    #Daily Database Query (With Predictions)
    current_date = datetime.datetime.now() - datetime.timedelta(days=1)
    formatted_current_date = current_date.strftime("%y-%m-%d")
    query = """
        SELECT take_home_earnings, miles, hours, gas_average, per_mile_rate, per_hour_rate
        FROM (
            SELECT * 
            FROM "public"."Daily"
            WHERE id = %s AND date_value < %s 
            ORDER BY date_value DESC 
            LIMIT 10
        ) sub;
    """

    params = (id, formatted_current_date)
    df = pd.read_sql(query, conn, params=params)
    Per_Hour_d = round(df['per_hour_rate'].mean(skipna=True), 2)
    per_mile_d = round(df['per_mile_rate'].mean(skipna=True), 2)
    real_take_home_d = round(df['take_home_earnings'].mean(skipna=True), 2)
    miles_d = round(df['miles'].mean(skipna=True), 2)
    hours_d = round(df['hours'].mean(skipna=True), 2)
    GA_d = round(df['gas_average'].mean(skipna=True), 3)
    GAV_d = round(((GA_d/25) * miles_d))
    

    #Weekly Database Query
    query2 = """
        SELECT gas_average
        FROM (
            SELECT * 
            FROM "public"."Daily" 
            WHERE id = %s AND date_value < %s 
            ORDER BY date_value DESC 
            LIMIT 30
        ) sub;
    """

    params = (id, formatted_current_date)

    df2 = pd.read_sql(query2, conn, params=params)

    query = """
        SELECT * 
        FROM "public"."Weekly"
        WHERE id = %s 
        ORDER BY week_number DESC 
        LIMIT 4;
    """

    params = (id,)

    df = pd.read_sql(query, conn, params=params)

    Per_Hour_w = str(round(df['per_hour_rate'].mean(), 2))
    per_mile_w = str(round(df['per_mile_rate'].mean(), 2))
    real_take_home_w = str(round(df['take_home_earnings'].mean(), 2))
    miles_w = round(df['miles'].mean(), 2)
    hours_w = str(round(df['hours'].mean(), 2))
    GA_w = round(df2['gas_average'].mean(skipna=True), 3)
    GAV_w = round(((GA_w/25) * miles_w))

    #Monthly Database Query
    query3 = """
        SELECT gas_average
        FROM (
            SELECT * 
            FROM "public"."Daily"
            WHERE id = %s AND date_value < %s 
            ORDER BY date_value DESC 
            LIMIT 30
        ) sub;
    """

    params = (id, formatted_current_date)

    df3 = pd.read_sql(query3, conn, params=params)

    query = """
        SELECT * 
        FROM "public"."Monthly"
        WHERE id = %s;
    """

    params = (id,)

    df = pd.read_sql(query, conn, params=params)

    cols_to_convert = ['per_hour_rate', 'per_mile_rate', 'real_take_home_after_expenses', 'miles']
    df[cols_to_convert] = df[cols_to_convert].replace({'\$': '', ',': ''}, regex=True).astype(float)
    Per_Hour_m = str(round(df['per_hour_rate'].mean(), 2))
    per_mile_m = str(round(df['per_mile_rate'].mean(), 2))
    real_take_home_m = str(round(df['real_take_home_after_expenses'].mean(), 2))
    miles_m = round(df['miles'].mean(), 2)
    hours_m = round(df['hours'].mean(), 2)
    hours_m2 = hours_m / 4
    GA_m = round(df3['gas_average'].mean(skipna=True), 3)
    GAV_m = round(((GA_m/25) * miles_m))

    return render_template('visualization.html',
                active_page='visualization',
                username=username,
                overall_trend=overall_trend,
                forecast_list=forecast_list,
                takeHome=takeHome,
                hourly=hourly,
                miles=miles,
                hours=hours,
                Per_Hour_d=Per_Hour_d,
                per_mile_d=per_mile_d,
                real_take_home_d=real_take_home_d,
                miles_d=miles_d,
                hours_d=hours_d,
                GA_d=GA_d,
                GAV_d=GAV_d,
                Per_Hour_w=Per_Hour_w,
                Per_mile_w=per_mile_w,
                miles_w=miles_w,
                real_take_home_w=real_take_home_w,
                hours_w=hours_w,
                GA_w=GA_w, 
                GAV_w=GAV_w,
                Per_Hour_m=Per_Hour_m,
                Per_mile_m=per_mile_m,
                miles_m=miles_m,
                real_take_home_m=real_take_home_m,
                hours_m=hours_m,
                hours_m2=hours_m2,
                GA_m=GA_m,
                GAV_m=GAV_m)