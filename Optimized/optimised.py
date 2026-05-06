"""
COS 730 – Assignment 2
Task 5: Optimised Implementation
Aligned with the redesigned sequence diagram (Task 4).
Key changes:
  - SubmissionController is a thin Controller (GRASP)
  - ReviewerManager owns all reviewer logic (Information Expert)
  - EvaluationManager owns scoring AND decision logic
  - NotificationService is invoked by EvaluationManager, not the controller
  - Database access is encapsulated; controller never calls DB directly
"""

import time
import random


# ──────────────────────────────────────────────
# Domain objects (unchanged)
# ──────────────────────────────────────────────

class Submission:
    def __init__(self, data: dict):
        self.data = data
        self.submission_id = random.randint(1000, 9999)


class ReviewerRecord:
    def __init__(self, reviewer_id: int, conflicts: list, workload: int):
        self.reviewer_id = reviewer_id
        self.conflicts   = conflicts
        self.workload    = workload


# ──────────────────────────────────────────────
# Validator  – unchanged responsibility
# ──────────────────────────────────────────────

class Validator:
    def validateFormat(self, data: dict) -> bool:
        required = ["title", "author", "content"]
        return all(field in data and data[field] for field in required)


# ──────────────────────────────────────────────
# SubmissionRepository  (replaces raw Database access from controller)
# Single responsibility: persistence only
# ──────────────────────────────────────────────

class SubmissionRepository:
    """Controller no longer calls Database directly (decoupled)."""

    def __init__(self):
        self._store: dict = {}
        self._reviewers: list[ReviewerRecord] = [
            ReviewerRecord(1, ["Topic A"],   2),
            ReviewerRecord(2, [],            1),
            ReviewerRecord(3, ["author_x"],  3),
            ReviewerRecord(4, [],            0),
            ReviewerRecord(5, ["Topic C"],   2),
        ]

    def save(self, data: dict) -> str:
        sid = random.randint(1000, 9999)
        self._store[sid] = data
        time.sleep(0.002)
        return f"SAVED:{sid}"

    def getAllReviewers(self) -> list[ReviewerRecord]:
        time.sleep(0.002)
        return list(self._reviewers)


# ──────────────────────────────────────────────
# ReviewerManager  – now owns ALL reviewer logic
# GRASP: Information Expert (has reviewer data + filtering knowledge)
# ──────────────────────────────────────────────

class ReviewerManager:
    MAX_WORKLOAD    = 3
    REVIEWERS_NEEDED = 3

    def __init__(self, repo: SubmissionRepository):
        self._repo = repo

    def getAssignedReviewers(self, submission: Submission) -> list:
        """
        Single entry point: fetch → filter conflicts → filter workload → assign.
        Eliminates the 4 separate round-trips in the baseline.
        """
        all_reviewers = self._repo.getAllReviewers()
        eligible = self._filter(all_reviewers, submission)
        return eligible[:self.REVIEWERS_NEEDED]

    def _filter(self, reviewers: list, submission: Submission) -> list:
        author = submission.data.get("author", "")
        topic  = submission.data.get("topic",  "")
        return [
            r for r in reviewers
            if author not in r.conflicts
            and topic  not in r.conflicts
            and r.workload < self.MAX_WORKLOAD
        ]

    def collectScore(self, record: ReviewerRecord, submission: Submission) -> float:
        time.sleep(0.001)
        return round(random.uniform(50, 100), 2)


# ──────────────────────────────────────────────
# NotificationService  – same interface
# ──────────────────────────────────────────────

class NotificationService:
    def notify(self, outcome: str, submission: Submission) -> str:
        time.sleep(0.001)
        msgs = {
            "accepted": f"[NOTIFY] Accepted – ID={submission.submission_id}",
            "rejected": f"[NOTIFY] Rejected – ID={submission.submission_id}",
            "revision": f"[NOTIFY] Revision – ID={submission.submission_id}",
        }
        return msgs.get(outcome, "[NOTIFY] Unknown outcome")


# ──────────────────────────────────────────────
# EvaluationManager  – owns decision logic (Decision Table)
# GRASP: Information Expert + Pure Fabrication
# ──────────────────────────────────────────────

class EvaluationManager:
    CONSENSUS_THRESHOLD = 20.0
    ACCEPT_THRESHOLD    = 75.0
    REVISE_THRESHOLD    = 50.0

    def __init__(self, notification_service: NotificationService):
        self._notifier = notification_service

    def evaluate(self, scores: list, submission: Submission) -> dict:
        """
        Encapsulates: calculateAverage + checkConsensus + applyRules + notify.
        Returns outcome dict.
        """
        average   = sum(scores) / len(scores) if scores else 0.0
        consensus = (max(scores) - min(scores)) <= self.CONSENSUS_THRESHOLD \
                    if len(scores) >= 2 else True

        outcome = self._decisionTable(average, consensus)
        note    = self._notifier.notify(outcome, submission)
        return {"outcome": outcome, "average": average,
                "consensus": consensus, "notification": note}

    def _decisionTable(self, average: float, consensus: bool) -> str:
        """
        Implements the formal Decision Table (Task 3).
        Rule mapping:
          R1: consensus=F  → revision   (regardless of score)
          R2: consensus=T, avg>=75 → accepted
          R3: consensus=T, 50<=avg<75 → revision
          R4: consensus=T, avg<50  → rejected
        """
        if not consensus:
            return "revision"                             # R1
        if average >= self.ACCEPT_THRESHOLD:
            return "accepted"                             # R2
        if average >= self.REVISE_THRESHOLD:
            return "revision"                             # R3
        return "rejected"                                 # R4


# ──────────────────────────────────────────────
# SubmissionController  – thin GRASP Controller
# Only orchestrates; does not make decisions
# ──────────────────────────────────────────────

class SubmissionController:

    def __init__(self, validator: Validator,
                 repo: SubmissionRepository,
                 reviewer_manager: ReviewerManager,
                 evaluation_manager: EvaluationManager):
        self.validator          = validator
        self.repo               = repo
        self.reviewer_manager   = reviewer_manager
        self.evaluation_manager = evaluation_manager
        self.call_count         = 0

    def submit(self, data: dict) -> dict:
        self.call_count = 0

        # 1. Validate
        self.call_count += 1
        if not self.validator.validateFormat(data):
            self.call_count += 1
            return {"outcome": "invalid", "notification": "return error",
                    "calls": self.call_count}

        # 2. Persist
        self.call_count += 1
        submission = Submission(data)
        self.repo.save(data)

        # 3. Get pre-filtered reviewers (single call – expert handles it)
        self.call_count += 1
        assigned = self.reviewer_manager.getAssignedReviewers(submission)

        # 4. Collect scores
        scores = []
        for record in assigned:
            self.call_count += 1
            score = self.reviewer_manager.collectScore(record, submission)
            scores.append(score)

        # 5. Evaluate + notify (evaluation manager handles everything)
        self.call_count += 1
        result = self.evaluation_manager.evaluate(scores, submission)
        result["calls"] = self.call_count
        return result


# ──────────────────────────────────────────────
# UI  – presentation layer only
# ──────────────────────────────────────────────

class UI:
    def __init__(self, controller: SubmissionController):
        self.controller = controller

    def submitResearchOutput(self, data: dict) -> dict:
        return self.controller.submit(data)


# ──────────────────────────────────────────────
# Factory / wiring
# ──────────────────────────────────────────────

def build_optimised_system():
    validator    = Validator()
    repo         = SubmissionRepository()
    notifier     = NotificationService()
    eval_manager = EvaluationManager(notifier)
    rev_manager  = ReviewerManager(repo)
    controller   = SubmissionController(validator, repo, rev_manager, eval_manager)
    ui           = UI(controller)
    return ui, controller


if __name__ == "__main__":
    ui, ctrl = build_optimised_system()
    sample = {
        "title":   "Deep Learning in NLP",
        "author":  "Z. Nxesi",
        "content": "This paper explores ...",
        "topic":   "NLP"
    }
    result = ui.submitResearchOutput(sample)
    print(f"Outcome      : {result['outcome']}")
    print(f"Notification : {result['notification']}")
    print(f"Method calls : {result['calls']}")
