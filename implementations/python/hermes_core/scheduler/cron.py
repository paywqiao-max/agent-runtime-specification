"""
Hermes v1.0 — Scheduler Interface
Ch2 Component: Cron (orthogonal to component layers)
Ch3 §3.2 scheduler/jobs.json
"""

from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class CronJob:
    """Scheduled job definition."""
    job_id: str
    schedule: str           # cron expression
    workflow_id: str
    inputs: dict = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[str] = None
    last_status: Optional[str] = None


class Scheduler:
    """
    Scheduler — manages cron job definitions. Ch2 Cron component.
    """

    def __init__(self, jobs_file: Path):
        self.jobs_file = jobs_file

    def load_jobs(self) -> list[CronJob]:
        if not self.jobs_file.exists():
            return []
        data = json.loads(self.jobs_file.read_text(encoding="utf-8"))
        return [CronJob(**j) for j in data.get("jobs", [])]

    def save_jobs(self, jobs: list[CronJob]) -> None:
        self.jobs_file.parent.mkdir(parents=True, exist_ok=True)
        raw = {
            "schema_version": "1.0",
            "jobs": [j.__dict__ for j in jobs],
        }
        self.jobs_file.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
