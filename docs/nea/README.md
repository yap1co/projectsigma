# NEA Documentation - README

## Overview

This directory contains the complete NEA (Non-Exam Assessment) documentation for **Project Sigma: University Course Recommender System**, an A-Level Computer Science project.

## Document Structure

The documentation follows AQA A-Level Computer Science NEA requirements with five main sections:

### Core Documentation Files

1. **[00_PROJECT_OVERVIEW.md](00_PROJECT_OVERVIEW.md)** - Executive summary, context, and technology stack
2. **[01_ANALYSIS.md](01_ANALYSIS.md)** - Problem definition, stakeholder interviews, requirements specification
3. **[02_DESIGN.md](02_DESIGN.md)** - System architecture, database design, algorithms, UI wireframes, test plan
4. **[03_DEVELOPMENT.md](03_DEVELOPMENT.md)** - Implementation evidence, code commentary, iterative sprints
5. **[04_TESTING.md](04_TESTING.md)** - Comprehensive testing (unit, integration, system, UAT, NFR)
6. **[05_EVALUATION.md](05_EVALUATION.md)** - Success criteria review, stakeholder feedback, lessons learned

## How to Use This Documentation

### For NEA Submission

**Option 1: Submit Markdown Files Directly (if allowed)**
```bash
# All files are in docs/nea/
00_PROJECT_OVERVIEW.md
01_ANALYSIS.md
02_DESIGN.md
03_DEVELOPMENT.md
04_TESTING.md
05_EVALUATION.md
```

**Option 2: Convert to PDF for Submission**

1. **Using VS Code Extension (Recommended):**
   - Install "Markdown PDF" extension
   - Open each .md file
   - Right-click → "Markdown PDF: Export (PDF)"
   - Combine PDFs using Adobe Acrobat or similar

2. **Using Pandoc (Command Line):**
```bash
cd docs/nea

# Convert individual sections
pandoc 01_ANALYSIS.md -o 01_ANALYSIS.pdf
pandoc 02_DESIGN.md -o 02_DESIGN.pdf
# ... etc

# Or combine all into single PDF
pandoc 00_PROJECT_OVERVIEW.md 01_ANALYSIS.md 02_DESIGN.md 03_DEVELOPMENT.md 04_TESTING.md 05_EVALUATION.md -o NEA_Project_Sigma_Complete.pdf
```

3. **Using Online Converter:**
   - Visit: https://www.markdowntopdf.com/
   - Upload each .md file
   - Download PDF

### For Development Reference

Read files in order (00 → 05) to understand the complete project lifecycle.

## Documentation Standards

### Markdown Features Used

- **Headings:** Clear hierarchy (# → ## → ###)
- **Code Blocks:** Syntax-highlighted with language tags (```python, ```sql, ```typescript)
- **Tables:** Structured data (requirements, tests, etc.)
- **Links:** Cross-references to code files
- **Lists:** Bullet points and numbered lists
- **Emphasis:** **Bold** for important terms, *italic* for emphasis

### Code References

Code examples reference actual project files:
- `[server/recommendation_engine.py](../../server/recommendation_engine.py)` → links to source
- Line numbers provided for specific segments (e.g., "lines 724-795")

### Evidence Standards

Each major claim includes:
- **Evidence:** Test results, code snippets, user feedback
- **Analysis:** Interpretation of evidence
- **Screenshots:** (Placeholders for actual screenshots - add your own)

## Completing the Documentation

### Fill in Placeholders

1. **Personal Information (00_PROJECT_OVERVIEW.md):**
   - Replace `[Your Name]`, `[Centre Number]`, `[Candidate Number]`
   - Update abstract with your summary

2. **Stakeholder Details (01_ANALYSIS.md):**
   - Add real interview dates and participant names
   - Fill in interview responses with actual data
   - Update problem definition with your perspective

3. **Screenshots (04_TESTING.md):**
   - Capture actual test execution screenshots
   - Screenshot UAT sessions with participants
   - Take UI screenshots for system tests

4. **Personal Reflection (05_EVALUATION.md):**
   - Customize "Personal Reflection" section (9.0)
   - Add your genuine challenges and learnings
   - Update career implications with your goals

### Adding Evidence

**Recommended Evidence to Include:**

1. **Analysis:**
   - Stakeholder interview notes (scanned/typed)
   - Problem research (UCAS screenshots, competitor analysis)

2. **Design:**
   - Hand-drawn wireframes (scanned)
   - Database diagrams (screenshot from tool)
   - Algorithm flowcharts (draw.io or similar)

3. **Development:**
   - Git commit history (`git log --oneline > commits.txt`)
   - Code screenshots (VS Code with line numbers)
   - Error messages and fixes (before/after)

4. **Testing:**
   - Test execution output (terminal screenshots)
   - UAT session photos (participants using system)
   - Performance test graphs (Excel chart)

5. **Evaluation:**
   - User feedback quotes (emails/messages)
   - Comparison before/after scope reduction

## AQA Marking Criteria Mapping

### Analysis (20 marks)
- **Problem definition:** Section 1.1-1.3
- **Stakeholder analysis:** Section 1.2, 3.0
- **Research:** Section 2.0
- **Requirements:** Section 4.0
- **Computational methods:** Section 6.0

### Design (20 marks)
- **System design:** Section 1.0
- **Database design:** Section 2.0
- **Algorithm design:** Section 3.0
- **UI design:** Section 4.0
- **Test plan:** Section 5.0

### Development (20 marks)
- **Implementation evidence:** Section 3.0
- **Code commentary:** Section 3.1
- **Iterative development:** Section 2.0
- **Error handling:** Section 3.2
- **Version control:** Section 4.0

### Testing (20 marks)
- **Unit tests:** Section 2.0
- **Integration tests:** Section 3.0
- **System tests:** Section 4.0
- **UAT:** Section 5.0
- **NFR testing:** Section 6.0

### Evaluation (20 marks)
- **Success criteria:** Section 1.0
- **Limitations:** Section 2.0
- **Improvements:** Section 4.0
- **Stakeholder feedback:** Section 5.0
- **Reflection:** Section 9.0

## Tips for Strong NEA Submission

### Content Tips

1. **Be Specific:** Use actual numbers, dates, names (where appropriate)
2. **Show Evidence:** Every claim needs supporting evidence
3. **Be Critical:** Acknowledge limitations and areas for improvement
4. **Link Everything:** Show how Analysis → Design → Development → Testing → Evaluation
5. **Use Technical Terms:** Demonstrate understanding (normalization, parameterized queries, etc.)

### Presentation Tips

1. **Consistent Formatting:** Use same heading styles throughout
2. **Clear Code Blocks:** Always specify language for syntax highlighting
3. **Label Everything:** Figure 1, Table 1, Test Case UT1, etc.
4. **Page Numbers:** Add when converting to PDF
5. **Table of Contents:** Generate automatically with Pandoc

### Common Pitfalls to Avoid

❌ Generic problem definition (be specific to your project)  
❌ Missing test evidence (include screenshots/output)  
❌ No code commentary (explain *why*, not just *what*)  
❌ Superficial evaluation (be honestly critical)  
❌ Insufficient technical depth (show understanding of algorithms)

✅ Specific, measurable requirements  
✅ Detailed algorithm pseudocode  
✅ Comprehensive test coverage with results  
✅ Critical reflection on limitations  
✅ Evidence of iterative development

## Estimated Reading Time

- **Analysis:** 20 minutes
- **Design:** 30 minutes
- **Development:** 40 minutes
- **Testing:** 30 minutes
- **Evaluation:** 25 minutes
- **Total:** ~2.5 hours

## Contact / Questions

For questions about this documentation structure or Project Sigma:
- See main [README.md](../../README.md) in project root
- Check [PROJECT_STATUS.md](../PROJECT_STATUS.md) for current state
- Review [QUICK_REFERENCE.md](../QUICK_REFERENCE.md) for setup

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-02-01 | Initial comprehensive documentation |
| 1.1 | [Your Date] | Added screenshots and personalized content |

---

**Good luck with your NEA submission! 🎓**
