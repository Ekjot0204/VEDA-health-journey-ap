# VEDA — AI Personal Health Copilot

A functional Flask prototype for the VEDA hackathon concept.

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create/activate a virtual environment (recommended).
4. Run:
   `pip install -r requirements.txt`
5. Start:
   `python app.py`
6. Open:
   `http://127.0.0.1:5000`

## What is functional

- Real CRUD data stored in SQLite
- Live dashboard counts and 5-second synchronization
- Health Journey / memory timeline
- Document upload and storage
- Medicine Cabinet
- Appointment management
- Doctor Brief generation from saved data
- Family coordination records
- Emergency Health Card
- Profile and privacy UI
- A safe, data-grounded prototype copilot
- Responsive UI

## Important production note

This prototype intentionally does NOT pretend that an LLM or OCR has medically interpreted an image when no medical AI service is configured. For a production/hackathon deployment, connect:
- OCR/document extraction service
- A vetted medication/drug database
- A secure AI API for document summarization
- Authentication and authorization
- Encryption in transit/at rest
- Audit logging
- Appropriate healthcare privacy/compliance controls

Do not put real patient health information into this prototype until those safeguards are implemented.
