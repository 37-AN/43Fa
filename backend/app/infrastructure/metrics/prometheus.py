from prometheus_client import Counter

request_counter = Counter("shadowplant_http_requests_total", "Total HTTP requests", ["method", "path", "status"])
upload_counter = Counter("shadowplant_uploads_total", "Total dataset uploads")
