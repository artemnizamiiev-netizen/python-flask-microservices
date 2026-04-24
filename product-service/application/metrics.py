from prometheus_client import Counter

products_created_total = Counter(
    "products_created_total",
    "Total number of created products."
)

products_lookup_total = Counter(
    "products_lookup_total",
    "Total number of searching attempts grouped by result.",
    ["result"]
)
