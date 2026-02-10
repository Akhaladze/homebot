import os
import logging
import json
import pandas as pd
import duckdb
import requests
from datetime import datetime
from flask import Flask, request, jsonify, abort
from werkzeug.middleware.proxy_fix import ProxyFix

# --- OpenTelemetry Imports ---
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Импорт наших сервисов
from services.telegrambot import tg_service

# --- Настройка Логирования и OTel ---
# Имя сервиса для Tempo/Loki
resource = Resource.create(attributes={"service.name": "iot-homebot", "service.namespace": "home-lab"})

# Провайдер трейсинга
trace.set_tracer_provider(TracerProvider(resource=resource))

# Экспортер в Alloy (по умолчанию localhost:14317, берем из ENV)
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://10.10.100.20:14317")
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

# Batch processor (отправляет пачками для эффективности)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Инструментация (автоматический сбор данных)
LoggingInstrumentor().instrument(set_logging_packages=True) # Добавляет TraceID в логи
RequestsInstrumentor().instrument() # Трейсит исходящие запросы (requests.get)

# Стандартный логгер Python
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(name)s] [trace_id=%(otelTraceID)s] %(message)s')
logger = logging.getLogger(__name__)

# --- Инициализация Flask ---
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Инструментация Flask (трейсит входящие запросы)
FlaskInstrumentor().instrument_app(app)

# --- Инициализация Mikrotik (если нужен) ---
# from services.mikrotik import MikroTikService
# mt_service = MikroTikService(...) 

@app.route('/')
def index():
    logger.info("Index page accessed")
    return jsonify({"status": "running", "otel": "enabled"})

# --- Webhook Endpoint ---
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            # Передаем обновление в телеграм сервис
            if tg_service:
                tg_service.process_update(json_string)
            return 'OK', 200
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            return jsonify({"error": "Internal Error"}), 500
    else:
        abort(403)

@app.route('/init-webhook', methods=['GET'])
def init_webhook_route():
    if not tg_service:
        return jsonify({"error": "Bot service not initialized"}), 500
    
    try:
        updated = tg_service.setup_webhook()
        return jsonify({"status": "success", "updated": updated, "url": tg_service.webhook_url})
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/sync-all', methods=['POST'])
def sync_all():
    # Трейсер можно получить вручную для кастомных спанов
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("sync_logic"):
        logger.info("Starting sync process...")
        # ... твоя логика с pandas и duckdb ...
        # Пример:
        # with tracer.start_as_current_span("mikrotik_fetch"):
        #     leases = mt_service.get_dhcp_leases()
        return jsonify({"status": "simulated_success"})

if __name__ == '__main__':
    # При локальном запуске
    logger.info("Starting Flask app locally...")
    app.run(host='0.0.0.0', port=5000, debug=True)
