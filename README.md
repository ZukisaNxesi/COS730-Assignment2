# COS 730 – Assignment 2
## From Behavioural Models to Optimised Implementation

**Student:** Zukisa Nxesi  
**Module:** COS 730 – Software Engineering  
**Institution:** University of Pretoria  
**Due Date:** 14 May 2026 @ 11:00  
**Language:** Python 3.11  
**System:** Intelligent Submission and Review System

---

## Repository Structure

```
COS730-Assignment2/
│
├── Original/               ← Task 1: Baseline Implementation
│   ├── baseline.py         # Faithful translation of the sequence diagram
│   └── README.md           # Task 1 explanation
│
├── Optimised/              ← Tasks 4 & 5: Redesigned system
│   ├── optimised.py        # Refactored, GRASP-aligned implementation
│   ├── benchmark.py        # Task 6: Empirical evaluation script
    ├── baseline.py
│   └── README.md           # Task 4 & 5 explanation
│
└── README.md               

## Task Summary

| Task | Description | Marks | Location |
|------|-------------|-------|----------|
| 1 | Baseline Implementation (Correctness Phase) | 15 | `Original/` |
| 2 | Design Analysis (GRASP principles) | 10 | PDF Report |
| 3 | Decision Table Modelling | 15 | PDF Report |
| 4 | Sequence Diagram Optimisation | 10 | PDF Report + `Optimised/` |
| 5 | Optimised Implementation | 20 | `Optimised/` |
| 6 | Empirical Evaluation & Comparison | 30 | `Optimised/benchmark.py` |

> **Full written report (PDF)** covers Tasks 2, 3, 4, and 6 in detail and is submitted separately on ClickUP.

---

## How to Run

### Requirements
```bash
python3 --version   # Python 3.8+ required
# No external libraries needed
```

### Run the Baseline System
```bash
cd Original
python3 baseline.py
```

**Expected output:**
```
Outcome      : accepted / revision / rejected
Notification : [NOTIFY] ...
Method calls : 22
```

### Run the Optimised System
```bash
cd Optimised
python3 optimised.py
```

**Expected output:**
```
Outcome      : accepted / revision / rejected
Notification : [NOTIFY] ...
Method calls : 7
```

### Run the Empirical Benchmark (Task 6)
```bash
cd Optimised
python3 benchmark.py
```

This runs **200 iterations** of both systems and prints a JSON comparison of:
- Average / min / max execution time (ms)
- Standard deviation
- Method call counts

---

## Key Results (Task 6 Summary)

| Metric | Baseline | Optimised | Improvement |
|--------|----------|-----------|-------------|
| Avg Execution Time | 20.78 ms | 11.92 ms | **2.56× faster** |
| Method Calls / Submission | 22 | 7 | **68% reduction** |
| Controller Cyclomatic Complexity | 6 | 4 | **−33%** |
| Controller Efferent Coupling | 5 | 4 | **−1 dependency** |

---

## Design Principles Applied (Optimised Version)

- **Information Expert (GRASP)** – Each class owns the behaviour it has data to support
- **Controller Pattern (GRASP)** – SubmissionController is a thin use-case coordinator
- **Low Coupling** – SubmissionRepository decouples persistence from the controller
- **High Cohesion** – ReviewerManager and EvaluationManager each have a single focused role
- **Decision Table** – `EvaluationManager._decisionTable()` directly implements the formal decision table from Task 3

---

## System Components

### Original (Baseline)
| Class | Diagram Lifeline | Role |
|-------|-----------------|------|
| `UI` | UI | Receives researcher input |
| `SubmissionController` | SubmissionController | God-class orchestrator (22 calls) |
| `Validator` | Validator | Format validation |
| `Database` | Database | Persistence + reviewer fetch |
| `ReviewerManager` | ReviewerManager | 3-step reviewer pipeline |
| `Reviewer` | Reviewer | Score submission |
| `EvaluationManager` | EvaluationManager | Scoring calculations |
| `NotificationService` | NotificationService | Outcome notifications |

### Optimised
| Class | Role | Key Change |
|-------|------|------------|
| `SubmissionController` | Thin coordinator | 22 → 7 method calls |
| `SubmissionRepository` | Persistence façade | New – decouples DB access |
| `ReviewerManager` | Full selection pipeline | 3 calls → 1 (`getAssignedReviewers`) |
| `EvaluationManager` | Scoring + decision + notify | Owns all evaluation logic |
| `NotificationService` | Notification delivery | Now called by EvaluationManager |
