import logging.handlers
import os

_logger = logging.getLogger('weread_to_notion')
_logger.setLevel(logging.DEBUG)

_cons_rht = logging.StreamHandler()

# _log_base_dir = f'/var/log'
_log_base_dir = '.'

# _pid = os.getpid()
log_dir = f'{_log_base_dir}/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file_name = 'weread_to_notion'

_file_rht = logging.handlers.RotatingFileHandler(f"{log_dir}/{log_file_name}.log",
                                                 maxBytes=1024 * 1024 * 1024,
                                                 backupCount=100)

_fmt = logging.Formatter("%(asctime)s pid:%(process)d %(filename)s:%(lineno)s %(levelname)s: %(message)s",
                         "%Y-%m-%d %H:%M:%S")

_file_rht.setFormatter(_fmt)
_cons_rht.setFormatter(_fmt)

_logger.addHandler(_file_rht)
_logger.addHandler(_cons_rht)

debug = _logger.debug
info = _logger.info
warning = _logger.warning
error = _logger.error
exception = _logger.exception
critical = _logger.critical
