import sqlite3
import json
import re
import subprocess
import flask
import joblib
import numpy as np

app = flask.Flask(__name__)
ml_model = joblib.load("cognitive_model.pkl")

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            difficulty TEXT,
            wpm REAL,
            errors INTEGER,
            backspaces INTEGER,
            pauses INTEGER,
            accuracy REAL,
            load_score REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------- ACCURATE LOAD SCORE (NASA-TLX inspired) -------- #
def compute_load_score(wpm, errors, backspaces, pauses, accuracy, difficulty):
    bench = {"Easy": 40, "Medium": 30, "Hard": 20}.get(difficulty, 30)
    # Speed penalty: how far below benchmark (0-100)
    speed_penalty  = max(0, (bench - wpm) / bench * 100)
    # Error load: inaccuracy percentage
    error_load     = max(0, 100 - accuracy)
    # Pause load: each 2s+ pause = attention lapse, capped at 50
    pause_load     = min(pauses * 6, 50)
    # Backspace load: self-correction overhead, capped at 40
    bs_load        = min(backspaces * 2.5, 40)
    # Difficulty multiplier
    diff_mult      = {"Easy": 0.80, "Medium": 1.0, "Hard": 1.25}.get(difficulty, 1.0)

    raw = (error_load * 0.35 + speed_penalty * 0.25 + pause_load * 0.25 + bs_load * 0.15) * diff_mult
    return round(min(max(raw, 0), 100), 2)


def compute_breakdown(wpm, errors, backspaces, pauses, accuracy, difficulty, load_score):
    bench    = {"Easy": 40, "Medium": 30, "Hard": 20}.get(difficulty, 30)
    sp       = max(0, (bench - wpm) / bench * 100)
    err_comp = max(0, 100 - accuracy)
    pau_comp = min(pauses * 6, 50)
    bs_comp  = min(backspaces * 2.5, 40)

    def lvl(v, lo=20, hi=50):
        return "Low" if v < lo else ("Moderate" if v < hi else "High")

    breakdown = {
        "speed":      {"label": "Speed Deficit",       "value": round(sp, 1),       "level": lvl(sp),
                       "advice": f"Your {round(wpm,1)} WPM is below the {bench} WPM benchmark — mental strain slows typing." if sp > 20 else "Speed is within the expected range."},
        "accuracy":   {"label": "Inaccuracy Load",     "value": round(err_comp, 1), "level": lvl(err_comp),
                       "advice": f"{round(100-accuracy,1)}% error rate signals cognitive overload — information not processed cleanly." if err_comp > 20 else "Accuracy is solid."},
        "pauses":     {"label": "Attention Gaps",      "value": round(pau_comp, 1), "level": lvl(pau_comp),
                       "advice": f"{pauses} pause(s) detected — working memory saturation." if pauses > 2 else "Focus maintained well throughout."},
        "backspaces": {"label": "Self-Correction Cost","value": round(bs_comp, 1),  "level": lvl(bs_comp),
                       "advice": f"{backspaces} backspace(s) — high self-monitoring adds overhead." if backspaces > 5 else "Low correction rate — good coordination."},
    }
    if load_score < 20:   grade, glabel = "A", "Excellent"
    elif load_score < 35: grade, glabel = "B", "Good"
    elif load_score < 55: grade, glabel = "C", "Moderate"
    elif load_score < 75: grade, glabel = "D", "High Load"
    else:                 grade, glabel = "F", "Overloaded"
    return breakdown, grade, glabel


def compute_radar(wpm, errors, backspaces, pauses, accuracy, difficulty):
    cap   = {"Easy": 80, "Medium": 65, "Hard": 50}.get(difficulty, 60)
    speed = round(min(wpm / cap * 100, 100), 1)
    acc   = round(min(max(accuracy, 0), 100), 1)
    focus = round(max(100 - pauses * 12 - backspaces * 1.5, 0), 1)
    stab  = round(max(100 - (100 - accuracy) * 0.6 - pauses * 7, 0), 1)
    bm    = {"Easy": [60,92,80,85], "Medium": [55,88,75,80], "Hard": [50,82,68,72]}.get(difficulty, [55,88,75,80])
    return {"speed": speed, "accuracy": acc, "focus": focus, "stability": stab,
            "bench_speed": bm[0], "bench_accuracy": bm[1], "bench_focus": bm[2], "bench_stability": bm[3]}


def clean_json_string(s):
    """Robustly extract and clean JSON from LLM output."""
    s = s.strip()
    # Remove markdown fences
    s = re.sub(r'```json\s*', '', s)
    s = re.sub(r'```\s*', '', s)
    s = s.strip()
    # Find the outermost { }
    start = s.find('{')
    end   = s.rfind('}')
    if start == -1 or end == -1:
        return None
    s = s[start:end+1]
    # Remove control characters that break json.loads (except \t \n \r)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', s)
    # Normalise newlines inside string values to spaces
    # Match string values and replace inner newlines
    def fix_string(m):
        inner = m.group(1).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return '"' + inner + '"'
    s = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_string, s)
    return s


# -------- ROUTES -------- #

@app.route("/")
def home():
    return flask.render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    difficulty = flask.request.form["difficulty"]
    wpm        = float(flask.request.form["wpm"])
    errors     = int(flask.request.form["errors"])
    backspaces = int(flask.request.form["backspaces"])
    pauses     = int(flask.request.form["pauses"])
    accuracy   = float(flask.request.form["accuracy"])
    load_score = compute_load_score(wpm, errors, backspaces, pauses, accuracy, difficulty)
    conn = sqlite3.connect("database.db")
    c    = conn.cursor()
    c.execute("INSERT INTO results (difficulty,wpm,errors,backspaces,pauses,accuracy,load_score) VALUES (?,?,?,?,?,?,?)",
              (difficulty, wpm, errors, backspaces, pauses, accuracy, load_score))
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return flask.redirect(flask.url_for("result", result_id=rid))


@app.route("/result/<int:result_id>")
def result(result_id):
    conn = sqlite3.connect("database.db")
    c    = conn.cursor()
    c.execute("SELECT * FROM results WHERE id = ?", (result_id,))
    data = c.fetchone()
    if data is None:
        conn.close()
        return "Result not found", 404
    c.execute("SELECT load_score FROM results WHERE id < ? ORDER BY id DESC LIMIT 1", (result_id,))
    prev  = c.fetchone()
    delta = round(data[7] - prev[0], 2) if prev else 0
    conn.close()

    features = np.array([[data[2], data[6], data[5], data[4]]])
    try:
        ml_score = float(ml_model.predict(features)[0])
    except Exception:
        ml_score = data[7]
    ml_score = round(max(0, min(ml_score, 100)), 2)

    imp = ml_model.feature_importances_
    feature_importance = {"Speed": round(imp[0]*100,1), "Accuracy": round(imp[1]*100,1),
                          "Pauses": round(imp[2]*100,1), "Backspaces": round(imp[3]*100,1)}

    ml_level = "Low" if ml_score < 25 else ("Moderate" if ml_score < 60 else "High")
    breakdown, grade, glabel = compute_breakdown(data[2],data[3],data[4],data[5],data[6],data[1],data[7])
    radar = compute_radar(data[2],data[3],data[4],data[5],data[6],data[1])

    return flask.render_template("result.html", data=data, delta=delta, ml_score=ml_score,
        ml_level=ml_level, feature_importance=feature_importance,
        breakdown=breakdown, grade=grade, grade_label=glabel, radar=radar)


@app.route("/ai/<int:result_id>")
def ai_analysis(result_id):
    conn = sqlite3.connect("database.db")
    c    = conn.cursor()
    c.execute("SELECT * FROM results WHERE id = ?", (result_id,))
    data = c.fetchone()
    conn.close()
    if data is None:
        return "Result not found", 404

    breakdown, grade, glabel = compute_breakdown(data[2],data[3],data[4],data[5],data[6],data[1],data[7])
    radar = compute_radar(data[2],data[3],data[4],data[5],data[6],data[1])

    bench      = {"Easy":40,"Medium":30,"Hard":20}.get(data[1],30)
    spd_status = "below benchmark" if data[2] < bench else "above benchmark"
    acc_status = "poor" if data[6] < 75 else ("fair" if data[6] < 90 else "excellent")

    # Very explicit prompt — tells model exactly what to output, no ambiguity
    prompt = f"""You are a cognitive performance analyst. Analyse this typing test data and give personalised insights.

DATA:
Difficulty: {data[1]}
WPM: {round(data[2],1)} ({spd_status}, benchmark is {bench} WPM)
Accuracy: {round(data[6],1)}% ({acc_status})
Errors made: {data[3]}
Backspaces used: {data[4]}
Attention pauses (2s+): {data[5]}
Cognitive Load Score: {round(data[7],1)} out of 100
Grade: {grade} - {glabel}
Focus score: {radar['focus']}/100
Stability score: {radar['stability']}/100

INSTRUCTIONS:
- Reference the actual numbers in your analysis
- Be specific, not generic
- Output ONLY a JSON object, nothing else, no markdown, no explanation before or after

OUTPUT FORMAT (valid JSON only):
{{
  "cognitive_state": "Write 2 sentences describing this person cognitive state based on their exact numbers.",
  "risk_level": "Low",
  "mental_load_summary": "Write 2 sentences explaining what the load score of {round(data[7],1)} means for this person right now.",
  "key_issues": ["Issue 1", "Issue 2", "Issue 3"],
  "action_tips": ["Tip 1", "Tip 2", "Tip 3"],
  "mental_peace_advice": "Write 2 sentences of calming advice and mental peace strategies for someone with this load level.",
  "recovery_plan": "Write 2 sentences suggesting specific recovery steps based on their weakest areas.",
  "strongest_area": "One sentence about what they did best.",
  "weakest_area": "One sentence about their biggest weakness and its cognitive meaning."
}}"""

    ai_output = {
        "cognitive_state": "Ollama is not running or gemma3:4b is not available. Start Ollama and try again.",
        "risk_level": "Unknown",
        "mental_load_summary": "",
        "key_issues": [],
        "action_tips": [],
        "mental_peace_advice": "",
        "recovery_plan": "",
        "strongest_area": "",
        "weakest_area": ""
    }

    try:
        proc = subprocess.run(
            "ollama run gemma3:4b",
            input=prompt, text=True, capture_output=True,
            shell=True, timeout=120, encoding="utf-8", errors="replace"
        )
        raw = proc.stdout
        cleaned = clean_json_string(raw)
        if cleaned:
            ai_output = json.loads(cleaned)
    except json.JSONDecodeError as e:
        ai_output["cognitive_state"] = f"JSON parse error: {e}. Raw: {raw[:200]}"
    except Exception as e:
        ai_output["cognitive_state"] = f"Error: {str(e)}"

    return flask.render_template("ai.html", data=data, breakdown=breakdown,
        grade=grade, grade_label=glabel, radar=radar, ai_output=ai_output)


@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    c    = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return flask.render_template("history.html", rows=rows)


@app.route("/delete/<int:result_id>")
def delete(result_id):
    conn = sqlite3.connect("database.db")
    c    = conn.cursor()
    c.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    conn.close()
    return flask.redirect(flask.url_for("history"))


if __name__ == "__main__":
    app.run(debug=True)
