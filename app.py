#configurational imports

from flask import render_template
from flask_login import login_required, current_user
from config import app, load_user

#flask route imports
from reportsPage import visual
from entryTool import daily, weekly, monthly
from dbtables import daily_table, weekly_table, monthly_table
from login_logout_register import register, login, logout

#Dashbaord route
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.get_id()
    user = load_user(user_id)
    username = user.username
    return render_template('base.html', username=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
