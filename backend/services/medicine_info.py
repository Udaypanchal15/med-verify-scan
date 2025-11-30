import random
import requests
import json

medicine_knowledge = {
    "Paracetamol": {
        "side_effects": "Nausea, rash, headache, liver damage in overdose.",
        "drug_interactions": "Avoid alcohol and other hepatotoxic drugs.",
        "contraindications": "Severe liver disease, allergy to paracetamol.",
        "avoid_medicines": ["Warfarin", "Isoniazid"],
        "dosage": "500mg every 4-6 hours, max 4g/day.",
    },
    "Ibuprofen": {
        "side_effects": "Stomach pain, heartburn, dizziness, increased bleeding risk.",
        "drug_interactions": "Avoid other NSAIDs, blood thinners, and certain antihypertensives.",
        "contraindications": "Peptic ulcer, severe heart failure, allergy to NSAIDs.",
        "avoid_medicines": ["Aspirin", "Warfarin", "Lithium"],
        "dosage": "200-400mg every 4-6 hours, max 1200mg/day OTC.",
    }
}

def search_online_database(med_name):
    simulated_db = {
        "Paracetamol": {
            "source": "Simulated Online DB",
            "side_effects": "Simulated: Nausea, rash, headache (less detailed).",
            "drug_interactions": "Simulated: Avoid alcohol.",
            "contraindications": "Simulated: Liver issues.",
            "avoid_medicines": ["Simulated Warfarin"],
            "dosage": "Simulated: 500mg."
        },
        "Ibuprofen": {
            "source": "Simulated Online DB",
            "side_effects": "Simulated: Stomach upset, bleeding risk.",
            "drug_interactions": "Simulated: Avoid other pain relievers.",
            "contraindications": "Simulated: Ulcers.",
            "avoid_medicines": ["Simulated Aspirin"],
            "dosage": "Simulated: 200-400mg."
        }
    }

    try:
        if random.random() < 0.1:
            raise requests.exceptions.RequestException("Simulated network error")

        return simulated_db.get(med_name)
    except Exception as e:
        print(f"Online DB Error: {e}")
        return None

def ai_describe_medicine(med_name, medicine_data=None):
    """
    Get AI-generated description of medicine
    Uses LLM service if available, falls back to knowledge base
    """
    med_name = med_name.strip().title()
    
    # Try AI service first (lazy import to avoid circular dependency)
    try:
        from services.ai_service import get_ai_service
        ai_service = get_ai_service()
        if medicine_data:
            ai_summary = ai_service.get_medicine_ai_summary(medicine_data)
            return ai_summary.get("summary", {})
        else:
            # Create minimal medicine data
            medicine_data = {"name": med_name}
            ai_summary = ai_service.get_medicine_ai_summary(medicine_data)
            return ai_summary.get("summary", {})
    except Exception as e:
        print(f"AI service error: {e}")
        # Fall back to knowledge base
        pass
    
    # Fallback to knowledge base
    online_info = search_online_database(med_name)
    if online_info:
        return online_info

    info = medicine_knowledge.get(med_name)
    if not info:
        return {"message": "No detailed information available for this medicine."}

    return info
