import hmac
import os

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

from total_leave import LeaveManagement

LOGIN_PAGE = """<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Employee Leave Management Login</title></head>
  <body>
    <h1>Employee Leave Management</h1>
    {% if error %}<p role="alert">{{ error }}</p>{% endif %}
    <form method="post">
      <label>Username <input name="username" autocomplete="username"></label>
      <label>Password <input name="password" type="password" autocomplete="current-password"></label>
      <button type="submit">Log in</button>
    </form>
  </body>
</html>"""

DASHBOARD = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Employee Leave Management</title>
  </head>
  <body>
    <h1>Employee Leave Management</h1>
    <section>
      <h2>Check leave balance</h2>
      <label>Employee ID <input id="employee-id" value="{{ employee_id }}"></label>
      <button id="refresh" type="button">Check balance and requests</button>
      <p id="balance" aria-live="polite"></p>
    </section>
    <section>
      <h2>Apply for leave</h2>
      <form id="apply-form">
        <label>Leave days <input name="requested_days" type="number" min="1" step="1" required></label>
        <label>Reason <input name="reason" required></label>
        <button type="submit">Submit leave request</button>
      </form>
      <p id="message" role="status"></p>
    </section>
    <section>
      <h2>Leave requests</h2>
      <ul id="requests"></ul>
    </section>
    <script>
      const employeeInput = document.getElementById("employee-id");
      const balanceOutput = document.getElementById("balance");
      const requestsList = document.getElementById("requests");
      const message = document.getElementById("message");

      async function send(url, options = {}) {
        const response = await fetch(url, options);
        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
          throw new Error(
            `API ${url} returned HTTP ${response.status} instead of JSON. ` +
            "Check that you opened the leave-management app on the correct port."
          );
        }
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Request failed");
        return data;
      }

      async function refresh() {
        const employeeId = encodeURIComponent(employeeInput.value);
        const balance = await send(`/api/leave-balance?employee_id=${employeeId}`);
        balanceOutput.textContent =
          `Available: ${balance.available_days} days; approved: ${balance.approved_days}; pending: ${balance.pending_days}`;
        const data = await send(`/api/leave-requests?employee_id=${employeeId}`);
        requestsList.replaceChildren();
        for (const leaveRequest of data.requests) {
          const item = document.createElement("li");
          item.textContent =
            `${leaveRequest.requested_days} day(s) - ${leaveRequest.reason} (${leaveRequest.status})`;
          if (leaveRequest.status === "pending") {
            for (const decision of ["approved", "rejected"]) {
              const button = document.createElement("button");
              button.type = "button";
              button.textContent = decision === "approved" ? "Approve" : "Reject";
              button.addEventListener("click", async () => {
                try {
                  await send(`/api/leave-requests/${leaveRequest.id}/decision`, {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({decision})
                  });
                  message.textContent = `Request ${decision}.`;
                  await refresh();
                } catch (error) {
                  message.textContent = error.message;
                }
              });
              item.append(" ", button);
            }
          }
          requestsList.append(item);
        }
      }

      document.getElementById("refresh").addEventListener("click", () => {
        refresh().catch(error => { message.textContent = error.message; });
      });
      document.getElementById("apply-form").addEventListener("submit", async event => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        try {
          await send("/api/leave-requests", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
              employee_id: employeeInput.value,
              requested_days: Number(formData.get("requested_days")),
              reason: formData.get("reason")
            })
          });
          event.currentTarget.reset();
          message.textContent = "Leave request submitted.";
          await refresh();
        } catch (error) {
          message.textContent = error.message;
        }
      });
      refresh().catch(error => { message.textContent = error.message; });
    </script>
  </body>
</html>"""


def create_app(leave_management=None):
    application = Flask(__name__)
    application.config["LEAVE_MANAGEMENT"] = leave_management or LeaveManagement()

    @application.get("/")
    @application.get("/dashboard")
    def dashboard():
        return render_template_string(
            DASHBOARD, employee_id=os.environ.get("DEMO_USERNAME", "demo")
        )

    @application.get("/login")
    @application.post("/login")
    def login():
        if request.method == "GET":
            return render_template_string(LOGIN_PAGE, error=None)

        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected_username = os.environ.get("DEMO_USERNAME", "demo")
        expected_password = os.environ.get("DEMO_PASSWORD", "leave123")

        if hmac.compare_digest(username, expected_username) and hmac.compare_digest(
            password, expected_password
        ):
            return redirect(url_for("dashboard"))
        return (
            render_template_string(
                LOGIN_PAGE, error="Invalid username or password"
            ),
            401,
        )

    @application.get("/api")
    def api_index():
        return jsonify(
            service="employee-leave-management",
            endpoints={
                "check_balance": "GET /api/leave-balance?employee_id=demo",
                "apply_for_leave": "POST /api/leave-requests",
                "list_requests": "GET /api/leave-requests",
                "approve_or_reject": "POST /api/leave-requests/<id>/decision",
            },
        )

    @application.get("/api/leave-balance")
    def leave_balance():
        employee_id = request.args.get("employee_id", "demo")
        try:
            balance = application.config["LEAVE_MANAGEMENT"].balance(employee_id)
        except ValueError as error:
            return jsonify(error=str(error)), 400
        return jsonify(employee_id=employee_id, **balance)

    @application.route("/api/leave-requests", methods=["GET", "POST"])
    def leave_requests():
        manager = application.config["LEAVE_MANAGEMENT"]
        if request.method == "GET":
            employee_id = request.args.get("employee_id")
            return jsonify(requests=manager.list_requests(employee_id))

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Expected a JSON object"), 400
        try:
            created = manager.apply(
                data.get("employee_id", "demo"),
                data.get("requested_days"),
                data.get("reason"),
            )
        except ValueError as error:
            return jsonify(error=str(error)), 400
        return jsonify(created), 201

    @application.post("/api/leave-requests/<int:request_id>/decision")
    def decide_leave(request_id):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Expected a JSON object"), 400
        try:
            updated = application.config["LEAVE_MANAGEMENT"].decide(
                request_id, data.get("decision")
            )
        except LookupError as error:
            return jsonify(error=str(error)), 404
        except ValueError as error:
            return jsonify(error=str(error)), 400
        return jsonify(updated)

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
