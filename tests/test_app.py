import os
import tempfile
import unittest

_TEST_DIR = tempfile.mkdtemp(prefix="aprende-web-tests-")
os.environ["SECRET_KEY"] = "test-secret-key-only"
os.environ["COOKIE_SECURE"] = "false"
os.environ["DATABASE_PATH"] = os.path.join(_TEST_DIR, "test.db")
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "test-admin-password"

import app as site


class AcademySmokeTests(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.join(_TEST_DIR, self._testMethodName + ".db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        site.DATABASE = self.db_path
        site.init_db()
        site.app.config.update(TESTING=True, SECRET_KEY="test-secret-key-only")
        self.client = site.app.test_client()
        self.token = "csrf-test-token"
        with self.client.session_transaction() as session:
            session["_csrf"] = self.token

    def refresh_csrf(self):
        with self.client.session_transaction() as session:
            self.token = session.get("_csrf", self.token)

    def post(self, path, data=None):
        payload = dict(data or {})
        payload["_csrf"] = self.token
        response = self.client.post(path, data=payload, follow_redirects=True)
        self.refresh_csrf()
        return response

    def register_student(self):
        response = self.post("/registro", {
            "username": "estudiante_test",
            "password": "una-clave-de-prueba-123"
        })
        self.assertEqual(response.status_code, 200)
        self.refresh_csrf()

    def test_public_pages_render(self):
        for path in ("/", "/aprender-programar", "/curso/html", "/laboratorio",
                     "/herramientas", "/proyectos", "/retos", "/ranking", "/comunidad/proyectos"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_student_notes_bookmarks_quiz_and_progress(self):
        self.register_student()

        response = self.post("/curso/html/apunte/1", {"note": "Repasar etiquetas semánticas."})
        self.assertEqual(response.status_code, 200)

        response = self.post("/curso/html/guardar")
        self.assertEqual(response.status_code, 200)

        response = self.post("/curso/html/completar/1")
        self.assertEqual(response.status_code, 200)

        response = self.post("/curso/html/evaluar", {"q0": "0", "q1": "1", "q2": "2"})
        self.assertEqual(response.status_code, 200)

        with site.get_db() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM lesson_notes").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM progress").fetchone()[0], 1)
            score = conn.execute("SELECT score FROM quiz_attempts").fetchone()[0]
            self.assertEqual(score, 3)

        self.assertEqual(self.client.get("/mi-aprendizaje").status_code, 200)
        self.assertEqual(self.client.get("/curso/html").status_code, 200)

    def test_invalid_csrf_is_rejected(self):
        response = self.client.post("/comentarios", data={"message": "Prueba"})
        self.assertEqual(response.status_code, 400)

    def test_admin_can_sign_in(self):
        response = self.post("/admin/login", {
            "username": "admin",
            "password": "test-admin-password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/admin").status_code, 200)


    def test_profile_community_and_tutor_sections(self):
        self.register_student()
        self.assertEqual(self.client.get("/mi-perfil").status_code, 200)
        response = self.post("/mi-perfil", {
            "display_name": "Estudiante Demo",
            "bio": "Estoy aprendiendo desarrollo web y creando proyectos.",
            "favorite_stack": "HTML, CSS y Python",
            "website": "https://example.com"
        })
        self.assertEqual(response.status_code, 200)
        response = self.post("/comunidad/proyectos", {
            "title": "Mi primera web",
            "description": "Una página de práctica que hice para aprender HTML y CSS.",
            "technologies": "HTML, CSS",
            "project_url": "https://example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/tutor").status_code, 200)
        response = self.post("/tutor", {"question": "¿Qué es una variable en Python?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/notificaciones").status_code, 200)
        with site.get_db() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM project_posts").fetchone()[0], 1)
            profile = conn.execute("SELECT display_name FROM user_profiles").fetchone()
            self.assertEqual(profile["display_name"], "Estudiante Demo")


    def test_legendary_academy_practice_and_private_snippets(self):
        self.assertEqual(self.client.get("/academia").status_code, 200)
        self.assertEqual(self.client.get("/practica").status_code, 200)
        self.register_student()
        response = self.client.get("/practica/1")
        self.assertEqual(response.status_code, 200)
        response = self.post("/practica/1", {"code": "<h1>Mi primera web</h1>"})
        self.assertEqual(response.status_code, 200)
        with site.get_db() as conn:
            attempt = conn.execute("SELECT passed FROM exercise_attempts WHERE user_id=?", (1,)).fetchone()
            self.assertIsNotNone(attempt)
            self.assertEqual(attempt["passed"], 1)
        response = self.post("/mis-fragmentos", {
            "title": "Mi título HTML", "language": "HTML", "code": "<h1>Hola</h1>"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/mis-fragmentos").status_code, 200)
        with site.get_db() as conn:
            snippet = conn.execute("SELECT id FROM code_snippets WHERE user_id=?", (1,)).fetchone()
        self.assertIsNotNone(snippet)
        self.assertEqual(self.post(f"/mis-fragmentos/{snippet['id']}/eliminar").status_code, 200)

    def test_admin_can_manage_practice_exercises(self):
        self.post("/admin/login", {"username": "admin", "password": "test-admin-password"})
        self.assertEqual(self.client.get("/admin/ejercicios").status_code, 200)
        response = self.post("/admin/ejercicios", {
            "title": "Ejercicio de prueba", "technology": "HTML", "level": "Inicial",
            "description": "Un ejercicio creado desde el panel.",
            "instructions": "Creá una etiqueta h2 para practicar.",
            "starter_code": "<!-- empezá acá -->", "required_tokens": "<h2>||</h2>"
        })
        self.assertEqual(response.status_code, 200)
        with site.get_db() as conn:
            row = conn.execute("SELECT id FROM practice_exercises WHERE title=?", ("Ejercicio de prueba",)).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(self.post(f"/admin/ejercicios/{row['id']}/eliminar").status_code, 200)

if __name__ == "__main__":
    unittest.main()
