# Employee Leave Management

A Flask leave-management demo for employees to apply for leave and check their
balances, and for managers to approve or reject leave requests.

## Run locally

Install dependencies and start the application:

```powershell
python -m pip install -r requirements-dev.txt
python app.py
```

Open `http://127.0.0.1:5000`. The demo login is `demo` / `leave123`; configure
`DEMO_USERNAME` and `DEMO_PASSWORD` to change it. Demo credentials and the
development server are not intended for production.

The leave-management API is available at `/api`:

| Action | Endpoint |
|---|---|
| Check an employee's balance | `GET /api/leave-balance?employee_id=demo` |
| Apply for leave | `POST /api/leave-requests` |
| List leave requests | `GET /api/leave-requests?employee_id=demo` |
| Approve or reject a request | `POST /api/leave-requests/<id>/decision` |

Example request to apply:

```json
{
  "employee_id": "demo",
  "requested_days": 3,
  "reason": "Personal leave"
}
```

Use `{"decision": "approved"}` or `{"decision": "rejected"}` to decide a pending
request. Pending requests reserve days against the available balance; rejected
requests release those days. This demo keeps requests in memory, so they reset when
the application restarts. Manager approval endpoints are demonstration-only and
are not protected by production authorization.

## Tests and CI

Run the unit and API tests with `python -m pytest -q`. The standalone Selenium login
check requires Chrome and a running application; run `python selenium_login.py`.
Set `APP_URL` when the application is hosted at a different address.

The GitHub Actions workflow runs the leave application/approval smoke check and
pytest on each push to `main`.

## Docker

```powershell
docker build -t leave-management .
docker run -d --name leave-management -p 5001:5000 leave-management
docker ps
docker inspect leave-management
docker logs leave-management
```

Open `http://127.0.0.1:5001`; the container listens on port `5000`. In the
`-p 5001:5000` mapping, the first port is the host port. Use `5001` in the browser,
not `5000` (which may belong to another application already running on your machine).
If the page displays an API/JSON error, reload the correct address and confirm the
container is running with `docker ps`.

## Jira backlog

`jira/backlog.csv` contains the three leave-management stories: apply for leave,
approve or reject leave, and check leave balance. It includes priorities, story
points, and sample workflow statuses for import into a Jira Scrum project.

## GitHub Actions CI/CD

The workflow at `.github/workflows/ci.yml` runs the leave-management smoke check,
pytest suite, and Docker image build for pull requests and pushes to `main`. On a
push to `main`, it also publishes `ghcr.io/<owner>/<repository>:latest` and a
commit-SHA-tagged image to GitHub Container Registry using the built-in
`GITHUB_TOKEN`. Ensure Actions is allowed to write packages in the repository
settings. After the first successful main-branch run, the published image can be
started with:

```powershell
docker run -d --name leave-management -p 5001:5000 ghcr.io/<owner>/<repository>:latest
```
