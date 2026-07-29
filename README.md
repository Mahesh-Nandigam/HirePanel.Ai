

  # HirePanel.ai
  ### The Autonomous AI Hiring Committee that Vets Candidates in less than 30 seconds


  HirePanel.ai is a multi-agent screening system that automates the initial stages of technical recruiting. By parsing uploaded resumes, analyzing candidate codebases on GitHub, evaluating work history on LinkedIn, and running a structured debate between virtual Tech Lead and HR roles, HirePanel delivers a comprehensive candidate evaluation and consensus verdict in under 30 seconds.

  ### Links
  - [Live Video Demo](https://www.linkedin.com/posts/mahesh-nandigam_ai-agenticai-techcommunity-ugcPost-7474855620551241728-O5H9/?utm_source=share&utm_medium=member_desktop&rcm=ACoAADW99hsBJVeFIsEk7TLOg9YovphT7Sd-cWg)
  - [Live App Link](https://hirepanel-ai.vercel.app)
</div>

---

## Architecture and Agent Choreography

HirePanel.ai structures candidate screening as a pipeline of cooperative, specialized AI agents. This structure ensures that candidates are evaluated from multiple perspectives (such as technical depth and team alignment) before a final decision is reached.

```mermaid
flowchart TD
    %% Define styles for clean appearance
    classDef input fill:#e1f5fe,stroke:#01579b,stroke-width:1px;
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:1px;
    classDef process fill:#efebe9,stroke:#3e2723,stroke-width:1px;
    classDef output fill:#e8f5e9,stroke:#1b5e20,stroke-width:1px;

    subgraph Inputs [1. Inputs]
        JD[Job Description]
        PDF[PDF Resumes <br/> Supports bulk upload from 1 up to 10,000 files]
    end
    class Inputs,JD,PDF input;

    subgraph IntakeStage [2. Intake and Parsing]
        Intake[Intake Agent]
        PDF --> Intake
    end
    class IntakeStage,Intake process;

    subgraph RoutingStage [3. URL and Data Extraction]
        Parsed[Parsed Candidate Profile]
        Intake --> Parsed
    end
    class RoutingStage,Parsed process;

    subgraph Extractors [4. Parallel Assessment]
        GH_Agent[GitHub Agent]
        LI_Agent[LinkedIn Agent]
        JD_Agent[JD Agent]
        Res_Agent[Resume Agent]
        
        Parsed -->|Extracts and routes GitHub URL| GH_Agent
        Parsed -->|Extracts and routes LinkedIn URL| LI_Agent
        Parsed -->|Routes resume text| JD_Agent
        Parsed -->|Routes resume text| Res_Agent
    end
    class Extractors,GH_Agent,LI_Agent,JD_Agent,Res_Agent agent;

    subgraph EvaluationPanel [5. Debate Committee]
        TechLead[Tech Lead Agent<br/>Evaluates system design & code depth]
        HR[HR Partner Agent<br/>Evaluates longevity & culture fit]
        
        GH_Agent --> TechLead
        Res_Agent --> TechLead
        LI_Agent --> HR
        JD_Agent --> HR
        
        TechLead <-->|Consensus debate & score matrix| HR
    end
    class EvaluationPanel,TechLead,HR agent;

    subgraph DecisionStage [6. Verdict Rendering]
        Decider[Decider Agent]
        Verdict[Final Verdict<br/>HIRE, WAITLIST, or REJECT]
        
        TechLead --> Decider
        HR --> Decider
        Decider --> Verdict
    end
    class DecisionStage,Decider,Verdict output;
```

---

## Key Features

- **Fast Evaluations (Groq Cloud):** Processes candidate profiles concurrently using Llama-3.3-70b on Groq, completing evaluations in less than 30 seconds.
- **Evidence-Based Reasoning:** Extracts candidate details directly from uploaded PDFs, ensuring all strengths and areas of concern are supported by direct citations.
- **Dynamic Peer Review:** Employs a debate between Tech Lead and HR Partner personas to balance technical competence with long-term retention and team fit.
- **Resilient API Layer:** Includes a Groq API Key Rotator supporting up to 10 keys to prevent rate limit blocks, alongside a local fallback to Ollama (running gemma3:4b or llama3) for offline stability.
- **Real-Time Dashboards:** Features a dashboard tracking active agent status, detailed side-by-side agent debate logs, and candidate rankings.
- **Data Export:** Supports exporting evaluation metrics, notes, and final decisions to CSV.

---

## Meet The Committee

| Agent | Focus Area | Source Inputs | Key Output |
| :--- | :--- | :--- | :--- |
| **Intake Agent** | Information Extraction | Raw PDF Resume | Structured Candidate JSON (URLs, Text, Contact) |
| **JD Agent** | Role Relevance Alignment | Resume Text + Job Description | Score alignment, missing requirements, critical fits |
| **GitHub Agent** | Open Source & Project Depth | GitHub URL / Resume Projects | Code complexity, architecture patterns, repo stats |
| **LinkedIn Agent** | Career Stability & Longevity | LinkedIn URL / Career History | Work tenure, promotion frequency, career growth indicators |
| **Tech Lead Agent** | Technical Competence | JD + GitHub + Resume outputs | System design rating, code depth, core technical score |
| **HR Partner Agent** | Culture & Organizational Fit | LinkedIn + Resume outputs | Communication skills, teamwork potential, longevity rating |
| **Decider Agent** | Final Panel Consensus | Tech Lead & HR Debate + Scores | Final decision (HIRE, WAITLIST, REJECT) & Executive Summary |

---

## Codebase Structure

```directory
hirepanel.ai/
├── src/
│   ├── main.py                 # FastAPI Application (Endpoints: /api/intake, /api/evaluate)
│   ├── agents/
│   │   ├── intake_agent.py     # Parses PDFs and extracts structured details
│   │   ├── jd_agent.py         # Matches candidate experiences to the target job description
│   │   ├── github_agent.py     # Analyzes developer profiles and code repository footprints
│   │   ├── linkedin_agent.py   # Analyzes career timelines and workplace longevity
│   │   ├── resume_agent.py     # Reviews details, credentials, and achievements
│   │   ├── debate_agents.py    # Powers the Tech Lead and HR debate cycle
│   │   └── decider_agent.py    # Formulates final decision and executive summaries
│   └── utils/
│       └── groq_client.py      # LLM client with Groq Key Rotator & Local Ollama Fallback
├── frontend/
│   ├── src/                    # React (Vite) Frontend Components & Dashboard UI
│   ├── package.json
│   └── vite.config.js
├── Dockerfile                  # Application deployment packaging
└── requirements.txt            # Backend Python dependencies
```

---

## Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Optional] Ollama running locally (for local model fallbacks)

### 1. Clone the Repository
```bash
git clone https://github.com/Mahesh-Nandigam/HirePanel.Ai.git
cd HirePanel.Ai
```

### 2. Set Up the Backend (FastAPI)
Create a Python virtual environment and install the required dependencies:
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your Groq API keys:
```env
# .env
DEMO_MODE=True
GROQ_API_KEY=gsk_your_primary_key_here
GROQ_API_KEY_1=gsk_your_second_key_here
GROQ_API_KEY_2=gsk_your_third_key_here
```
> [!NOTE]
> Setting DEMO_MODE=True tells the system to bypass local Ollama setups and prioritize the Groq cloud endpoint for faster evaluation times.

Start the backend server:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Set Up the Frontend (React + Vite)
Open a new terminal window or tab and set up the interface:
```bash
cd frontend
npm install
npm run dev
```

### 4. Run and Test the Application
1. Open your browser to http://localhost:5173.
2. Input a Job Description (or use the preloaded template).
3. Upload candidate resumes (PDF format).
4. Click Start Evaluation and watch the AI hiring committee execute the interview assessment live!

---

## Reliability & Fail-safes
If you run out of Groq API limits:
1. The GroqKeyRotator immediately switches to the next available environment key.
2. If all API keys run dry, or if you disable DEMO_MODE (DEMO_MODE=False), the backend falls back gracefully to a locally running Ollama instance (gemma3:4b or llama3) to ensure data evaluation never stops.

---

<div align="center">
  <i>Designed and built for the future of technical recruiting.</i>
</div>
