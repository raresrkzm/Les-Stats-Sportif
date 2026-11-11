"""
Modulul conține implementarea unui ThreadPool cu fire de execuție
reutilizabile pentru procesarea joburilor asincrone.
"""

from queue import Queue, Empty
from threading import Thread, Event, Lock
import os
import json
from time import sleep
import multiprocessing
from app.logger import logger

class ThreadPool:
    """
    Gestionează un grup fix de fire de execuție (TaskRunner) care procesează joburi dintr-o coadă.
    Numărul de fire este dat de variabila de mediu TP_NUM_OF_THREADS
    sau de numărul de core-uri disponibile.
    """

    def __init__(self):
        self.task_queue = Queue()
        self.shutdown_event = Event()
        self.job_status = {}
        self.lock = Lock()

        num_threads = int(os.environ.get("TP_NUM_OF_THREADS", multiprocessing.cpu_count()))
        self.runners = [TaskRunner(self.task_queue, self.shutdown_event, self.job_status)
                        for _ in range(num_threads)]

        for runner in self.runners:
            runner.start()

    def submit_job(self, job_id, job_callable):
        """
        Trimite un job în coada de execuție, dacă nu s-a inițiat oprirea.
        Returnează True dacă a fost trimis cu succes, False altfel.
        """
        with self.lock:
            if self.shutdown_event.is_set():
                return False
            self.job_status[job_id] = "running"
            self.task_queue.put((job_id, job_callable))
            return True

    def graceful_shutdown(self):
        """
        Inițiază oprirea controlată a ThreadPool-ului.
        """
        self.shutdown_event.set()
        self.task_queue.join()

    def is_shutting_down(self):
        """
        Returnează True dacă s-a inițiat oprirea controlată, altfel False.
        """
        return self.shutdown_event.is_set()

    def remaining_jobs(self):
        """
        Returnează numărul de joburi rămase în coadă.
        """
        return self.task_queue.qsize()

    def get_status(self, job_id):
        """
        Returnează statusul unui job dat (ex. 'running', 'done', 'error') sau None dacă nu există.
        """
        return self.job_status.get(job_id, None)

    def all_jobs(self):
        """
        Returnează o copie a dicționarului cu statusul tuturor joburilor.
        """
        return self.job_status.copy()


class TaskRunner(Thread):
    """
    Fire de execuție care preiau joburi dintr-o coadă și le procesează,
    salvând rezultatul în fișiere JSON.
    """

    def __init__(self, task_queue, shutdown_event, job_status):
        super().__init__()
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.job_status = job_status

    def run(self):
        """
        Rulează în mod continuu, executând joburile din coadă
        până când se inițiază oprirea controlată.
        Rezultatele sunt salvate în fișiere JSON în directorul 'results/'.
        """

        while not self.shutdown_event.is_set() or not self.task_queue.empty():
            try:
                job_id, job_callable = self.task_queue.get()
                logger.info(f"[TaskRunner] Job {job_id} preluat pentru execuție.")
                try:
                    result = job_callable()
                    with open(f"results/{job_id}.json", "w", encoding="utf-8") as f:
                        json.dump({"status": "done", "data": result}, f)
                    self.job_status[job_id] = "done"

                    logger.info(f"[TaskRunner] Job {job_id} finalizat cu succes.")

                except Exception as e:
                    self.job_status[job_id] = f"error: {str(e)}"
                    logger.error(f"[TaskRunner] Eroare în job {job_id}: {str(e)}")

                finally:
                    self.task_queue.task_done()
                    sleep(0.1)

            except Empty:
                continue
