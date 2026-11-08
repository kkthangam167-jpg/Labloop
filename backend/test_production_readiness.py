"""
test_production_readiness.py
Comprehensive verification script for LabLoop production readiness.
"""
import sys
import unittest
import json
from app import create_app
from app.extensions import db
from app.models.user import User, ROLE_STUDENT, ROLE_LAB_INCHARGE, ROLE_SUPER_ADMIN

class ProductionReadinessTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.app.config["DEBUG"] = False
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

            # Seed Admin
            admin = User.query.filter_by(email="admin@labloop.com").first()
            if not admin:
                admin = User(
                    full_name="System Super Administrator",
                    email="admin@labloop.com",
                    role=ROLE_SUPER_ADMIN,
                    is_active=True,
                    email_verified=True,
                )
                admin.set_password("Admin@123")
                db.session.add(admin)

            # Seed In-charge
            incharge = User.query.filter_by(email="incharge@labloop.com").first()
            if not incharge:
                incharge = User(
                    full_name="Faculty Lab In-charge",
                    email="incharge@labloop.com",
                    role=ROLE_LAB_INCHARGE,
                    is_active=True,
                    email_verified=True,
                )
                incharge.set_password("Incharge@123")
                db.session.add(incharge)

            db.session.commit()

    def test_01_student_registration_and_no_dev_otp_leak(self):
        """Test student registration with institutional email format and verify dev_otp is NOT leaked."""
        res = self.client.post("/api/auth/register", json={
            "full_name": "Vijay Kumar",
            "admission_year": "25",
            "department_code": "CS",
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "password": "Password@123",
            "confirm_password": "Password@123"
        })
        # 201 if email sent, 503 if SMTP unconfigured
        self.assertIn(res.status_code, [201, 503])
        data = res.get_json()
        payload = data.get("data") or {}
        # In non-debug mode, dev_otp MUST NOT be present
        self.assertNotIn("dev_otp", payload, "dev_otp leaked in production/non-debug mode!")

    def test_02_invalid_student_email_rejection(self):
        """Test invalid institutional email formats are rejected with 422."""
        invalid_emails = [
            "vijay@gmail.com",
            "vijay.ug.2025.cs@francisxavier.ac.in",  # 4 digit year
            "vijay.cs@francisxavier.ac.in",          # missing .ug.
            "vijay.ug.25.c@francisxavier.ac.in",    # 1-letter dept
            "vijay.ug.25.cs@othercollege.edu",      # wrong domain
        ]
        for em in invalid_emails:
            res = self.client.post("/api/auth/register", json={
                "full_name": "Test Student",
                "admission_year": "25",
                "department_code": "CS",
                "email": em,
                "password": "Password@123",
                "confirm_password": "Password@123"
            })
            self.assertEqual(res.status_code, 422, f"Failed to reject invalid email: {em}")

    def test_03_unverified_student_cannot_login(self):
        """Test that unverified student accounts cannot log in (403 Forbidden)."""
        res = self.client.post("/api/auth/login", json={
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "password": "Password@123"
        })
        self.assertEqual(res.status_code, 403)
        data = res.get_json()
        self.assertIn("verified", data.get("message", "").lower())

    def test_04_otp_verification_activates_student(self):
        """Test OTP verification activates the student account and enables login."""
        with self.app.app_context():
            user = User.query.filter_by(email="vijay.ug.25.cs@francisxavier.ac.in").first()
            self.assertIsNotNone(user)
            # Set known OTP
            user.set_otp("654321", minutes=15)
            db.session.commit()

        # Wrong OTP test
        res_bad = self.client.post("/api/auth/verify-otp", json={
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "otp": "000000"
        })
        self.assertEqual(res_bad.status_code, 400)

        # Valid OTP test
        res_good = self.client.post("/api/auth/verify-otp", json={
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "otp": "654321"
        })
        self.assertEqual(res_good.status_code, 200)

        # Now student can log in
        res_login = self.client.post("/api/auth/login", json={
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "password": "Password@123"
        })
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertIn("access_token", login_data["data"])
        self.assertEqual(login_data["data"]["user"]["role"], "student")

    def test_05_admin_login_and_privileged_access(self):
        """Test Super Admin authentication and access to admin-only endpoints."""
        res_login = self.client.post("/api/auth/login", json={
            "email": "admin@labloop.com",
            "password": "Admin@123"
        })
        self.assertEqual(res_login.status_code, 200)
        token = res_login.get_json()["data"]["access_token"]

        # Admin accessing user management -> 200 OK
        res_users = self.client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_users.status_code, 200)

    def test_06_incharge_login_and_access(self):
        """Test Lab In-charge authentication and access."""
        res_login = self.client.post("/api/auth/login", json={
            "email": "incharge@labloop.com",
            "password": "Incharge@123"
        })
        self.assertEqual(res_login.status_code, 200)
        token = res_login.get_json()["data"]["access_token"]

        # In-charge accessing lab equipment -> 200 OK
        res_eq = self.client.get("/api/equipment", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_eq.status_code, 200)

    def test_07_role_based_security_student_blocked_from_admin_apis(self):
        """Test that student tokens are strictly rejected from admin endpoints (403 Forbidden)."""
        # Login student
        res_login = self.client.post("/api/auth/login", json={
            "email": "vijay.ug.25.cs@francisxavier.ac.in",
            "password": "Password@123"
        })
        token = res_login.get_json()["data"]["access_token"]

        # Student attempts to access /api/users (Admin only)
        res_admin = self.client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_admin.status_code, 403, "Student was able to access /api/users!")

        # Student attempts to create equipment (Incharge/Admin only)
        res_create_eq = self.client.post("/api/equipment", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Unauthorized Oscilloscope",
            "lab_id": 1
        })
        self.assertEqual(res_create_eq.status_code, 403, "Student was able to create equipment!")

if __name__ == "__main__":
    unittest.main()

