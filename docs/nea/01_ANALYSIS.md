# Analysis

## 1. Problem Definition

### 1.1 The Problem

[Describe the problem in detail:
- What difficulties do students face when choosing university courses?
- Why is the current process inadequate?
- What information is hard to find or compare?
- What are the consequences of poor decision-making?]

**Key Issues:**
- Information overload: 5000+ courses across 140+ UK universities
- Difficulty comparing employment outcomes across institutions
- Lack of personalized filtering based on grades and interests
- Time-consuming manual research process
- Disconnect between course marketing and real graduate outcomes

### 1.2 Target Users (Stakeholders)

**Primary Stakeholder:** A-level students (Year 13, ages 17-18) preparing for university applications

**Characteristics:**
- [Academic background, predicted grades]
- [Career interests and goals]
- [Technical capability]
- [Decision-making challenges]

**Secondary Stakeholders:**
- Parents/guardians seeking to support their children
- Careers advisors in schools
- [Your own use case: A-level student and NEA developer]

### 1.3 Current Solution Analysis

[Analyze existing solutions:
- UCAS Search: Pros and cons
- University websites: What they offer/lack
- Whatuni, UniCompare, etc.: Strengths and weaknesses]

**Why a new solution is needed:**
[Explain the gap that Project Sigma fills]

---

## 2. Research

### 2.1 Data Source Research

**HESA Discover Uni (C25061 Dataset):**
- Official UK higher education statistics
- Covers: employment outcomes, graduate salaries, entry requirements
- Data structure: [Explain key tables and relationships]
- Coverage: [Number of institutions, courses, years]

### 2.2 Technical Research

**Algorithm Research:**
- Weighted scoring algorithms for recommendation systems
- Multi-criteria decision making
- Data normalization techniques

**Database Research:**
- PostgreSQL for relational data
- Schema design for efficient queries
- Indexing strategies

**UI/UX Research:**
- Dashboard design patterns
- Filter and search interfaces
- Data visualization best practices

---

## 3. Stakeholder Interviews

### 3.1 Interview 1: [Student Name/Role]

**Date:** [Date]  
**Format:** [In-person/Online]

**Questions Asked:**
1. [Question about university selection challenges]
2. [Question about information needs]
3. [Question about preferred features]
4. [Question about decision criteria]

**Key Findings:**
- [Important insight 1]
- [Important insight 2]
- [Important insight 3]

**Requirements Derived:**
- [Functional requirement]
- [Non-functional requirement]

### 3.2 Interview 2: [Parent/Careers Advisor]

[Repeat structure]

---

## 4. Requirements Specification

### 4.1 Functional Requirements

| ID | Requirement | Priority | Source |
|----|------------|----------|--------|
| FR1 | System shall allow users to input predicted A-level grades | High | Student Interview 1 |
| FR2 | System shall allow users to select career interests | High | Student Interview 1 |
| FR3 | System shall generate personalized course recommendations | High | Problem definition |
| FR4 | System shall display employment outcomes for each course | High | Student Interview 2 |
| FR5 | System shall allow filtering by location, fees, entry requirements | Medium | Stakeholder analysis |
| FR6 | System shall save user profiles and preferences | Medium | Student Interview 1 |
| FR7 | System shall display graduate salary data (LEO3) | High | Data research |
| FR8 | System shall show common job types for graduates | Medium | Student Interview 2 |
| FR9 | System shall allow course comparison | Low | UX research |
| FR10 | System shall provide course details modal | Medium | Design consideration |

### 4.2 Non-Functional Requirements

| ID | Requirement | Priority | Measurable Criteria |
|----|------------|----------|---------------------|
| NFR1 | **Performance:** Recommendations generated within 3 seconds | High | Timed test with 100 courses |
| NFR2 | **Usability:** Interface navigable by A-level students without training | High | User testing feedback |
| NFR3 | **Reliability:** System available 99% of the time | Medium | Uptime monitoring |
| NFR4 | **Scalability:** Support 5000+ courses without performance degradation | High | Load testing |
| NFR5 | **Maintainability:** Code documented and modular | High | Code review checklist |
| NFR6 | **Security:** User data encrypted and password-protected | High | Security audit |
| NFR7 | **Data Accuracy:** HESA data correctly imported and mapped | High | Data validation tests |
| NFR8 | **Accessibility:** WCAG 2.1 AA compliance | Low | Accessibility testing |

### 4.3 Success Criteria

The project will be considered successful if:

1. ✅ **Accurate Recommendations:** Algorithm produces relevant courses matching user criteria (validated through user testing with 5+ students)
2. ✅ **Complete Data Pipeline:** All 7 HESA tables successfully imported and integrated
3. ✅ **Functional UI:** Dashboard allows profile setup, viewing recommendations, and exploring course details
4. ✅ **Performance Target:** Page load < 2s, recommendations generated < 3s
5. ✅ **User Satisfaction:** 80%+ positive feedback from stakeholder testing
6. ✅ **Code Quality:** Modular architecture, comprehensive error handling, documented code

---

## 5. Limitations and Constraints

### 5.1 Technical Constraints
- HESA data limited to full-time undergraduate courses
- Performance constraints with large dataset (5000+ courses)
- Development time: [Your NEA timeline]

### 5.2 Scope Constraints
- Focus on UK universities only
- No direct UCAS application integration
- No real-time data updates (static HESA snapshot)

### 5.3 User Constraints
- Requires internet connection
- Requires modern web browser
- Assumes users have predicted A-level grades

---

## 6. Computational Methods Justification

### 6.1 Weighted Scoring Algorithm

**Why:** [Explain why weighted scoring is appropriate for multi-criteria recommendation]

**Alternative Considered:** [e.g., Machine learning collaborative filtering]
**Justification for Choice:** [Why weighted scoring is better for this problem]

### 6.2 Relational Database (PostgreSQL)

**Why:** [Structured data, complex relationships, SQL queries]

**Alternative Considered:** [e.g., NoSQL database]
**Justification for Choice:** [Why relational model fits HESA data]

### 6.3 React/Next.js Frontend

**Why:** [Component-based architecture, TypeScript type safety, modern UX]

**Alternative Considered:** [e.g., Plain HTML/CSS/JS]
**Justification for Choice:** [Why React is appropriate for complexity]

---

## 7. Summary

[Conclude the Analysis section with:
- Key problems identified
- Stakeholder needs validated
- Requirements clearly defined
- Success criteria established
- Technical approach justified]

**Next Steps:** Proceed to Design phase with requirements as foundation.
