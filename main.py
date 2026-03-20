import math
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Medical Appointment System")

# --- DATA INITIALIZATION ---

# Q2 Data
doctors =[
    {"id": 1, "name": "Dr. Sarah Adams", "specialization": "Cardiologist", "fee": 250, "experience_years": 15, "is_available": True},
    {"id": 2, "name": "Dr. John Chen", "specialization": "Dermatologist", "fee": 150, "experience_years": 8, "is_available": True},
    {"id": 3, "name": "Dr. Emily Blunt", "specialization": "Pediatrician", "fee": 120, "experience_years": 5, "is_available": False},
    {"id": 4, "name": "Dr. Michael Scott", "specialization": "General", "fee": 80, "experience_years": 12, "is_available": True},
    {"id": 5, "name": "Dr. Lisa Ray", "specialization": "Cardiologist", "fee": 300, "experience_years": 20, "is_available": False},
    {"id": 6, "name": "Dr. James Wilson", "specialization": "General", "fee": 90, "experience_years": 3, "is_available": True}
]

# Q4 Data
appointments =[]
appt_counter = 1

# --- PYDANTIC MODELS (Q6 & Q9) ---

class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default='in-person')
    senior_citizen: bool = Field(default=False) # Added in Q9
    
# --- FOR Q11 ---
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = Field(default=True)


# --- HELPER FUNCTIONS (Q7, Q9, Q10) ---

def find_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

def calculate_fee(base_fee: float, appointment_type: str, senior_citizen: bool):
    fee = base_fee
    
    # Apply appointment type modifier (Q7)
    if appointment_type == 'video':
        fee *= 0.80
    elif appointment_type == 'emergency':
        fee *= 1.50
    # 'in-person' is full fee, so no change needed
        
    # Apply senior citizen discount (Q9)
    if senior_citizen:
        fee *= 0.85 # 15% discount
        
    return fee

def filter_doctors_logic(specialization: Optional[str] = None, max_fee: Optional[int] = None, min_experience: Optional[int] = None, is_available: Optional[bool] = None):
    filtered_list = doctors
    
    # All checks strictly use `is not None` (Q10)
    if specialization is not None:
        filtered_list =[d for d in filtered_list if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        filtered_list = [d for d in filtered_list if d["fee"] <= max_fee]
    if min_experience is not None:
        filtered_list = [d for d in filtered_list if d["experience_years"] >= min_experience]
    if is_available is not None:
        filtered_list = [d for d in filtered_list if d["is_available"] == is_available]
        
    return filtered_list

def find_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            return appt
    return None

# --- ROUTES ---

# Q1: Basic GET / route
@app.get("/")
def read_root():
    return {"message": "Welcome to MediCare Clinic"}


# Q2: GET all doctors with totals
@app.get("/doctors")
def get_all_doctors():
    available_count = sum(1 for doctor in doctors if doctor["is_available"])
    return {
        "doctors": doctors,
        "total": len(doctors),
        "available_count": available_count
    }


# Q4: GET all appointments
@app.get("/appointments")
def get_all_appointments():
    return {
        "appointments": appointments,
        "total": len(appointments)
    }

# Q15: GET active appointments 
@app.get("/appointments/active")
def get_active_appointments():
    active_appts =[a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {"active_appointments": active_appts, "count": len(active_appts)}

# Q8 & Q9: POST Appointment
@app.post("/appointments")
def create_appointment(request: AppointmentRequest):
    global appt_counter # Needed to modify the global counter
    
    doctor = find_doctor(request.doctor_id)
    
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    if not doctor["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor is currently unavailable")
        
    calculated_fee = calculate_fee(doctor["fee"], request.appointment_type, request.senior_citizen)
    
    new_appointment = {
        "appointment_id": appt_counter,
        "patient": request.patient_name,
        "doctor_name": doctor["name"],
        "date": request.date,
        "type": request.appointment_type,
        "original_fee": doctor["fee"],     # Required by Q9
        "calculated_fee": calculated_fee,  # Required by Q8 & Q9
        "status": "scheduled"
    }
    
    appointments.append(new_appointment)
    appt_counter += 1
    
    return new_appointment

# --- Q19: APPOINTMENTS SEARCH, SORT, PAGE ---

@app.get("/appointments/search")
def search_appointments(patient_name: str):
    keyword = patient_name.lower()
    matches = [a for a in appointments if keyword in a["patient"].lower()]
    
    if not matches:
        return {"message": f"No appointments found for patient '{patient_name}'", "total_found": 0, "results":[]}
        
    return {"total_found": len(matches), "results": matches}

@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "fee", order: str = "asc"):
    # Validate params
    if sort_by not in ["fee", "date"]:
        raise HTTPException(status_code=400, detail="Can only sort by 'fee' or 'date'")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'")
        
    # Map 'fee' to the actual dictionary key 'calculated_fee'
    sort_key = "calculated_fee" if sort_by == "fee" else "date"
    reverse_sort = True if order == "desc" else False
    
    sorted_appts = sorted(appointments, key=lambda x: x[sort_key], reverse=reverse_sort)
    return {"metadata": {"sort_by": sort_by, "order": order}, "results": sorted_appts}

@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 3):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be >= 1")
        
    total_items = len(appointments)
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    return {
        "metadata": {"page": page, "limit": limit, "total_pages": total_pages, "total_items": total_items},
        "results": appointments[start_idx:end_idx]
    }
    
# --- Q16, Q17, Q18, Q20: DOCTORS ADVANCED ROUTES ---

# Q16: Search Doctors
@app.get("/doctors/search")
def search_doctors(keyword: str):
    kw = keyword.lower()
    matches = [
        d for d in doctors 
        if kw in d["name"].lower() or kw in d["specialization"].lower()
    ]
    
    if not matches:
        return {"message": f"No doctors found matching '{keyword}'", "total_found": 0, "results":[]}
        
    return {"total_found": len(matches), "results": matches}

# Q17: Sort Doctors
@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    valid_sorts =["fee", "name", "experience_years"]
    
    # Validate both params
    if sort_by not in valid_sorts:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by. Must be one of {valid_sorts}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
        
    reverse_sort = True if order == "desc" else False
    sorted_docs = sorted(doctors, key=lambda x: x[sort_by], reverse=reverse_sort)
    
    return {"metadata": {"sort_by": sort_by, "order": order}, "results": sorted_docs}

# Q18: Paginate Doctors
@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be >= 1")
        
    total_items = len(doctors)
    total_pages = math.ceil(total_items / limit) # Ceiling division
    
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    return {
        "metadata": {"page": page, "limit": limit, "total_pages": total_pages},
        "results": doctors[start_idx:end_idx]
    }

# Q20: Browse Doctors (Combined Logic)
@app.get("/doctors/browse")
def browse_doctors(
    keyword: Optional[str] = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    # Start with all doctors
    data = doctors
    
    # 1. Apply Filter/Search
    if keyword:
        kw = keyword.lower()
        data = [d for d in data if kw in d["name"].lower() or kw in d["specialization"].lower()]
        
    # 2. Apply Sort
    if sort_by in ["fee", "name", "experience_years"] and order in ["asc", "desc"]:
        reverse_sort = True if order == "desc" else False
        data = sorted(data, key=lambda x: x[sort_by], reverse=reverse_sort)
        
    # 3. Apply Pagination
    total_items = len(data)
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_data = data[start_idx:end_idx]
    
    return {
        "metadata": {
            "keyword": keyword,
            "sort_by": sort_by,
            "order": order,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "total_found_after_search": total_items
        },
        "results": paginated_data
    }    

# Q5: GET doctors summary
@app.get("/doctors/summary")
def get_doctors_summary():
    if not doctors:
        return {"message": "No doctors available"}

    total_doctors = len(doctors)
    available_count = sum(1 for doctor in doctors if doctor["is_available"])
    
    # Calculate most experienced
    most_experienced_doctor = max(doctors, key=lambda x: x["experience_years"])
    
    # Calculate cheapest fee
    cheapest_doctor = min(doctors, key=lambda x: x["fee"])
    
    # Calculate counts per specialization
    specialization_counts = {}
    for doctor in doctors:
        spec = doctor["specialization"]
        if spec in specialization_counts:
            specialization_counts[spec] += 1
        else:
            specialization_counts[spec] = 1

    return {
        "total_doctors": total_doctors,
        "available_count": available_count,
        "most_experienced_doctor": most_experienced_doctor["name"],
        "cheapest_consultation_fee": cheapest_doctor["fee"],
        "specialization_counts": specialization_counts
    }

# Q10: GET doctors filter 
@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None, 
    max_fee: Optional[int] = None, 
    min_experience: Optional[int] = None, 
    is_available: Optional[bool] = None
):
    filtered = filter_doctors_logic(specialization, max_fee, min_experience, is_available)
    return {
        "results": filtered,
        "count": len(filtered)
    }


# Q3: GET specific doctor by ID
@app.get("/doctors/{doctor_id}")
def get_doctor_by_id(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
            
    # Return error if not found
    raise HTTPException(status_code=404, detail="Doctor not found")

# Q15: GET appointments by doctor
@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    doc_appts = [a for a in appointments if a["doctor_name"] == doctor["name"]]
    return {"appointments": doc_appts, "count": len(doc_appts)}

# Q14: Confirm appointment
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appt["status"] = "confirmed"
    return appt

# Q14: Cancel appointment
@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appt["status"] = "cancelled"
    
    # Mark doctor as available again
    for doc in doctors:
        if doc["name"] == appt["doctor_name"]:
            doc["is_available"] = True
            break
            
    return appt

# Q15: Complete appointment
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appt["status"] = "completed"
    return appt


# Q11: POST new doctor
@app.post("/doctors", status_code=status.HTTP_201_CREATED)
def add_doctor(doctor: NewDoctor):
    # Check for duplicate name
    for existing_doc in doctors:
        if existing_doc["name"].lower() == doctor.name.lower():
            raise HTTPException(status_code=400, detail="Doctor with this name already exists")
    
    # Generate new ID
    new_id = max((d["id"] for d in doctors), default=0) + 1
    
    # Create doctor dictionary
    new_doctor_dict = doctor.model_dump()
    new_doctor_dict["id"] = new_id
    
    doctors.append(new_doctor_dict)
    return new_doctor_dict

# Q12: PUT (Update) doctor
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: Optional[int] = None, is_available: Optional[bool] = None):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    if fee is not None:
        doctor["fee"] = fee
    if is_available is not None:
        doctor["is_available"] = is_available
        
    return doctor

# Q13: DELETE doctor
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # Check if doctor has scheduled appointments
    for appt in appointments:
        if appt["doctor_name"] == doctor["name"] and appt["status"] == "scheduled":
            raise HTTPException(status_code=400, detail="Cannot delete doctor with active scheduled appointments")
            
    doctors.remove(doctor)
    return {"message": f"Doctor {doctor['name']} successfully deleted"}