"""Custom pytest markers for proofagent tests."""

MARKERS = {
    "proofagent": "Mark test as a proofagent evaluation test",
    "safety": "Mark test as a safety/red-team evaluation",
    "agent": "Mark test as a multi-step agent evaluation",
    "cost": "Mark test that tracks cost assertions",
}
