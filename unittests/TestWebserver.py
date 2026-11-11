import unittest
import time
from app import webserver
from app.data_ingestor import DataIngestor


class TestWebserver(unittest.TestCase):
    """
    Clasa de testare pentru toate rutele API definite în serverul Flask.
    Verifică răspunsurile și valorile returnate de API comparativ cu cele
    returnate direct de metodele clasei DataIngestor.
    """

    def setUp(self):
        """
        Inițializează clientul Flask de test și obiectul DataIngestor.
        """
        self.client = webserver.test_client()
        self.question = (
            "Percent of adults who achieve at least 150 minutes a week of "
            "moderate-intensity aerobic physical activity or 75 minutes a week of "
            "vigorous-intensity aerobic activity (or an equivalent combination)"
        )
        self.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

    def wait_for_result(self, job_id, timeout=5):
        """
        Așteaptă până când jobul este finalizat sau până la expirarea timeout-ului.

        :param job_id: ID-ul jobului așteptat
        :param timeout: număr maxim de secunde de așteptare
        :return: rezultatul jobului dacă este finalizat
        :raises: Exception dacă jobul eșuează sau TimeoutError dacă expiră timpul
        """
        for _ in range(timeout * 10):
            response = self.client.get(f'/api/get_results/{job_id}')

            try:
                data = response.get_json()
            except Exception as e:
                print("Nu s-a putut parsa JSON:", e)
                print("Răspuns de la server:", response.data.decode())
                raise

            if data.get("status") == "done":
                return data.get("data")
            elif data.get("status") == "error":
                raise Exception(f"Job failed: {data}")
            time.sleep(0.1)

    def test_states_mean(self):
        """Testează ruta /api/states_mean."""
        response = self.client.post('/api/states_mean', json={"question": self.question})
        self.assertEqual(response.status_code, 200)
        
        job_id = response.get_json().get("job_id")
        self.assertIsNotNone(job_id)
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_states_mean(self.question), result)

    def test_state_mean(self):
        """Testează ruta /api/state_mean."""
        response = self.client.post('/api/state_mean', json={
            "question": self.question,
            "state": "Wyoming"
        })
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_state_mean(self.question, "Wyoming"), result)

    def test_best5(self):
        """Testează ruta /api/best5."""
        response = self.client.post('/api/best5', json={"question": self.question})
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_best5(self.question), result)

    def test_worst5(self):
        """Testează ruta /api/worst5."""
        response = self.client.post('/api/worst5', json={"question": self.question})
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_worst5(self.question), result)

    def test_global_mean(self):
        """Testează ruta /api/global_mean."""
        response = self.client.post('/api/global_mean', json={"question": self.question})
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_global_mean(self.question), result)

    def test_diff_from_mean(self):
        """Testează ruta /api/diff_from_mean."""
        response = self.client.post('/api/diff_from_mean', json={"question": self.question})
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_diff_from_mean(self.question), result)

    def test_state_diff_from_mean(self):
        """Testează ruta /api/state_diff_from_mean."""
        response = self.client.post('/api/state_diff_from_mean', json={
            "question": self.question,
            "state": "Florida"
        })
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(
            self.data_ingestor.get_state_diff_from_mean(self.question, "Florida"), result
        )

    def test_mean_by_category(self):
        """Testează ruta /api/mean_by_category."""
        response = self.client.post('/api/mean_by_category', json={"question": self.question})
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(self.data_ingestor.get_mean_by_category(self.question), result)

    def test_state_mean_by_category(self):
        """Testează ruta /api/state_mean_by_category."""
        response = self.client.post('/api/state_mean_by_category', json={
            "question": self.question,
            "state": "Michigan"
        })
        self.assertEqual(response.status_code, 200)

        job_id = response.get_json().get("job_id")
        result = self.wait_for_result(job_id)
        self.assertEqual(
            self.data_ingestor.get_state_mean_by_category(self.question, "Michigan"),
            result
        )

    def test_get_jobs(self):
        """Testează ruta /api/jobs pentru afișarea joburilor active."""
        post_response = self.client.post('/api/state_mean', json={
            "question": self.question,
            "state": "Wyoming"
        })
        self.assertEqual(post_response.status_code, 200)
        job_id = post_response.get_json().get("job_id")
        self.assertIsNotNone(job_id)

        response = self.client.get('/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "done")
        self.assertTrue(any(job_id in job for job in data["data"]))

    def test_num_jobs(self):
        """Testează ruta /api/num_jobs pentru numărul de joburi rămase."""
        response = self.client.get('/api/num_jobs')
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("num_jobs", data)
        self.assertIsInstance(data["num_jobs"], int)

