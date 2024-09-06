from flask import redirect, render_template, request, session
from functools import wraps

def apology(message, code=400):
    """Render Apology Message"""

    def escape(s):
        """Escape Special Characters"""

        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """Decorate Routes To Require Login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def php(value):
    """Format Value As Philippine Peso"""
    if value is None:
        return "₱ 0.00"
    return f"₱ {value:,.2f}"
