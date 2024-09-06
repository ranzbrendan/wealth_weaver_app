import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# for data viz purposes
import pandas as pd

# using dash
#from dash import Dash, html, dcc, Input, Output
#import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.io as pio

from helpers import apology, login_required, php

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["php"] = php

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    """Show Homepage"""

    if session.get("user_id") is None:
        return render_template("index.html")

    else:
        account = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        name = account[0]["username"]
        balance = account[0]["cash"]

        if len(db.execute("SELECT * FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'", session["user_id"])) != 0:

            today = db.execute("""
                            SELECT SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses' AND transaction_datetime = date('now')
                            """, session["user_id"]
                            )[0]["sum"]
            this_week = db.execute("""
                                SELECT SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses' AND
                                (transaction_datetime BETWEEN date(date('now'), '-6 day') AND date('now'))
                                """, session["user_id"]
                                )[0]["sum"]
            last_month = db.execute("""
                                    SELECT SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses' AND
                                    strftime('%Y-%m', transaction_datetime) = strftime('%Y-%m', date(date('now'), '-1 month'))
                                    """, session["user_id"]
                                    )[0]["sum"]
            ave_monthly = db.execute("""
                                    SELECT AVG(sum) AS avg FROM
                                    (SELECT strftime('%Y-%m', transaction_datetime) AS year_month,  SUM(amount) AS sum FROM transactions WHERE id_user = ? AND
                                    transaction_type = 'Expenses' AND strftime('%Y-%m', transaction_datetime) <> strftime('%Y-%m', date('now'))
                                    GROUP BY strftime('%Y-%m', transaction_datetime))
                                    """, session["user_id"]
                                    )[0]["avg"]

            if session.get("graph_data") is None or session.get("graph_selected") is None:
                return redirect("/select_graph")

            df = session["graph_data"]
            graph_selected = session["graph_selected"]

            fig = px.line(df, x="date", y="sum", markers=True, height=350, template="none")
            graph_json = pio.to_json(fig)

        else:
            today = 0
            this_week = 0
            last_month = 0
            ave_monthly = 0
            graph_selected = 'none'
            fig = px.scatter()
            graph_json = pio.to_json(fig)

        return render_template("dashboard.html", name=name, balance=balance, today=today, this_week=this_week, last_month=last_month, ave_monthly=ave_monthly, graph_json=graph_json, graph_selected=graph_selected)

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    # via post
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password")

        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/")

    # via get
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    # via post
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # ensure fields have inputs
        if not username:
            return apology("must provide username", 404)
        elif not password:
            return apology("must provide password", 404)
        elif not confirmation:
            return apology("must provide confirmation", 404)
        # ensure passwords match
        elif password != confirmation:
            return apology("passwords do not match", 404)

        # check & insert to database
        try:
            # ensure username is unique
            if len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
                return apology("username already exists", 404)

            # insert to database
            hash = generate_password_hash(password)

            # log in user
            session["user_id"] = db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, hash)

            # redirect to homepage
            print("XD")
            return redirect("/")

        except (KeyError, IndexError, ValueError):
            return None

    # via get
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/transactions", methods=["POST", "GET"])
@login_required
def transaction():

    # clear the graph_data
    session.pop("graph_data", None)
    session.pop("graph_selected", None)

    def show_transaction(transaction_id):
        # delete categories for user which have not been used

        db.execute("""
            DELETE FROM categories WHERE id_user = ? AND category NOT IN (SELECT category FROM transactions WHERE id_user = ?)
        """, session["user_id"], session["user_id"])

        categories = db.execute("SELECT * FROM categories WHERE id_user = ?", session["user_id"])
        income = db.execute("SELECT * FROM transactions WHERE id_user = ? AND transaction_type = 'Income' ORDER BY transaction_datetime DESC", session["user_id"])
        expenses = db.execute("SELECT * FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses' ORDER BY transaction_datetime DESC", session["user_id"])
        income_sum = db.execute("SELECT COALESCE(SUM(amount), 0) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Income'", session["user_id"])
        expenses_sum = db.execute("SELECT COALESCE(SUM(amount), 0) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'", session["user_id"])
        balance = income_sum[0]["sum"] - expenses_sum[0]["sum"]

        # options to be selected
        if transaction_id != 0:
            previous_transaction = db.execute("SELECT * FROM transactions WHERE id_transaction = ? ", transaction_id)
            if len(previous_transaction) == 1:
                type_selected = previous_transaction[0]['transaction_type']
                category_selected = previous_transaction[0]['category']
            else:
                type_selected = 0
                category_selected = 0
        else:
            type_selected = 0
            category_selected = 0

        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, session["user_id"])

        return render_template("transactions.html", income=income, expenses=expenses, categories=categories, type_selected=type_selected, category_selected=category_selected)


    # via post
    if request.method == "POST":

        # via add transaction
        if request.form.get("form_id") == "add":
            transaction_type = request.form.get("transaction_type")
            category = request.form.get("category").capitalize()
            amount = float(request.form.get("amount"))
            transaction_date = request.form.get("transaction_date")
            description = request.form.get("description")

            if not description:
                description = "No Description"

            query = """
                INSERT INTO transactions (
                    id_user, transaction_type, category, amount, transaction_datetime, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            transaction_id = db.execute(query, session["user_id"], transaction_type, category, amount, transaction_date, description)

            session["transaction_id"] = transaction_id

            return redirect("/transactions")

        # via delete transaction
        elif request.form.get("form_id") == "delete":
            transaction_id = request.form.get("transaction_id")

            db.execute("DELETE FROM transactions WHERE id_transaction = ?", transaction_id)

            return redirect("/transactions")

    # via get
    else:
        if session.get("transaction_id") is None:
            return show_transaction(0)
        else:
            pti = session["transaction_id"]
            session.pop("transaction_id", None)
            return show_transaction(pti)

@app.route('/add_category', methods=["POST"])
def add_category():
    category = request.json['category']

    # Add new option to database

    category_id = db.execute("INSERT INTO categories (id_user, category) VALUES (?, ?)", session["user_id"], category.capitalize())

    return jsonify({'category_id': category_id})

@app.route('/set_min_amount', methods=["GET"])
@login_required
def set_min_amount():

    balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    return jsonify({'balance': balance})

@app.route('/change_username', methods=["POST"])
def change_username():
    username = request.json['username']

    # update username in database
    db.execute("UPDATE users SET username = ? WHERE id = ?", username, session["user_id"])

    return 'success', 200

@app.route('/change_password', methods=["POST"])
def change_password():
    matches = False
    correct = False

    current_password = request.json['currentPassword']
    new_password = request.json['newPassword']
    new_confirmation = request.json['newConfirmation']

    user_info_row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    if check_password_hash(user_info_row[0]["hash"], current_password):
        correct = True
        if new_password == new_confirmation:
            matches = True
            hash = generate_password_hash(new_password)
            # update password in database
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])

    print(matches)
    print(correct)

    return jsonify({'matches': matches, 'correct': correct})

@app.route("/select_graph", methods=["POST", "GET"])
def select_graph():

    # via post
    if request.method == "POST":
        selection = request.form.get("graph_option")

        if selection == 'daily':
            # Data be used for the graph
            daily_data = db.execute("""
                                    SELECT transaction_datetime AS date, SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'
                                    GROUP BY transaction_datetime ORDER BY date DESC LIMIT 15
                                    """, session["user_id"]
                                    )
            # Import to pandas dataframe
            df_daily = pd.DataFrame(daily_data)
            session["graph_data"] = df_daily
            session["graph_selected"] = selection
            return redirect("/")

        elif selection == 'weekly':
            # Data be used for the graph
            weekly_data = db.execute("""
                                    SELECT strftime('%W', transaction_datetime) AS date, SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'
                                    GROUP BY strftime('%W', transaction_datetime) ORDER BY date DESC LIMIT 15
                                    """, session["user_id"]
                                    )
            # Import to pandas dataframe
            df_weekly = pd.DataFrame(weekly_data)
            session["graph_data"] = df_weekly
            session["graph_selected"] = selection
            return redirect("/")

        elif selection == 'monthly':
            # Data be used for the graph
            monthly_data = db.execute("""
                                    SELECT strftime('%m', transaction_datetime) AS date, SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'
                                    GROUP BY strftime('%m', transaction_datetime) ORDER BY date DESC LIMIT 15
                                    """, session["user_id"]
                                    )
            # Import to pandas dataframe
            df_monthly = pd.DataFrame(monthly_data)
            session["graph_data"] = df_monthly
            session["graph_selected"] = selection
            return redirect("/")

        elif selection == 'yearly':
            # Data be used for the graph
            yearly_data = db.execute("""
                                    SELECT strftime('%Y', transaction_datetime) AS date, SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'
                                    GROUP BY strftime('%Y', transaction_datetime) ORDER BY date DESC LIMIT 15
                                    """, session["user_id"]
                                    )
            # Import to pandas dataframe
            df_yearly = pd.DataFrame(yearly_data)
            session["graph_data"] = df_yearly
            session["graph_selected"] = selection
            return redirect("/")

    else:
        # Data be used for the graph
        daily_data = db.execute("""
                                SELECT transaction_datetime AS date, SUM(amount) AS sum FROM transactions WHERE id_user = ? AND transaction_type = 'Expenses'
                                GROUP BY transaction_datetime ORDER BY date DESC LIMIT 15
                                 """, session["user_id"]
                                 )
        # Import to pandas dataframe
        df_daily = pd.DataFrame(daily_data)
        session["graph_data"] = df_daily
        session["graph_selected"] = 'daily'
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

