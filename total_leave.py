from threading import Lock

from leave_balance import validate_leave_request


class LeaveManagement:
    def __init__(self, default_balance=20):
        if isinstance(default_balance, bool) or not isinstance(default_balance, int):
            raise ValueError("Default leave balance must be a whole number")
        if default_balance < 0:
            raise ValueError("Default leave balance cannot be negative")
        self.default_balance = default_balance
        self._requests = {}
        self._next_id = 1
        self._lock = Lock()

    @staticmethod
    def _validate_employee_id(employee_id):
        if not isinstance(employee_id, str) or not employee_id.strip():
            raise ValueError("employee_id must be a non-empty string")
        if len(employee_id) > 80:
            raise ValueError("employee_id must be 80 characters or fewer")
        return employee_id.strip()

    def balance(self, employee_id):
        employee_id = self._validate_employee_id(employee_id)
        with self._lock:
            employee_requests = [
                item
                for item in self._requests.values()
                if item["employee_id"] == employee_id
            ]
            approved_days = sum(
                item["requested_days"]
                for item in employee_requests
                if item["status"] == "approved"
            )
            pending_days = sum(
                item["requested_days"]
                for item in employee_requests
                if item["status"] == "pending"
            )
            return {
                "total_days": self.default_balance,
                "approved_days": approved_days,
                "pending_days": pending_days,
                "available_days": self.default_balance - approved_days - pending_days,
            }

    def apply(self, employee_id, requested_days, reason):
        employee_id = self._validate_employee_id(employee_id)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        if len(reason.strip()) > 500:
            raise ValueError("reason must be 500 characters or fewer")

        with self._lock:
            employee_requests = [
                item
                for item in self._requests.values()
                if item["employee_id"] == employee_id
            ]
            approved_days = sum(
                item["requested_days"]
                for item in employee_requests
                if item["status"] == "approved"
            )
            pending_days = sum(
                item["requested_days"]
                for item in employee_requests
                if item["status"] == "pending"
            )
            available_days = self.default_balance - approved_days - pending_days
            validate_leave_request(available_days, requested_days)
            leave_request = {
                "id": self._next_id,
                "employee_id": employee_id,
                "requested_days": requested_days,
                "reason": reason.strip(),
                "status": "pending",
            }
            self._requests[self._next_id] = leave_request
            self._next_id += 1
            return leave_request.copy()

    def list_requests(self, employee_id=None):
        if employee_id is not None:
            employee_id = self._validate_employee_id(employee_id)
        with self._lock:
            return [
                item.copy()
                for item in self._requests.values()
                if employee_id is None or item["employee_id"] == employee_id
            ]

    def decide(self, request_id, decision):
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be 'approved' or 'rejected'")
        with self._lock:
            leave_request = self._requests.get(request_id)
            if leave_request is None:
                raise LookupError("Leave request not found")
            if leave_request["status"] != "pending":
                raise ValueError("Only pending requests can be decided")
            leave_request["status"] = decision
            return leave_request.copy()


if __name__ == "__main__":
    manager = LeaveManagement()
    request = manager.apply("demo", 3, "Personal leave")
    manager.decide(request["id"], "approved")
    print(f"Available leave: {manager.balance('demo')['available_days']} days")
