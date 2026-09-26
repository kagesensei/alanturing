"""Shared local activity and chat logging for project applications."""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
import traceback


LOG_DIR = Path(__file__).resolve().parents[1] / 'logs'
ACTIVITY_LOG = LOG_DIR / 'application.log'
CHAT_DIR = LOG_DIR / 'chats'
SESSION_PATTERN = re.compile(r'[A-Za-z0-9_-]{16,128}\Z')


class JsonLineHandler(logging.Handler):
    """Write one JSON event per line to a record-specific log file."""

    def emit(self, record):
        try:
            target = Path(getattr(record, 'target_path', ACTIVITY_LOG))
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = self._payload(record)
            with target.open('a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(payload, ensure_ascii=False) + '\n')
        except OSError:
            self.handleError(record)

    @staticmethod
    def _payload(record):
        try:
            payload = json.loads(record.getMessage())
        except json.JSONDecodeError:
            payload = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'application': getattr(record, 'application_name', 'application'),
                'event': 'application_log',
                'level': record.levelname,
                'message': record.getMessage(),
            }
        if record.exc_info:
            payload['traceback'] = ''.join(traceback.format_exception(*record.exc_info))
        return payload


def _shared_logger():
    logger = logging.getLogger('alanturing.file_logs')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not any(isinstance(handler, JsonLineHandler) for handler in logger.handlers):
        logger.addHandler(JsonLineHandler())
    return logger


def _event(application, event, **details):
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'application': application,
        'event': event,
        **details,
    }


def record_application_event(application, event, **details):
    """Append an application activity event without request secrets or URLs."""
    payload = _event(application, event, **details)
    _shared_logger().info(json.dumps(payload, ensure_ascii=False),
                          extra={'target_path': ACTIVITY_LOG})


def record_application_error(application, event, error, **details):
    """Record an exception and traceback in the shared activity log."""
    payload = _event(application, event, level='ERROR',
                     error_type=type(error).__name__, message=str(error), **details)
    payload['traceback'] = ''.join(traceback.format_exception(
        type(error), error, error.__traceback__))
    _shared_logger().error(json.dumps(payload, ensure_ascii=False),
                           extra={'target_path': ACTIVITY_LOG})


def record_chat_event(session_id, event, application='turing_test_simulator', **details):
    """Append a structured chat event to the session's local .log file."""
    if not isinstance(session_id, str) or not SESSION_PATTERN.fullmatch(session_id):
        raise ValueError('Invalid chat log session identifier')
    payload = _event(application, event, **details)
    target = CHAT_DIR / f'{session_id}.log'
    _shared_logger().info(json.dumps(payload, ensure_ascii=False),
                          extra={'target_path': target})


def configure_flask_logging(app, application):
    """Capture Flask errors and request activity with route templates only."""
    from flask import request  # pylint: disable=import-outside-toplevel

    handler = _shared_logger().handlers[0]
    if handler not in app.logger.handlers:
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    record_application_event(application, 'application.started')

    @app.after_request
    def record_request(response):
        if request.endpoint != 'static':
            route = request.url_rule.rule if request.url_rule else 'unmatched'
            record_application_event(application, 'http_request',
                                     method=request.method, route=route,
                                     status_code=response.status_code)
        return response
