# Task 1: Baseline Implementation (Correctness Phase)

## Overview

This folder contains the **baseline implementation** — a faithful Python translation  
of the provided sequence diagram, with **no optimisations** applied.

Every message arrow in the diagram maps to exactly one method call in the code.

---

## Traceability: Diagram → Code

| Lifeline (Diagram) | Python Class | Methods |
|--------------------|-------------|---------|
| Researcher | *(actor — no class)* | Initiates via `UI.submitResearchOutput()` |
| UI | `UI` | `submitResearchOutput(data)` |
| SubmissionController | `SubmissionController` | `submit(data)` |
| Validator | `Validator` | `validateFormat(data)` |
| Database | `Database` | `saveSubmission(data)`, `fetchReviewers()` |
| ReviewerManager | `ReviewerManager` | `getAvailableReviewers()`, `filterConflicts()`, `checkWorkload()`, `assignReview()` |
| Reviewer | `Reviewer` | `submitScore(score)` |
| EvaluationManager | `EvaluationManager` | `startEvaluation()`, `saveScore()`, `calculateAverage()`, `checkConsensus()`, `applyRules()` |
| NotificationService | `NotificationService` | `notifyAcceptance()`, `notifyRejection()`, `notifyRevision()` |

---

## Interaction Flow (matches diagram exactly)

```
Researcher → UI.submitResearchOutput(data)
  UI → SubmissionController.submit(data)
    → Validator.validateFormat(data)          # alt [invalid] → return error
    → Database.saveSubmission(data)           # [valid]
    → ReviewerManager.getAvailableReviewers()
        → Database.fetchReviewers()
    → ReviewerManager.filterConflicts(list)
    → ReviewerManager.checkWorkload(list)
    loop [assign reviewers]:
      → ReviewerManager.assignReview()
    → EvaluationManager.startEvaluation()
    loop [each reviewer]:
      → Reviewer.submitScore()
      → EvaluationManager.saveScore()
    → EvaluationManager.calculateAverage()
    → EvaluationManager.checkConsensus()
    → EvaluationManager.applyRules()
    alt [accepted] → NotificationService.notifyAcceptance()
    alt [rejected] → NotificationService.notifyRejection()
    alt [revision] → NotificationService.notifyRevision()
```

---

## Known Design Issues (analysed in Task 2)

These issues are **intentionally preserved** in this baseline — they exist in the original diagram:

- `SubmissionController` depends on all 5 other subsystems (**God class**)
- Reviewer filtering split across 3 separate method calls (**low cohesion**)
- Decision logic (outcome) split between `EvaluationManager` and `SubmissionController`
- `NotificationService` dispatched by controller, not by the class that owns the outcome

---

## How to Run

```bash
python3 baseline.py
```
