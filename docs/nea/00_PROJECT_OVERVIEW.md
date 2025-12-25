# NEA Project Sigma - University Course Recommender System

**Student Name:** [Your Name]  
**Centre Number:** [Your Centre Number]  
**Candidate Number:** [Your Candidate Number]  
**Exam Board:** AQA A-Level Computer Science  
**Project Title:** University Course Recommender System (Project Sigma)

---

## Abstract

[Brief summary of the project - 150-200 words covering:
- The problem being solved
- Who the stakeholders are
- The solution approach
- Key technologies used
- Main outcomes/achievements]

---

## Project Context

This project aims to help A-level students make informed decisions about university course selection by providing personalized recommendations based on:
- Academic qualifications (predicted A-level grades)
- Career interests and aspirations
- Financial considerations (tuition fees, future earnings)
- Personal preferences (location, institution type)
- Graduate employment outcomes

The system integrates official HESA (Higher Education Statistics Agency) Discover Uni data, providing evidence-based recommendations grounded in real graduate outcomes.

---

## Technology Stack

- **Backend:** Python 3.11, Flask
- **Frontend:** React, Next.js, TypeScript
- **Database:** PostgreSQL
- **Data Source:** HESA Discover Uni (C25061 dataset)
- **Development Environment:** VS Code, Windows, Git

---

## Project Structure (Physical Organization)

### Root Level Structure

```
projectsigma/
├── .git/                   # Git version control
├── .gitignore              # Git ignore rules
├── README.md               # Project overview & quick start
├── package.json            # Root npm scripts
│
├── venv/                   # Python virtual environment
│
├── data/                   # 📊 HESA CSV Data (7 files)
├── server/                 # 🐍 Backend (Python/Flask)
├── client/                 # ⚛️ Frontend (React/Next.js)
└── docs/                   # 📚 All Documentation
```

**Rationale for Structure:**
- **Clear Separation of Concerns:** Backend, frontend, and documentation are completely isolated
- **Modularity:** Each component can be developed, tested, and deployed independently
- **Professional Standards:** Follows industry conventions for Flask + Next.js projects
- **Maintainability:** Easy for new developers to understand and navigate

### Key Components

| Folder | Purpose | Technologies |
|--------|---------|-------------|
| `data/` | Raw HESA CSV files (478 universities, 30,835 courses) | CSV data files |
| `server/` | REST API, recommendation engine, business logic | Python, Flask, PostgreSQL |
| `client/` | User interface, dashboard, forms | React, Next.js, TypeScript |
| `docs/` | NEA documentation, technical guides | Markdown |

---

## Key Features

1. **Personalized Recommendations:** Weighted scoring algorithm considering multiple factors
2. **HESA Data Integration:** Real employment outcomes, salaries, and entry requirements
3. **Interactive Dashboard:** User-friendly interface for exploring courses
4. **Profile Customization:** Save preferences and predicted grades
5. **Course Comparison:** View detailed outcomes data side-by-side

---

## Project Scope (Post-Reduction)

- **Database Tables:** 23 total (15 core application + 7 HESA + 1 migrations)
- **Data Files:** 7 HESA CSV files (79% reduction from original 33 files)
- **Code Size:** ~14,000 lines
- **HESA Tables:** `hesa_institution`, `hesa_kiscourse`, `hesa_employment`, `hesa_entry`, `hesa_gosalary`, `hesa_joblist`, `hesa_leo3`

---

## Documentation Structure

This NEA documentation is organized into the following sections following AQA A-Level requirements:

1. **Analysis** - Problem definition, stakeholder analysis, requirements
2. **Design** - System architecture, algorithms, data structures, UI design, test plan
3. **Development** - Implementation evidence, code commentary, iterative development
4. **Testing** - Comprehensive test plan execution with evidence
5. **Evaluation** - Success criteria assessment, user feedback, improvements
