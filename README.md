<div align="center">
  <h1>🚀 HirePanel.ai</h1>
  <p><b>An Autonomous AI Hiring Committee that vets candidates in under 30 seconds.</b></p>
  
  <p>
    Manual recruiting is cooked. 💀 <i>HirePanel.ai</i> is an elite multi-agent LLM squad that reads resumes, extracts evidence, catches red flags, debates the fit, and drops an executive summary—all before you finish your coffee.
  </p>

  <h3>📺 <a href="https://www.linkedin.com/posts/mahesh-nandigam_ai-agenticai-techcommunity-ugcPost-7474855620551241728-O5H9/?utm_source=share&utm_medium=member_desktop&rcm=ACoAADW99hsBJVeFIsEk7TLOg9YovphT7Sd-cWg">Watch the Live Video Demo</a></h3>

  [![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)]()
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)]()
  [![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white)]()
  [![Llama3](https://img.shields.io/badge/Llama_3-0466C8?style=for-the-badge)]()
</div>

<br />

## ✨ The MVP Experience

HirePanel is not a basic keyword scanner. It is a **multi-agent committee** where different AI personas (Tech Lead, HR Partner) analyze candidates from distinct perspectives and debate the final outcome. 

### Core Features
- **⚡ Blazing Fast (Groq Cloud):** Process and evaluate 3 candidates in parallel in under 30 seconds using Llama-3.3-70b on Groq.
- **🕵️ Resume-Driven Intelligence:** Zero generic templates. Every score, strength, and concern is directly cited from evidence found in the uploaded PDF.
- **⚖️ Dynamic Committee Debate:** The Tech Lead evaluates architecture and code depth, while the HR Partner evaluates career stability and culture fit. They disagree when appropriate.
- **📊 Real-time Dashboard:** Watch the live progress of agents as they evaluate candidates, flipping into a dynamic Score Matrix and Leaderboard.
- **📥 One-Click Export:** Download the entire evaluation session, including scores and the Decider's executive summary, straight to CSV.

---

## 🧠 Meet The Agents

1. **📄 Intake Agent:** Extracts candidate names, identifiers, and pure text from raw PDFs.
2. **🎯 JD Agent:** Maps candidate skills directly against the Job Description. Explicitly flags missing critical requirements.
3. **💻 GitHub Agent:** Analyzes open-source presence or infers code complexity and architecture patterns directly from the resume projects.
4. **👔 LinkedIn Agent:** Evaluates career trajectory, tenure stability, and professional progression.
5. **🛠️ Tech Lead Agent:** Evaluates the candidate strictly on technical depth and system design capability.
6. **🤝 HR Partner Agent:** Evaluates organizational fit, tenure, and communication potential.
7. **👑 Decider Agent:** The final boss. Takes the mathematical weights, reads the Tech Lead and HR debate, and outputs an executive verdict (`HIRE`, `WAITLIST`, or `REJECT`).

---

## 🛠️ Tech Stack

**Frontend:**
- React (Vite)
- TailwindCSS (Glassmorphism UI)
- Isometric Wave Animations

**Backend:**
- Python 3.10+
- FastAPI
- PyMuPDF (PDF parsing)
- Groq Cloud API (Llama-3.3-70b-versatile)

---

## 🚀 Quickstart Guide

### 1. Clone the repository
```bash
git clone https://github.com/Mahesh-Nandigam/HirePanel.Ai.git
cd HirePanel.Ai
```

### 2. Set up the Backend (FastAPI)
Open a terminal and set up your Python environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your Groq API keys (we use a rotator to bypass rate limits on the free tier):
```env
# .env
DEMO_MODE=True
GROQ_API_KEY_1=your_groq_key_here
GROQ_API_KEY_2=your_second_groq_key_here
```

Start the backend server:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Set up the Frontend (React/Vite)
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

### 4. Run the Platform
Open your browser and navigate to the local development URL provided by Vite (usually `http://localhost:5173`).

Paste a Job Description, upload a few PDF resumes, and watch the AI committee go to work!

---

<div align="center">
  <i>Built for the future of technical recruiting. 🚀</i>
</div>
