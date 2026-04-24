from prometheus_client import Counter

user_registrations_total = Counter(
    "user_registrations_total",
    "Total number of successful user registrations."
)

user_login_attempts_total = Counter(
    "user_login_attempts_total",
    "Total number of user login attempts grouped by result.",
    ["result"]
)
