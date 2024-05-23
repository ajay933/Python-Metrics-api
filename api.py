from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Gauge, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)
API_CALL_DURATION = Histogram(
    'api_call_duration_seconds',
    'External API Call Duration',
    ['api_name']
)
DATABASE_QUERY_TIME = Gauge(
    'database_query_time_seconds',
    'Database Query Time',
    ['query_type']
)

@app.route('/')
def hello():
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()

    try:
        # Simulate an API call
        logging.info('Making an API call')
        time.sleep(1)  # Replace with actual API call logic
        API_CALL_DURATION.labels('external_api').observe(time.time() - start_time)

        # Simulate a database query
        logging.info('Executing a database query')
        query_time = 0.5  # Replace with actual query execution time
        DATABASE_QUERY_TIME.labels('select').set(query_time)
        time.sleep(query_time)

        response = jsonify(message='Hello, worldsfdsf dsavcskdvflkdsnflsanfcdd!')
        REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
        return response

    except Exception as e:
        logging.error(f'Error processing request: {e}')
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
