# Food Ordering Demo

A small Flask application used to demonstrate order totals, a containerized Python
service, automated tests, and a GitHub Actions workflow.

Run locally with `python -m pip install -r requirements-dev.txt` followed by
`python app.py`. The application listens on `http://127.0.0.1:5000`. Sample login
credentials are `demo` / `food123`; override them with `DEMO_USERNAME` and
`DEMO_PASSWORD` environment variables. These defaults are for local demonstration
only, not production authentication.

Calculate a sample order (`$50` with a `10%` discount) with `python order_total.py`.
The GitHub Actions workflow at `.github/workflows/ci.yml` runs this command and the
pytest suite on each push to `main`.

Run tests with `python -m pytest -q`. The Selenium login test uses an installed
Chrome browser and driver; start the app first, then run
`python selenium_login_test.py`. Set `APP_URL` if the app runs elsewhere.

Build and run the container with:

```powershell
docker build -t food-ordering-demo .
docker run -d --name food-ordering-demo -p 5000:5000 food-ordering-demo
docker ps
docker inspect food-ordering-demo
docker logs food-ordering-demo
```

`jira/backlog.csv` is a Jira CSV-import-ready backlog with three stories, priorities,
story points, and example workflow statuses. Create a company-managed Scrum project
in Jira, then import this CSV through Jira's external system import flow and map
`Story point estimate` and `Status` to the corresponding Jira fields. The statuses
are sample states and must exist in the project's workflow.

The requested feature branch is named `leavebalance-validation`; Git does not allow
spaces in branch names. It adds validation that a leave request is positive and
does not exceed the available balance.
