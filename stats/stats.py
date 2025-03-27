from prometheus_client import Counter, Histogram, generate_latest, Gauge

from flask import Blueprint, Flask, request, abort
from cfg import PROMETHEUS_ENABLED, PROMETHEUS_TOKEN
import time

stats = Blueprint('stats', __name__, url_prefix='/api')

class Prometheus:
    def __init__(self, app: Flask):
        self.searched_songs = Counter('searched_songs', 'Number of songs looked up', ['endpoint'])
        self.endpoint_latency = Histogram('endpoint_latency_seconds', 'Endpoint response time', ['endpoint'])
        self.error_counter = Counter('endpoint_errors', 'Total errors per endpoint and status code', ['endpoint', 'status_code'])

        app.after_request(self.after_request)
        app.before_request(self.before_request)

    def before_request(self):
        request.start_time = time.time()
    
    def after_request(self, response):
        if (response.status_code > 400 and response.status_code < 600):
            self.error_counter.labels(endpoint=request.path, status_code=str(response.status_code)).inc()

        if request.path not in ('/favicon.ico', '/metrics'):
            latency = time.time() - request.start_time
            self.endpoint_latency.labels(endpoint=request.path).observe(latency)

        return response



@stats.route('/metrics')
def metrics():
    if not PROMETHEUS_ENABLED: abort(410)
    
    auth_header = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        abort(401)

    token = auth_header.split(" ")[1]
    if token != PROMETHEUS_TOKEN:
        print(token, PROMETHEUS_TOKEN)
        abort(403)

    return generate_latest(), 200, {'Content-Type': 'text/plain'}
