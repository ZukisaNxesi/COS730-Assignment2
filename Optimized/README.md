# Tasks 4 & 5: Optimised Implementation

## Overview

This folder contains the **optimised system** (Task 5) and the **empirical benchmark** (Task 6).  
The design is aligned with the redesigned sequence diagram from Task 4.

---

## Design Principles Applied

| Principle | How It Was Applied |
|-----------|-------------------|
| **Information Expert (GRASP)** | `ReviewerManager` owns all filtering; `EvaluationManager` owns all decision logic |
| **Controller Pattern (GRASP)** | `SubmissionController` is a thin 5-step coordinator |
| **Low Coupling** | `SubmissionRepository` introduced — controller no longer touches DB directly |
| **High Cohesion** | Each class has one focused responsibility |
| **Decision Table** | `EvaluationManager._decisionTable()` implements the formal Task 3 table |

---

## What Changed vs Baseline

| Area | Baseline | Optimised |
|------|----------|-----------|
| Method calls / submission | 22 | 7 |
| Reviewer selection | 3 separate calls | 1 call: `getAssignedReviewers()` |
| Decision + notify | Split across 2 classes | Encapsulated in `EvaluationManager` |
| DB access | Controller + ReviewerManager | Repository pattern only |
| Controller complexity (CC) | 6 | 4 |

---

## Optimised Interaction Flow

```
Researcher → UI.submitResearchOutput(data)
  UI → SubmissionController.submit(data)
    → Validator.validateFormat(data)              # [invalid] → return error
    → SubmissionRepository.save(data)             # [valid]
    → ReviewerManager.getAssignedReviewers()      # single call – expert handles all
        [internal] → repo.getAllReviewers()
        [internal] → _filter()  # conflict + workload combined
    loop [each reviewer]:
      → ReviewerManager.collectScore(record, submission)
    → EvaluationManager.evaluate(scores, submission)
        [internal] → _decisionTable(avg, consensus)   # implements Task 3 table
        [internal] → NotificationService.notify(outcome)
    return result → Researcher
```

---

## Decision Table (implemented in `_decisionTable()`)

| Rule | Consensus | Avg ≥ 75 | Avg ≥ 50 | Outcome |
|------|-----------|----------|----------|---------|
| R1 | No | — | — | revision |
| R2 | Yes | Yes | — | **accepted** |
| R3 | Yes | No | Yes | revision |
| R4 | Yes | No | No | **rejected** |

---

## How to Run

### Optimised System
```bash
python3 optimised.py
```

### Benchmark (Task 6 — 200 runs of both systems)
```bash
python3 benchmark.py
```

**Sample output:**
```json
{
  "baseline":  { "avg_time_ms": 20.78, "avg_calls": 22 },
  "optimised": { "avg_time_ms": 8.73,  "avg_calls": 7  }
}
```
