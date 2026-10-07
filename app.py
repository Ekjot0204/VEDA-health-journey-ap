
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import sqlite3, os, re, json

BASE = Path(__file__).resolve().parent
DB = BASE / "veda.db"
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
ALLOWED = {"pdf","png","jpg","jpeg","webp","txt"}

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS records (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      kind TEXT NOT NULL,
      title TEXT NOT NULL,
      content TEXT DEFAULT '',
      date TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS medicines (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      salt TEXT DEFAULT '',
      dosage TEXT DEFAULT '',
      frequency TEXT DEFAULT '',
      status TEXT DEFAULT 'Active',
      notes TEXT DEFAULT '',
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS appointments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      doctor TEXT NOT NULL,
      date TEXT NOT NULL,
      purpose TEXT DEFAULT '',
      notes TEXT DEFAULT '',
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS family (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      relation TEXT DEFAULT '',
      phone TEXT DEFAULT '',
      access TEXT DEFAULT 'Emergency only',
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS reports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT NOT NULL,
      title TEXT NOT NULL,
      uploaded_at TEXT NOT NULL,
      extracted_text TEXT DEFAULT ''
    );
    """)
    c.commit()
    c.close()

init_db()

def now():
    return datetime.now().isoformat(timespec="seconds")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(UPLOADS, name)

@app.get("/api/state")
def state():
    c = db()
    records = [dict(x) for x in c.execute("SELECT * FROM records ORDER BY date DESC, id DESC").fetchall()]
    meds = [dict(x) for x in c.execute("SELECT * FROM medicines ORDER BY id DESC").fetchall()]
    appts = [dict(x) for x in c.execute("SELECT * FROM appointments ORDER BY date ASC, id ASC").fetchall()]
    family = [dict(x) for x in c.execute("SELECT * FROM family ORDER BY id DESC").fetchall()]
    reports = [dict(x) for x in c.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()]
    c.close()
    return jsonify({"records":records, "medicines":meds, "appointments":appts, "family":family, "reports":reports})

@app.post("/api/records")
def add_record():
    d = request.json or {}
    title = (d.get("title") or "Health event").strip()
    kind = (d.get("kind") or "Health event").strip()
    content = (d.get("content") or "").strip()
    date = d.get("date") or datetime.now().strftime("%Y-%m-%d")
    c = db()
    c.execute("INSERT INTO records(kind,title,content,date,created_at) VALUES(?,?,?,?,?)",(kind,title,content,date,now()))
    c.commit(); c.close()
    return jsonify({"ok":True})

@app.post("/api/medicines")
def add_medicine():
    d=request.json or {}
    name=(d.get("name") or "").strip()
    if not name: return jsonify({"ok":False,"error":"Medicine name required"}),400
    c=db()
    c.execute("""INSERT INTO medicines(name,salt,dosage,frequency,status,notes,created_at)
                 VALUES(?,?,?,?,?,?,?)""",
              (name,d.get("salt",""),d.get("dosage",""),d.get("frequency",""),d.get("status","Active"),d.get("notes",""),now()))
    c.commit(); c.close()
    return jsonify({"ok":True})

@app.delete("/api/medicines/<int:item_id>")
def delete_medicine(item_id):
    c=db(); c.execute("DELETE FROM medicines WHERE id=?",(item_id,)); c.commit(); c.close()
    return jsonify({"ok":True})

@app.post("/api/appointments")
def add_appointment():
    d=request.json or {}
    if not d.get("doctor") or not d.get("date"): return jsonify({"ok":False,"error":"Doctor and date required"}),400
    c=db()
    c.execute("INSERT INTO appointments(doctor,date,purpose,notes,created_at) VALUES(?,?,?,?,?)",
              (d["doctor"],d["date"],d.get("purpose",""),d.get("notes",""),now()))
    c.commit(); c.close()
    return jsonify({"ok":True})

@app.post("/api/family")
def add_family():
    d=request.json or {}
    if not d.get("name"): return jsonify({"ok":False,"error":"Name required"}),400
    c=db()
    c.execute("INSERT INTO family(name,relation,phone,access,created_at) VALUES(?,?,?,?,?)",
              (d["name"],d.get("relation",""),d.get("phone",""),d.get("access","Emergency only"),now()))
    c.commit(); c.close()
    return jsonify({"ok":True})

@app.post("/api/upload")
def upload():
    f=request.files.get("file")
    if not f or not f.filename: return jsonify({"ok":False,"error":"No file"}),400
    ext=f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED: return jsonify({"ok":False,"error":"Unsupported file type"}),400
    safe=secure_filename(f.filename)
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
    filename=f"{stamp}_{safe}"
    f.save(UPLOADS/filename)
    title=request.form.get("title") or safe
    extracted=""
    # Text files are parsed locally; PDFs/images are safely stored and can be connected
    # to an OCR/medical document AI service later without changing the UI.
    if ext=="txt":
        try: extracted=(UPLOADS/filename).read_text(errors="ignore")[:10000]
        except: extracted=""
    c=db()
    c.execute("INSERT INTO reports(filename,title,uploaded_at,extracted_text) VALUES(?,?,?,?)",
              (filename,title,now(),extracted))
    c.execute("INSERT INTO records(kind,title,content,date,created_at) VALUES(?,?,?,?,?)",
              ("Medical report",title,extracted or "Document uploaded; OCR/AI extraction not configured.",datetime.now().strftime("%Y-%m-%d"),now()))
    c.commit(); c.close()
    return jsonify({"ok":True,"filename":filename,"title":title,"extracted_text":extracted})

@app.post("/api/copilot")
def copilot():
    d=request.json or {}
    q=(d.get("message") or "").strip().lower()
    c=db()
    meds=[dict(x) for x in c.execute("SELECT * FROM medicines WHERE status='Active'").fetchall()]
    appts=[dict(x) for x in c.execute("SELECT * FROM appointments ORDER BY date ASC").fetchall()]
    reports=[dict(x) for x in c.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()]
    records=[dict(x) for x in c.execute("SELECT * FROM records ORDER BY date DESC").fetchall()]
    c.close()

    if any(w in q for w in ["medicine","medication","tablet","drug"]):
        if meds:
            answer="You currently have " + str(len(meds)) + " active medicine(s): " + ", ".join(m["name"] for m in meds) + ". I can organize this list, but medication changes should be confirmed with a doctor or pharmacist."
        else:
            answer="You don't have any active medicines saved yet. You can add them from Medicine Cabinet."
    elif any(w in q for w in ["appointment","doctor","visit"]):
        if appts:
            a=appts[0]
            answer=f"Your next saved appointment is with {a['doctor']} on {a['date']}. Purpose: {a['purpose'] or 'not specified'}. You can generate a Doctor Brief from the Appointment Preparation screen."
        else:
            answer="You don't have an appointment saved yet. Add one in Appointment Preparation."
    elif any(w in q for w in ["report","document","record","health journey"]):
        answer=f"VEDA currently has {len(reports)} uploaded document(s) and {len(records)} health timeline event(s). I can help you find, summarize, or prepare information from your stored records."
    elif any(w in q for w in ["allergy","conflict","interaction","duplicate","salt"]):
        answer="For medication safety, VEDA can flag possible duplicate active ingredients and recorded allergy conflicts. This prototype only uses the information you enter; confirm any warning with a pharmacist or doctor."
    elif any(w in q for w in ["hello","hi","hey"]):
        answer="Hi! I'm VEDA. I can help you navigate your stored health information, medicines, reports, appointments, and Doctor Briefs."
    else:
        answer="I can work with your saved VEDA data. Try asking: “What medicines am I taking?”, “When is my next appointment?”, or “How many reports do I have?” For medical decisions, please consult a qualified healthcare professional."
    return jsonify({"ok":True,"answer":answer})

@app.get("/api/health")
def health():
    return jsonify({"status":"online","time":now()})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
