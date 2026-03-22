# 🧠 Cognitive Load Analyzer

A full-stack web application that analyzes a user's cognitive load using behavioral typing metrics, machine learning, and AI-based insights.

---

## 📌 Overview

The **Cognitive Load Analyzer** is designed to evaluate mental effort and performance under different conditions by analyzing typing behavior. It simulates real-world cognitive stress using time constraints and varying levels of text complexity.

The system captures behavioral signals such as typing speed, pauses, backspaces, and accuracy, and processes them to estimate cognitive load levels.

---

## 🚀 Features

* 🎯 **Difficulty-Based Testing**

  * Easy, Medium, Hard modes with increasing linguistic complexity
  * Time-based constraints to simulate cognitive pressure

* ⌨️ **Real-Time Typing Analysis**

  * Character-level validation (correct / incorrect / pending)
  * Live feedback with visual highlighting

* 📊 **Behavioral Metrics Tracking**

  * Words Per Minute (WPM)
  * Accuracy (%)
  * Pauses (hesitation detection)
  * Backspaces (correction behavior)

* 🧠 **Cognitive Load Calculation**

  * Custom weighted formula based on behavioral signals

* 🤖 **Machine Learning Integration**

  * Random Forest model predicts cognitive load level (Low / Medium / High)
  * Feature importance analysis for explainability

* 🌐 **AI-Powered Insights**

  * Cloud-based LLM (Groq/OpenAI-compatible)
  * Provides cognitive state, risk level, and improvement suggestions

* 📈 **Performance Visualization**

  * Interactive charts using Chart.js
  * Session comparison and performance breakdown

* 🗂 **History Management**

  * Stores all attempts in SQLite database
  * View past performance trends
  * Delete specific records

---

## 🧱 Tech Stack

### Frontend

* HTML, CSS, JavaScript
* Chart.js (data visualization)

### Backend

* Python (Flask)

### Database

* SQLite

### Machine Learning

* scikit-learn (Random Forest)

### AI Integration

* Groq API (LLM inference)

---

## 🏗️ System Architecture

```
User → Frontend (Typing UI)
     → JavaScript (Behavior Tracking)
     → Flask Backend
     → Cognitive Load Calculation
     → ML Model Prediction
     → AI API (Groq)
     → Results + Visualization
```

---

## ⚙️ How It Works

1. User selects difficulty level (Easy / Medium / Hard)
2. A paragraph is loaded based on difficulty
3. User types within a time limit
4. System tracks:

   * Speed
   * Accuracy
   * Pauses
   * Backspaces
5. Data is sent to backend
6. Cognitive load is calculated using weighted formula
7. ML model predicts load category
8. AI generates insights and recommendations
9. Results are displayed with charts and analysis

---

## 🧮 Cognitive Load Formula

```
Load Score =
(100 - accuracy) * 0.4 +
(pauses * 2) * 0.25 +
(backspaces * 1.5) * 0.2 +
(max(0, 50 - wpm)) * 0.15
```

---

## 🧠 Machine Learning Model

* Algorithm: Random Forest Classifier
* Features:

  * WPM
  * Accuracy
  * Pauses
  * Backspaces
* Output:

  * Low
  * Medium
  * High

---

## 🔐 Environment Variables

Create environment variable:

```
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run Locally

```bash
# Clone repository
git clone https://github.com/your-username/cognitive-load-analyzer.git

# Navigate to folder
cd cognitive-load-analyzer

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

Then open:

```
http://127.0.0.1:5000
```

---

## 🌍 Deployment

* Can be deployed on Render / Railway / VPS
* Requires setting environment variable for API key
* SQLite works for small-scale usage

---

## ⚠️ Limitations

* Uses synthetic dataset for ML training
* Cognitive load formula is heuristic-based
* AI insights are advisory, not diagnostic
* SQLite not suitable for large-scale production

---

## 🎯 Future Improvements

* User authentication system
* Real-time analytics dashboard
* Export reports (PDF/CSV)
* Advanced ML models with real-world datasets
* Adaptive difficulty based on performance

---

## 👨‍💻 Author

Developed by **Nitesh Bhoir**

---

## ⭐ Acknowledgment

This project explores the intersection of:

* Human-computer interaction
* Behavioral analytics
* Machine learning
* AI-assisted decision systems
