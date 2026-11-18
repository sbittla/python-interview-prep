"""
Exercise 02 — Design a custom exception hierarchy              [Tier: ★ Core]
Chapter 26 · Pattern: domain errors + translation at the boundary · Target time: 20 min

Problem
-------
Build a tiny in-memory user service whose errors form a hierarchy:

    AppError (code "APP", status 500)
    ├── ValidationError  (code "VALIDATION", status 400)
    ├── NotFoundError    (code "NOT_FOUND",  status 404)
    └── ConflictError    (code "CONFLICT",   status 409)

``AppError(message, *, details=None)`` stores ``details`` (a dict) and offers ``to_dict()``.
``UserService.create_user(username, email)`` validates input (username 3–20 chars of
``[a-z0-9_]``, email contains exactly one ``@`` with a dot after it) and refuses duplicates.
``UserService.get_user(username)`` raises ``NotFoundError`` for unknown users.

``handle(service, action, **kwargs)`` is the "HTTP boundary": it calls the service and returns
``{"status": 200, "data": ...}`` on success or ``{"status": <code>, "error": err.to_dict()}`` on an
``AppError``. Any other exception must propagate (it is a bug, not a client error).

Examples
--------
>>> svc = UserService()
>>> handle(svc, "create", username="ada", email="ada@example.com")["status"]
200
>>> handle(svc, "create", username="ada", email="ada@example.com")["error"]["code"]
'CONFLICT'

Constraints
-----------
- Callers must be able to catch every service error with one ``except AppError``.
- Do not compare error message strings to decide what happened.

Approach ladder
---------------
1. Brute force — raise ``Exception("user exists")`` and let the boundary parse the message. Brittle:
   rewording a message breaks the API.
2. Improved   — distinct classes per failure, but each handled by its own ``except`` clause at the
   boundary; adding a new error means editing every boundary.
3. Optimal    — a common base with class attributes ``code`` and ``status``; the boundary catches
   ``AppError`` once and reads the attributes (polymorphism instead of ``if`` chains).

Hints
-----
- Class attributes are inherited and can be overridden per subclass.
- Call ``super().__init__(message)`` so ``str(err)`` and ``err.args`` behave normally.
- Keep payload data in attributes (``details``), not baked into the message.

Follow-ups
----------
- Should ``NotFoundError`` also subclass ``LookupError``? (Multiple inheritance lets callers that
  only know built-ins still catch it.)
- How do you keep exceptions picklable? (``args`` must be enough to rebuild the object, or define
  ``__reduce__``.)
"""
from __future__ import annotations

import re


class AppError(Exception):
    code = "APP"
    status = 500

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = dict(details or {})

    def to_dict(self) -> dict:
        return {"code": self.code, "message": str(self), "details": self.details}


class ValidationError(AppError):
    code = "VALIDATION"
    status = 400


class NotFoundError(AppError, LookupError):   # also catchable as a built-in LookupError
    code = "NOT_FOUND"
    status = 404


class ConflictError(AppError):
    code = "CONFLICT"
    status = 409


USERNAME_RE = re.compile(r"[a-z0-9_]{3,20}")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class UserService:
    def __init__(self) -> None:
        self._users: dict[str, dict] = {}

    def create_user(self, username: str, email: str) -> dict:
        problems = {}
        if not USERNAME_RE.fullmatch(username or ""):
            problems["username"] = "3-20 chars of a-z, 0-9, _"
        if not EMAIL_RE.fullmatch(email or ""):
            problems["email"] = "must look like name@domain.tld"
        if problems:
            raise ValidationError("invalid user", details=problems)
        if username in self._users:
            raise ConflictError(f"user {username!r} already exists", details={"username": username})
        user = {"username": username, "email": email}
        self._users[username] = user
        return dict(user)

    def get_user(self, username: str) -> dict:
        try:
            return dict(self._users[username])
        except KeyError:
            # 'from None' hides the internal KeyError: callers see only the domain error.
            raise NotFoundError(f"no user {username!r}", details={"username": username}) from None


def handle(service: UserService, action: str, **kwargs) -> dict:
    operations = {"create": service.create_user, "get": service.get_user}
    try:
        data = operations[action](**kwargs)
    except AppError as err:                 # one clause for the whole family
        return {"status": err.status, "error": err.to_dict()}
    return {"status": 200, "data": data}


def main() -> None:
    print("== hierarchy ==")
    for cls in [ValidationError, NotFoundError, ConflictError]:
        print(f"{cls.__name__:<16} code={cls.code:<11} status={cls.status} "
              f"is AppError: {issubclass(cls, AppError)}")
    print("NotFoundError is LookupError:", issubclass(NotFoundError, LookupError))

    print("\n== boundary ==")
    svc = UserService()
    calls = [
        ("create", {"username": "ada", "email": "ada@example.com"}),
        ("create", {"username": "ada", "email": "ada@example.com"}),
        ("create", {"username": "X!", "email": "nope"}),
        ("get", {"username": "ada"}),
        ("get", {"username": "grace"}),
    ]
    for action, kwargs in calls:
        print(f"{action:<6} {kwargs} -> {handle(svc, action, **kwargs)}")

    print("\n== bugs still propagate ==")
    try:
        handle(svc, "delete", username="ada")
    except KeyError as exc:
        print("KeyError escaped the boundary:", exc)


if __name__ == "__main__":
    main()
