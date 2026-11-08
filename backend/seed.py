"""
seed.py
────────
Database seeding script for LabLoop.

Creates all tables and inserts the initial set of demo users:
  • 1 Super Admin
  • 1 Lab In-charge
  • 2 Students

Run from the backend directory:
    python seed.py

WARNING: Running this script multiple times will skip users whose e-mail
addresses already exist in the database.
"""

import sys

from app import create_app
from app.extensions import db
from app.models.user import User, ROLE_STUDENT, ROLE_LAB_INCHARGE, ROLE_SUPER_ADMIN
from app.models.department import Department
from app.models.lab import Lab, LabAssignment
from app.models.equipment import Equipment, EquipmentCategory, STATUS_AVAILABLE, STATUS_UNDER_MAINTENANCE

# ── Seed data ─────────────────────────────────────────────────────────────────

SEED_USERS = [
    {
        "full_name": "Super Admin",
        "email": "admin@labloop.com",
        "password": "Admin@123",
        "role": ROLE_SUPER_ADMIN,
        "roll_number": None,
    },
    {
        "full_name": "Dr. Rajesh Kumar",
        "email": "incharge@labloop.com",
        "password": "Incharge@123",
        "role": ROLE_LAB_INCHARGE,
        "roll_number": None,
    },
    {
        "full_name": "Priya Sharma",
        "email": "student1@labloop.com",
        "password": "Student@123",
        "role": ROLE_STUDENT,
        "roll_number": "CS2021001",
    },
    {
        "full_name": "Arjun Nair",
        "email": "student2@labloop.com",
        "password": "Student@123",
        "role": ROLE_STUDENT,
        "roll_number": "CS2021002",
    },
]


def run_seed() -> None:
    """Create tables and insert seed users."""
    app = create_app("development")

    with app.app_context():
        # Ensure all tables exist
        db.create_all()
        print("[seed] Database tables verified / created.")

        created_count = 0
        skipped_count = 0

        for user_data in SEED_USERS:
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                print(
                    f"[seed] SKIP  — {user_data['role']:<12}  {user_data['email']} "
                    f"(already exists, id={existing.id})"
                )
                skipped_count += 1
                continue

            try:
                user = User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    role=user_data["role"],
                    roll_number=user_data.get("roll_number"),
                    is_active=True,
                    email_verified=True,  # Pre-verified for seed accounts
                )
                user.set_password(user_data["password"])
                db.session.add(user)
                db.session.commit()
                print(
                    f"[seed] CREATE — {user_data['role']:<12}  {user_data['email']} "
                    f"(id={user.id})"
                )
                created_count += 1
            except Exception as exc:
                db.session.rollback()
                print(
                    f"[seed] ERROR  — {user_data['email']}: {exc}",
                    file=sys.stderr,
                )

        # ── Seed Departments ──────────────────────────────────────────────────
        depts_data = [
            {"name": "Computer Science & Engineering", "code": "CSE", "description": "AI, Software Systems, Cloud & Networks"},
            {"name": "Electrical & Electronics Engineering", "code": "EEE", "description": "Power Systems, Robotics, Control Systems"},
            {"name": "Mechanical Engineering", "code": "MECH", "description": "CAD/CAM, Prototyping, Thermodynamics"},
        ]
        created_depts = {}
        for d in depts_data:
            existing = Department.query.filter(
                (Department.code == d["code"]) | (Department.name == d["name"])
            ).first()
            if not existing:
                dept = Department(name=d["name"], code=d["code"], description=d["description"])
                db.session.add(dept)
                db.session.commit()
                created_depts[d["code"]] = dept
            else:
                created_depts[d["code"]] = existing

        # Assign Student 1 & 2 to CSE
        cse_dept = created_depts.get("CSE")
        if cse_dept:
            for email in ["student1@labloop.com", "student2@labloop.com"]:
                u = User.query.filter_by(email=email).first()
                if u and not u.department_id:
                    u.department_id = cse_dept.id
                    db.session.commit()

        # ── Seed Labs ─────────────────────────────────────────────────────────
        labs_data = [
            {
                "name": "Advanced Robotics & AI Lab",
                "department_id": created_depts.get("EEE").id if created_depts.get("EEE") else 1,
                "location": "Tech Block 204",
                "capacity": 35,
            },
            {
                "name": "Network Systems & Cloud Lab",
                "department_id": created_depts.get("CSE").id if created_depts.get("CSE") else 1,
                "location": "Tech Block 301",
                "capacity": 40,
            },
        ]
        created_labs = {}
        for l in labs_data:
            existing = Lab.query.filter_by(name=l["name"]).first()
            if not existing:
                lab = Lab(
                    name=l["name"],
                    department_id=l["department_id"],
                    location=l["location"],
                    capacity=l["capacity"],
                )
                db.session.add(lab)
                db.session.commit()
                created_labs[l["name"]] = lab
            else:
                created_labs[l["name"]] = existing

        # Assign Lab In-charge to Robotics Lab
        incharge_user = User.query.filter_by(email="incharge@labloop.com").first()
        robotics_lab = created_labs.get("Advanced Robotics & AI Lab")
        if incharge_user and robotics_lab:
            existing_assignment = LabAssignment.query.filter_by(
                lab_id=robotics_lab.id, user_id=incharge_user.id
            ).first()
            if not existing_assignment:
                assignment = LabAssignment(
                    lab_id=robotics_lab.id,
                    user_id=incharge_user.id,
                    is_primary=True,
                )
                db.session.add(assignment)
                db.session.commit()

        # ── Seed Equipment Categories ─────────────────────────────────────────
        cat_data = [
            {"name": "High Performance Computing", "slug": "hpc-computing", "icon_name": "Cpu", "description": "GPU workstations and training clusters"},
            {"name": "Measurement & Signal Analysis", "slug": "signal-measurement", "icon_name": "Activity", "description": "Oscilloscopes and spectrum analyzers"},
            {"name": "Prototyping & Fabrication", "slug": "prototyping-fab", "icon_name": "Layers", "description": "3D printers and micro-fabrication"},
        ]
        created_cats = {}
        for c in cat_data:
            existing = EquipmentCategory.query.filter_by(slug=c["slug"]).first()
            if not existing:
                cat = EquipmentCategory(name=c["name"], slug=c["slug"], icon_name=c["icon_name"], description=c["description"])
                db.session.add(cat)
                db.session.commit()
                created_cats[c["slug"]] = cat
            else:
                created_cats[c["slug"]] = existing

        # ── Seed Equipment ────────────────────────────────────────────────────
        secret_key = app.config.get("SECRET_KEY", "dev-secret-key")
        eq_items = [
            {
                "name": "NVIDIA RTX A6000 GPU Workstation #04",
                "model_number": "A6000-48GB",
                "serial_number": "GPU-RAI-2024-04",
                "manufacturer": "NVIDIA / Dell Precision",
                "lab_id": robotics_lab.id if robotics_lab else 1,
                "category_id": created_cats.get("hpc-computing").id if created_cats.get("hpc-computing") else 1,
                "quantity_total": 8,
                "quantity_available": 6,
                "status": STATUS_AVAILABLE,
                "description": "48GB VRAM Workstation for Deep Learning & Computer Vision Research",
                "location_in_lab": "Bay 3, Desk 04",
            },
            {
                "name": "Keysight DSO-X 2000A Digital Oscilloscope",
                "model_number": "DSOX2024A",
                "serial_number": "DSO-KYS-400-09",
                "manufacturer": "Keysight Technologies",
                "lab_id": robotics_lab.id if robotics_lab else 1,
                "category_id": created_cats.get("signal-measurement").id if created_cats.get("signal-measurement") else 2,
                "quantity_total": 12,
                "quantity_available": 10,
                "status": STATUS_AVAILABLE,
                "description": "100 MHz Bandwidth, 2GSa/s, 4 Analog Channels with WaveGen",
                "location_in_lab": "Workbench 2",
            },
            {
                "name": "Creality Ender-3 S1 Pro 3D Printer",
                "model_number": "Ender-3-S1-PRO",
                "serial_number": "PRN-3D-2024-02",
                "manufacturer": "Creality",
                "lab_id": robotics_lab.id if robotics_lab else 1,
                "category_id": created_cats.get("prototyping-fab").id if created_cats.get("prototyping-fab") else 3,
                "quantity_total": 4,
                "quantity_available": 3,
                "status": STATUS_AVAILABLE,
                "description": "Dual-gear direct extruder, 300C high-temp nozzle for ABS/PLA",
                "location_in_lab": "Prototyping Table 1",
            },
        ]
        for eq in eq_items:
            existing = Equipment.query.filter_by(serial_number=eq["serial_number"]).first()
            if not existing:
                item = Equipment(
                    name=eq["name"],
                    model_number=eq["model_number"],
                    serial_number=eq["serial_number"],
                    manufacturer=eq["manufacturer"],
                    lab_id=eq["lab_id"],
                    category_id=eq["category_id"],
                    quantity_total=eq["quantity_total"],
                    quantity_available=eq["quantity_available"],
                    status=eq["status"],
                    description=eq["description"],
                    location_in_lab=eq["location_in_lab"],
                )
                item.generate_qr(secret_key)
                db.session.add(item)
                db.session.commit()
                print(f"[seed] Equipment added: {item.name} (QR token: {item.qr_code_token[:10]}...)")

        # ── Summary ───────────────────────────────────────────────────────────
        print()
        print("=" * 60)
        print("  LabLoop — Seed Complete")
        print("=" * 60)
        print(f"  Created : {created_count}")
        print(f"  Skipped : {skipped_count}")
        print()
        print("  Credentials:")
        print()
        for user_data in SEED_USERS:
            print(
                f"  [{user_data['role']:<12}]  "
                f"email: {user_data['email']:<30}  "
                f"password: {user_data['password']}"
            )
        print("=" * 60)
        print()


if __name__ == "__main__":
    run_seed()
