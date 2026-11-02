import hmac
import os

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from order_total import calculate_order_total

app = Flask(__name__)

LOGIN_PAGE = """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Food Ordering Login</title></head>
  <body>
    <h1>Food Ordering Login</h1>
    {% if error %}<p role="alert">{{ error }}</p>{% endif %}
    <form method="post">
      <label>Username <input name="username" autocomplete="username"></label>
      <label>Password <input name="password" type="password" autocomplete="current-password"></label>
      <button type="submit">Log in</button>
    </form>
  </body>
</html>"""


@app.get("/")
def home():
    return jsonify(
        service="food-ordering-demo",
        order_total_endpoint="/api/order-total",
        login_page="/login",
    )


@app.post("/api/order-total")
def order_total():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Expected a JSON object"), 400
    try:
        total = calculate_order_total(
            data.get("subtotal"), data.get("discount_percent", 0)
        )
    except ValueError as error:
        return jsonify(error=str(error)), 400
    return jsonify(total=total)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_PAGE, error=None)

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    expected_username = os.environ.get("DEMO_USERNAME", "demo")
    expected_password = os.environ.get("DEMO_PASSWORD", "food123")

    if hmac.compare_digest(username, expected_username) and hmac.compare_digest(
        password, expected_password
    ):
        return redirect(url_for("dashboard"))
    return render_template_string(LOGIN_PAGE, error="Invalid username or password"), 401


@app.get("/dashboard")
def dashboard():
    return "<h1>Welcome to your food ordering account</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
