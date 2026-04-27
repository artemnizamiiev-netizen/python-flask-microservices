from prometheus_client import Counter

order_items_added_total = Counter(
    "order_items_added_total",
    "Total number of added products."
)

checkout_attempts_total = Counter(
    "checkout_attempts_total",
    "Total number of checkout attempts grouped by result.",
    ["result"]
)
