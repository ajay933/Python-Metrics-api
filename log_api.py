from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.exceptions import HTTPException
import time
import logging
import sys

# Configure logging to console
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

logger = logging.getLogger(__name__)

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

@app.route('/')
def hello():
    start_time = time.time()
    try:
        REQUEST_COUNT.labels('GET', '/', 200).inc()

        # Simulate an API call
        logger.info('Making an API call')
        time.sleep(1)  # Replace with actual API call logic
        API_CALL_DURATION.labels('external_api').observe(time.time() - start_time)

        # Simulate a successful response
        response = jsonify(message='Hello, world!')
        REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
        return response

    except Exception as e:
        logger.error(f'Error processing request: {e}')
        return jsonify(error=str(e)), 500

@app.errorhandler(404)
def not_found(error):
    logger.error(f'404 Error: {error}')
    REQUEST_COUNT.labels('GET', request.path, 404).inc()
    return jsonify(error='Not Found', status=404), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'500 Error: {error}')
    REQUEST_COUNT.labels('GET', request.path, 500).inc()
    return jsonify(error='Internal Server Error', status=500), 500

@app.errorhandler(401)
def unauthorized(error):
    logger.error(f'401 Error: {error}')
    REQUEST_COUNT.labels('GET', request.path, 401).inc()
    return jsonify(error='Unauthorized', status=401), 401

@app.errorhandler(Exception)
def handle_exception(error):
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    logger.error(f'{code} Error: {error}')
    REQUEST_COUNT.labels(request.method, request.path, code).inc()
    return jsonify(error=str(error), status=code), code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

