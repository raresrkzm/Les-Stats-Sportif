"""Inițializarea aplicației Flask și a componentelor globale."""

import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

# Creez directorul results dacă nu există deja
if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

# Inițializez thread pool-ul și încărcăm datele
webserver.tasks_runner = ThreadPool()
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
webserver.job_counter = 1

from app import routes
