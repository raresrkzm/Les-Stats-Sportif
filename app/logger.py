"""
Configurare logger pentru serverul Flask, cu salvare în fișier rotativ `webserver.log`.

Folosește RotatingFileHandler pentru a limita dimensiunea fișierului și a păstra istoricul.
"""

import logging
from logging.handlers import RotatingFileHandler
import time

# Numele fișierului de log unde se salvează toate înregistrările
LOG_FILE = "webserver.log"

# Creează un logger global cu numele "webserver_logger"
logger = logging.getLogger("webserver_logger")
logger.setLevel(logging.INFO)  # Se loghează doar mesaje de nivel INFO și mai sus

# Creează un handler care rotește fișierul log
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)

# Formatter pentru fiecare linie de log
formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Timpul este salvat în UTC, nu în local time
formatter.converter = time.gmtime
handler.setFormatter(formatter)

# Atașează handlerul la logger dacă nu are deja altul atașat
if not logger.hasHandlers():
    logger.addHandler(handler)
