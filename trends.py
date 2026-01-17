import io
import base64
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prophet import Prophet
from config import create_connection


def create_prophet_model_and_forecast(df, column_name, periods=10):
    df = df[['date_value', column_name]].rename(columns={'date_value': 'ds', column_name: 'y'})
    model = Prophet(daily_seasonality=True, yearly_seasonality=False)
    model.fit(df)
    future = model.make_future_dataframe(periods=periods)
    return model.predict(future)


def create_bar_plot(forecast):
    days = forecast['ds'].dt.strftime('%A').tolist()
    weekly_pattern = forecast['weekly'].tolist()

    cumulative = {d: 0 for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']}
    counts = {d: 0 for d in cumulative}

    for i, day in enumerate(days):
        cumulative[day] += weekly_pattern[i]
        counts[day] += 1

    avg = {d: (cumulative[d] / counts[d]) if counts[d] else 0 for d in cumulative}
    ordered = {d: avg[d] for d in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']}

    plt.figure(figsize=(8, 8))
    plt.bar(ordered.keys(), ordered.values(), color='#3a3a3a')
    plt.xticks(rotation=45)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return [base64.b64encode(buffer.getvalue()).decode('utf-8')]


def trend_plot_for_user(user_id, column_name):
    conn = create_connection()
    query = f"""
        SELECT date_value, {column_name}
        FROM "public"."Daily"
        WHERE id = %s
        ORDER BY date_value;
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()

    df.dropna(subset=['date_value', column_name], inplace=True)
    forecast = create_prophet_model_and_forecast(df, column_name)
    return create_bar_plot(forecast)


def takehome_trend(user_id):
    return trend_plot_for_user(user_id, 'take_home_earnings')


def hourly_rate_trend(user_id):
    return trend_plot_for_user(user_id, 'per_hour_rate')


def mile_rate_trend(user_id):
    return trend_plot_for_user(user_id, 'per_mile_rate')


def hours_rate_trend(user_id):
    return trend_plot_for_user(user_id, 'hours')


def get_forecast(user_id):
    conn = create_connection()
    query = """
        SELECT date_value, take_home_earnings
        FROM "public"."Daily"
        WHERE id = %s
        ORDER BY date_value;
    """
    df = pd.read_sql(query, conn, params=(user_id,))
    conn.close()

    df.dropna(subset=['date_value', 'take_home_earnings'], inplace=True)
    forecast = create_prophet_model_and_forecast(df, 'take_home_earnings')

    trend_values = forecast['trend'].tolist()
    overall_trend = "Trend: Increasing" if trend_values[-1] > trend_values[0] else "Trend: Decreasing"

    future_dates = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)
    forecast_list = []
    for _, row in future_dates.iterrows():
        predicted = row['yhat']
        low = row['yhat_lower']
        high = row['yhat_upper']
        confidence_percentage = (1 - (predicted - low) / (high - low)) * 100 if (high - low) else 0

        forecast_list.append({
            'date': row['ds'].strftime('%Y-%m-%d'),
            'day_of_week': row['ds'].strftime('%A'),
            'predicted_value': predicted,
            'lower_bound': low,
            'upper_bound': high,
            'confidence_percentage': confidence_percentage
        })

    return forecast_list, overall_trend
