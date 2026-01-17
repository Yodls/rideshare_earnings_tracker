from datetime import datetime, timedelta
from config import create_connection
import psycopg2

def get_user_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")  # Adjust SQL query to match your database structure
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return user_ids

def auto_weekly_for_user(user_id, conn):
    cursor = conn.cursor()
    
    # Date and reference calculations
    current_date = datetime.today()
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    reference_start = start_of_week.strftime("%b%d")
    reference_end = end_of_week.strftime("%b%d")
    my_reference = f"{reference_start}-{reference_end}"
    start_date = current_date - timedelta(days=8)
    end_date = current_date - timedelta(days=1)
    
    # Get the maximum week number
    query2 = f"""
    SELECT MAX(week_number)
    FROM "public"."Weekly"
    WHERE id = %s;
    """
    cursor.execute(query2, (user_id,))
    result2 = cursor.fetchone()
    week_number = (result2[0] if result2[0] is not None else 0) + 1

    # Get the daily data for the specified date range
    query = """
    SELECT take_home_earnings, miles, hours
    FROM "public"."Daily"
    WHERE date_value >= %s AND date_value <= %s
    AND id = %s; 
    """
    cursor.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), user_id))
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

    # Calculate the summary statistics
    TH = sum(take_home_earnings_list)
    H = sum(hours_list)
    TM = sum(miles_list)
    I = Insurance * 10
    THH = TH / H if H else 0
    THTM = TH / TM if TM else 0

    # Insert the new weekly data
    cursor.execute(
    """
    INSERT INTO "public"."Weekly"
    (id, week_number, my_reference, take_home_earnings, miles, hours, per_mile_rate, per_hour_rate) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, 
    (user_id, week_number, my_reference, TH, TM, H, THTM, THH)
    )

    # Commit the transaction
    conn.commit()
    cursor.close()

def main():
    conn = create_connection()
    
    user_ids = get_user_ids(conn)
    
    for user_id in user_ids:
        auto_weekly_for_user(user_id, conn)
    
    conn.close()

if __name__ == "__main__":
    main()
