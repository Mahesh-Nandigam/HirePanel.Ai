# Detailed Task Checklist - PanelAI Recruiter

- [x] **Task 1:** Install backend Python dependencies (`google-generativeai`, `fastapi`, `uvicorn`, `python-multipart`, `pypdf`, `reportlab`)
- [x] **Task 2:** Setup clean backend directory structure (`src/agents/`, `src/utils/`, `data/`)
- [x] **Task 3:** Build JD Agent (Stage 1) to parse raw JD text into a structured JSON `JD_Context`
- [x] **Task 4:** Test JD Agent (Stage 1) in the terminal with sample JDs and verify JSON output quality
- [x] **Task 5:** Build Intake Agent to parse PDF resumes and extract name, GitHub URL, and LinkedIn URL (mark "No" if missing)
- [x] **Task 6:** Test Intake Agent with test PDFs and verify extracted links table
- [x] **Task 7:** Build GitHub Agent to evaluate commit history, consistency, stars, and GSoC
- [x] **Task 8:** Test GitHub Agent with mock JSON profiles and verify the X/10 score output
- [x] **Task 9:** Build LinkedIn Agent to evaluate work tenure, stability, and career progression
- [x] **Task 10:** Test LinkedIn Agent with mock JSON work histories and verify the Y/10 score output
- [x] **Task 11:** Build Resume Agent to evaluate CV text for skill matching
- [x] **Task 12:** Test Resume Agent with mock resume text and verify the Z/10 score output
- [x] **Task 13:** Build JD Agent (Stage 2 - Alignment) to calculate the mathematical alignment score using the 50/20/15/15 formula and output structured JSON
- [x] **Task 14:** Test JD Agent (Stage 2 - Alignment) and verify score calculation accuracy
- [x] **Task 15:** Build Tech Lead Agent and HR Agent debate prompts and response handlers
- [x] **Task 16:** Build Decider Agent to review debate history, check for consensus, and output the final W/100 score
- [x] **Task 17:** Connect all agents into a unified pipeline script `test_pipeline.py` and run a complete mock candidates simulation in the CLI
- [x] **Task 18:** Set up FastAPI backend server in `src/main.py`
- [x] **Task 19:** Implement the `/api/intake` endpoint (PDF parsing & link extraction)
- [x] **Task 20:** Implement the `/api/vet-batch` endpoint (parallel async execution engine)
- [x] **Stage 1:** Scaffold Vite/React in `/frontend` with Tailwind v3, and build the JD Input Screen
- [x] **Stage 2:** Build the Resume Upload Screen
- [x] **Stage 3:** Build the Intake Table
- [ ] **Stage 4:** Build the Start Vetting Button (Trigger backend API)
- [ ] **Stage 5:** Build Candidate Cards Grid (Data Flow First)
- [ ] **Stage 6:** Build Leaderboard Table
- [ ] **Stage 7:** Build Chat Drawer
- [ ] **Stage 8:** Add Card Flip Animation (Polish)
- [ ] **Stage 9:** Add Auto-Scroll to Leaderboard (Polish)
- [ ] **Stage 10:** Implement PDF Export integration

---

### 🚀 Phase 2: Upgradations (For Final Round Evaluation)
- [ ] **Upgrade 1:** Implement Vector Embeddings & Cosine Similarity in the Resume Agent (Hybrid Scoring)
- [ ] **Upgrade 2:** Add Live Web Scraping for LinkedIn/GitHub (using Proxycurl/GitHub APIs if we get sponsor credits)
as usaul 