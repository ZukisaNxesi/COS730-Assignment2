"""
COS 730 – Assignment 2
Task 1: Baseline Implementation (Correctness Phase)
Faithful translation of the provided sequence diagram.
Each class and method maps 1-to-1 to a lifeline/message in the diagram.
"""

import time
import random


# ──────────────────────────────────────────────
# Domain / Data objects
# ──────────────────────────────────────────────

class Submission:
    def __init__(self, data: dict):
        self.data = data
        self.submission_id = random.randint(1000, 9999)
        self.scores: list[float] = []
        self.outcome: str = ""


class ReviewerRecord:
    def __init__(self, reviewer_id: int, conflicts: list[str], workload: int):
        self.reviewer_id = reviewer_id
        self.conflicts = conflicts      # list of author names / topics
        self.workload = workload        # number of current assignments


# ──────────────────────────────────────────────
# Validator  (diagram lifeline: Validator)
# ──────────────────────────────────────────────

class Validator:
    """Diagram message: validateFormat(data)"""

    def validateFormat(self, data: dict) -> str:          # → valid / invalid
        required_fields = ["title", "author", "content"]
        for field in required_fields:
            if field not in data or not data[field]:
                return "invalid"
        return "valid"


# ──────────────────────────────────────────────
# Database  (diagram lifeline: Database)
# ──────────────────────────────────────────────

class Database:
    """Diagram messages: saveSubmission(data), fetchReviewers()"""

    def __init__(self):
        self._submissions: dict = {}
        self._reviewers: list[ReviewerRecord] = [
            ReviewerRecord(1, ["Topic A"],   2),
            ReviewerRecord(2, [],            1),
            ReviewerRecord(3, ["author_x"],  3),
            ReviewerRecord(4, [],            0),
            ReviewerRecord(5, ["Topic C"],   2),
        ]

    def saveSubmission(self, data: dict) -> str:          # → confirmation
        sid = random.randint(1000, 9999)
        self._submissions[sid] = data
        time.sleep(0.002)                                  # simulate I/O
        return f"SAVED:{sid}"

    def fetchReviewers(self) -> list[ReviewerRecord]:     # → reviewerList
        time.sleep(0.002)                                  # simulate I/O
        return list(self._reviewers)


# ──────────────────────────────────────────────
# Reviewer  (diagram lifeline: Reviewer)
# ──────────────────────────────────────────────

class Reviewer:
    """Diagram message: submitScore(score)"""

    def __init__(self, record: ReviewerRecord):
        self.record = record

    def submitScore(self, submission: Submission) -> float:
        # Simulated scoring
        score = round(random.uniform(50, 100), 2)
        time.sleep(0.001)
        return score


# ──────────────────────────────────────────────
# ReviewerManager  (diagram lifeline: ReviewerManager)
# ──────────────────────────────────────────────

class ReviewerManager:
    """
    Diagram messages:
      getAvailableReviewers() → calls Database.fetchReviewers()
      filterConflicts(reviewerList)
      checkWorkload(reviewerList)
      assignReview()
    """

    def __init__(self, database: Database):
        self.database = database
        self.assigned_reviewers: list[Reviewer] = []

    def getAvailableReviewers(self) -> list[ReviewerRecord]:
        # Diagram: SubmissionController → ReviewerManager → Database
        return self.database.fetchReviewers()              # fetchReviewers()

    def filterConflicts(self, reviewer_list: list[ReviewerRecord],
                        submission: Submission) -> list[ReviewerRecord]:
        author = submission.data.get("author", "")
        topic  = submission.data.get("topic",  "")
        filtered = []
        for r in reviewer_list:
            if author not in r.conflicts and topic not in r.conflicts:
                filtered.append(r)
        time.sleep(0.001)
        return filtered

    def checkWorkload(self, reviewer_list: list[ReviewerRecord]) -> list[ReviewerRecord]:
        MAX_WORKLOAD = 3
        return [r for r in reviewer_list if r.workload < MAX_WORKLOAD]

    def assignReview(self, reviewer_record: ReviewerRecord) -> Reviewer:
        reviewer = Reviewer(reviewer_record)
        self.assigned_reviewers.append(reviewer)
        time.sleep(0.001)
        return reviewer


# ──────────────────────────────────────────────
# EvaluationManager  (diagram lifeline: EvaluationManager)
# ──────────────────────────────────────────────

class EvaluationManager:
    """
    Diagram messages:
      startEvaluation()
      saveScore(score)
      calculateAverage()
      checkConsensus()
      applyRules()
    """

    def __init__(self):
        self.scores: list[float] = []

    def startEvaluation(self):
        self.scores = []
        time.sleep(0.001)

    def saveScore(self, score: float):
        self.scores.append(score)
        time.sleep(0.001)

    def calculateAverage(self) -> float:
        if not self.scores:
            return 0.0
        avg = sum(self.scores) / len(self.scores)
        time.sleep(0.001)
        return avg

    def checkConsensus(self) -> bool:
        if len(self.scores) < 2:
            return True
        variance = max(self.scores) - min(self.scores)
        time.sleep(0.001)
        return variance <= 20.0                            # consensus threshold

    def applyRules(self, average: float, consensus: bool) -> str:
        time.sleep(0.001)
        if not consensus:
            return "revision"
        if average >= 75:
            return "accepted"
        elif average >= 50:
            return "revision"
        else:
            return "rejected"


# ──────────────────────────────────────────────
# NotificationService  (diagram lifeline: NotificationService)
# ──────────────────────────────────────────────

class NotificationService:
    """
    Diagram messages:
      notifyAcceptance()  [alt: accepted]
      notifyRejection()   [alt: rejected]
      notifyRevision()    [alt: revision]
    """

    def notifyAcceptance(self, submission: Submission):
        time.sleep(0.001)
        return f"[NOTIFY] Submission accepted. ID={submission.submission_id}"

    def notifyRejection(self, submission: Submission):
        time.sleep(0.001)
        return f"[NOTIFY] Submission rejected. ID={submission.submission_id}"

    def notifyRevision(self, submission: Submission):
        time.sleep(0.001)
        return f"[NOTIFY] Revision required. ID={submission.submission_id}"

    def sendNotification(self, outcome: str, submission: Submission) -> str:
        # Diagram: alt [accepted] / [rejected] / [revision]
        if outcome == "accepted":
            return self.notifyAcceptance(submission)
        elif outcome == "rejected":
            return self.notifyRejection(submission)
        else:
            return self.notifyRevision(submission)


# ──────────────────────────────────────────────
# UI  (diagram lifeline: UI)
# ──────────────────────────────────────────────

class UI:
    """
    Diagram messages:
      submitResearchOutput(data) [Researcher → UI]
      submit(data)               [UI → SubmissionController]
    """

    def __init__(self, controller):
        self.controller = controller

    def submitResearchOutput(self, data: dict):
        # Researcher → UI: submitResearchOutput(data)
        return self.controller.submit(data)               # UI → SubmissionController


# ──────────────────────────────────────────────
# SubmissionController  (diagram lifeline: SubmissionController)
# ──────────────────────────────────────────────

class SubmissionController:
    """
    Central orchestrator. Diagram shows SubmissionController touching
    every other lifeline (high coupling by design — baseline).
    """

    def __init__(self, validator: Validator, database: Database,
                 reviewer_manager: ReviewerManager,
                 evaluation_manager: EvaluationManager,
                 notification_service: NotificationService):
        self.validator            = validator
        self.database             = database
        self.reviewer_manager     = reviewer_manager
        self.evaluation_manager   = evaluation_manager
        self.notification_service = notification_service
        self.call_count           = 0                     # metric counter

    def submit(self, data: dict) -> dict:
        result = {"calls": 0, "outcome": "", "notification": ""}
        self.call_count = 0

        # ── validateFormat(data) ──────────────────────────────
        self.call_count += 1
        validity = self.validator.validateFormat(data)     # Diagram: → Validator

        # ── alt [invalid] ────────────────────────────────────
        if validity == "invalid":
            self.call_count += 1
            result["outcome"] = "invalid"
            result["notification"] = "return error"
            result["calls"] = self.call_count
            return result

        # ── [valid] branch ───────────────────────────────────
        # saveSubmission(data)
        self.call_count += 1
        submission = Submission(data)
        confirmation = self.database.saveSubmission(data)  # Diagram: → Database

        # getAvailableReviewers()
        self.call_count += 1
        reviewer_list = self.reviewer_manager.getAvailableReviewers()

        # fetchReviewers() is called inside ReviewerManager
        self.call_count += 1

        # filterConflicts(reviewerList)
        self.call_count += 1
        filtered = self.reviewer_manager.filterConflicts(reviewer_list, submission)

        # checkWorkload(reviewerList)
        self.call_count += 1
        filtered = self.reviewer_manager.checkWorkload(filtered)

        # filteredReviewers returned to SubmissionController
        self.call_count += 1

        # ── loop [assign reviewers] ───────────────────────────
        assigned: list[Reviewer] = []
        NUM_REVIEWERS = min(3, len(filtered))
        selected = filtered[:NUM_REVIEWERS]

        for record in selected:
            self.call_count += 1                           # assignReview()
            reviewer = self.reviewer_manager.assignReview(record)
            assigned.append(reviewer)

        # startEvaluation()
        self.call_count += 1
        self.evaluation_manager.startEvaluation()

        # ── loop [each reviewer] ─────────────────────────────
        for reviewer in assigned:
            self.call_count += 1                           # submitScore(score)
            score = reviewer.submitScore(submission)

            self.call_count += 1                           # saveScore(score)
            self.evaluation_manager.saveScore(score)

        # calculateAverage()
        self.call_count += 1
        average = self.evaluation_manager.calculateAverage()

        # checkConsensus()
        self.call_count += 1
        consensus = self.evaluation_manager.checkConsensus()

        # applyRules()
        self.call_count += 1
        outcome = self.evaluation_manager.applyRules(average, consensus)

        # alt [accepted / rejected / revision] → NotificationService
        self.call_count += 1
        notification = self.notification_service.sendNotification(outcome, submission)

        # sendNotification() → Researcher
        self.call_count += 1

        result["outcome"]       = outcome
        result["notification"]  = notification
        result["calls"]         = self.call_count
        result["average"]       = average
        result["consensus"]     = consensus
        return result


# ──────────────────────────────────────────────
# Factory / wiring
# ──────────────────────────────────────────────

def build_baseline_system():
    validator          = Validator()
    database           = Database()
    evaluation_manager = EvaluationManager()
    notification       = NotificationService()
    reviewer_manager   = ReviewerManager(database)
    controller         = SubmissionController(
        validator, database, reviewer_manager, evaluation_manager, notification
    )
    ui = UI(controller)
    return ui, controller


if __name__ == "__main__":
    ui, ctrl = build_baseline_system()
    sample_data = {
        "title":   "Deep Learning in NLP",
        "author":  "Z. Nxesi",
        "content": "This paper explores ...",
        "topic":   "NLP"
    }
    result = ui.submitResearchOutput(sample_data)
    print(f"Outcome      : {result['outcome']}")
    print(f"Notification : {result['notification']}")
    print(f"Method calls : {result['calls']}")
