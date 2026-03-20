# FastAPI Backend: Medical Appointment System

This repository contains a fully functional Medical Appointment System developed as the final project for the Innomatics Technology Hub FastAPI Internship.

## 🚀 Features Implemented
* **Appointment Management:** 20 RESTful endpoints for managing doctors, patients, and schedules.
* **Pydantic Validation:** Strict data schemas for booking appointments and registering patients.
* **CRUD Operations:** Full Create, Read, Update, and Delete functionality for medical records.
* **Multi-Step Workflow:** Integrated logic for Appointment Booking → Check-in → Patient History.
* **Advanced Search:** Keyword search for doctors by specialty, sorting by date, and pagination.

## 🛠️ Installation & Setup
1. **Clone the repository:**
   
   ```bash
   git clone [Your-GitHub-Link-Here]

3. **Set up Virtual Environment:**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate | Mac: source venv/bin/activate

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

5. **Run the Server:**
   ```bash
   uvicorn main:app --reload

## 📂 Project Structure

* **main.py:** Core application code.
* **requirements.txt:** Project dependencies.
* **screenshots/:** 20 Swagger UI testing images.
