"""
Acest modul definește rutele API pentru aplicația Flask.

Rutele permit procesarea cererilor legate de statistici despre sănătate și activitate fizică în SUA.
Fiecare rută primește cereri de tip POST sau GET, pornește joburi asincrone prin `TasksRunner`
și returnează răspunsuri JSON corespunzătoare.
"""

import os
import json
from flask import request, jsonify
from app import webserver
from app.logger import logger

def register_job(func):
    """Inregistrează un job asincron și returnează un ID asociat."""
    job_id = f"job_id_{webserver.job_counter}"
    webserver.job_counter += 1
    logger.info(f"Înregistrare job nou: {job_id}")

    success = webserver.tasks_runner.submit_job(job_id, func)

    if not success:
        logger.info(f"Job {job_id} respins: sistemul se închide.")
        return jsonify({"status": "error", "reason": "shutting down"})

    logger.info(f"Job {job_id} înregistrat cu succes.")
    return jsonify({"job_id": job_id})

@webserver.route('/api/post_endpoint', methods=['POST'])
def post_endpoint():
    """Endpoint de test pentru primirea datelor JSON prin POST."""
    if request.method == 'POST':
        # Assuming the request contains JSON data
        data = request.json
        print(f"got data in post {data}")

        # Process the received data
        # For demonstration purposes, just echoing back the received data
        response = {"message": "Received data successfully", "data": data}

        # Sending back a JSON response
        return jsonify(response)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/get_results/<job_id>', methods=['GET'])
def get_response(job_id):
    """Returnează rezultatul unui job dacă este gata, altfel statusul curent."""
    logger.info(f"GET /api/get_results - job_id: {job_id}")
    path = f"results/{job_id}.json"

    if not os.path.exists(path):
        status = webserver.tasks_runner.get_status(job_id)

        logger.info(f"Job {job_id} nu are rezultat încă. Status: {status}")

        if status is None:
            return jsonify({"status": "error", "reason": "Invalid job_id"})

        return jsonify({"status": "running"})

    with open(path, "r", encoding="utf-8") as f:
        result = json.load(f)

    logger.info(f"Rezultat returnat pentru job {job_id}")
    return jsonify(result)

@webserver.route('/api/states_mean', methods=['POST'])
def states_mean_request():
    """Inițiază un job pentru media valorilor la nivel de state."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/state_mean - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_states_mean(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/state_mean', methods=['POST'])
def state_mean_request():
    """Inițiază un job pentru media unei valori pentru un stat specific."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/states_mean - data: {data}")
        question = data.get("question")
        state = data.get("state")

        def job():
            return webserver.data_ingestor.get_state_mean(question, state)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405


@webserver.route('/api/best5', methods=['POST'])
def best5_request():
    """Inițiază un job care returnează top 5 cele mai bune state."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/best5 - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_best5(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/worst5', methods=['POST'])
def worst5_request():
    """Inițiază un job care returnează top 5 cele mai slabe state."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/worst5 - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_worst5(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/global_mean', methods=['POST'])
def global_mean_request():
    """Inițiază un job care calculează media globală a unei valori."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/global_mean - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_global_mean(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/diff_from_mean', methods=['POST'])
def diff_from_mean_request():
    """Inițiază un job care returnează diferențele faȓă de media globală."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/diff_from_mean - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_diff_from_mean(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/state_diff_from_mean', methods=['POST'])
def state_diff_from_mean_request():
    """Inițiază un job pentru diferența unui stat faȓă de media globală."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/state_diff_from_mean - data: {data}")
        question = data.get("question")
        state = data.get("state")

        def job():
            return webserver.data_ingestor.get_state_diff_from_mean(question, state)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/mean_by_category', methods=['POST'])
def mean_by_category_request():
    """Inițiază un job care returnează media valorilor pe categorii."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/mean_by_category - data: {data}")
        question = data.get("question")

        def job():
            return webserver.data_ingestor.get_mean_by_category(question)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/state_mean_by_category', methods=['POST'])
def state_mean_by_category_request():
    """Inițiază un job care returnează media pe categorii pentru un stat."""
    if request.method == 'POST':
        data = request.json
        logger.info(f"POST /api/state_mean_by_category - data: {data}")
        question = data.get("question")
        state = data.get("state")

        def job():
            return webserver.data_ingestor.get_state_mean_by_category(question, state)

        return register_job(job)

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/graceful_shutdown', methods=['GET'])
def graceful_shutdown():
    """Inițiază oprirea controlată a executorului de taskuri."""
    if request.method == 'GET':
        logger.info("GET /api/graceful_shutdown - oprire controlată inițiată.")
        webserver.tasks_runner.graceful_shutdown()

        if webserver.tasks_runner.remaining_jobs() > 0:
            logger.info("Joburi încă în execuție.")
            return jsonify({"status": "running"})

        logger.info("Toate joburile finalizate. Shutdown complet.")
        return jsonify({"status": "done"})

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Returnează toate job-urile curente cu statusul lor."""
    if request.method == 'GET':
        logger.info("GET /api/jobs - listare joburi active.")
        jobs = webserver.tasks_runner.all_jobs()
        data = [{jid: status} for jid, status in jobs.items()]

        return jsonify({"status": "done", "data": data})

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/api/num_jobs', methods=['GET'])
def num_jobs():
    """Returnează numărul de joburi în așteptare sau în execuție."""
    if request.method == 'GET':
        logger.info("GET /api/num_jobs - interogare număr joburi rămase.")
        return jsonify({"num_jobs": webserver.tasks_runner.remaining_jobs()})

    # Method Not Allowed
    return jsonify({"error": "Method not allowed"}), 405

@webserver.route('/')
@webserver.route('/index')
def index():
    """Pagina principală - listează toate rutele definite ale serverului."""
    logger.info("GET / - pagina principală accesată.")
    routes = get_defined_routes()
    msg = "Hello, World!\n Interact with the webserver using one of the defined routes:\n"

    # Display each route as a separate HTML <p> tag
    paragraphs = ''.join(f"<p>{route}</p>" for route in routes)

    msg += paragraphs
    return msg

def get_defined_routes():
    """Returnează toate rutele definite în aplicație într-un format lizibil."""
    routes = []
    for rule in webserver.url_map.iter_rules():
        methods = ', '.join(rule.methods)
        routes.append(f"Endpoint: \"{rule}\" Methods: \"{methods}\"")
    return routes
