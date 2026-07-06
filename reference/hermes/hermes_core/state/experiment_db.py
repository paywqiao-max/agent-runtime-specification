"""
Hermes v1.0 — Experiment Database
Ch2 Component: Experiment Database (Layer 2 Knowledge)
Ch4 §4.5.2 Knowledge State
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Any
from dataclasses import dataclass, field, asdict

from ..core.exceptions import SpecificationError, InvariantViolation


@dataclass
class ExperimentRecord:
    """A single experiment record. Ch4 §4.5.2."""
    schema_version: str = "1.0"
    exp_id: str = ""
    status: str = "planned"         # planned | training | inference_done | submitted | analyzed
    parent: Optional[str] = None
    variable_changed: Optional[str] = None
    config_path: Optional[str] = None
    start_time: Optional[str] = None
    gpu: list[int] = field(default_factory=list)
    training_log: Optional[str] = None
    total_epochs: Optional[int] = None
    best_val_mAP: Optional[float] = None
    best_epoch: Optional[int] = None
    checkpoint_path: Optional[str] = None
    inference_script: Optional[str] = None
    inference_output_size: Optional[int] = None
    inference_non_empty: Optional[int] = None
    leaderboard_score: Optional[float] = None
    submission_zip: Optional[str] = None
    notes: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ExperimentDatabase:
    """
    Experiment Database — Single Source of Truth for experiments.
    Ch4 §4.5.2, Ch2 Experiment DB component.
    
    Schema versioning: §4.9
    State integrity: §4.10
    Invariant I1 (unique IDs): §4.13
    """
    schema_version: str = "1.0"
    experiments: dict[str, ExperimentRecord] = field(default_factory=dict)
    baselines: dict = field(default_factory=lambda: {"current": None, "history": []})
    roi_pipeline: list = field(default_factory=list)
    last_modified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: Optional[str] = None

    @classmethod
    def load(cls, path: Path) -> "ExperimentDatabase":
        """Load from JSON file. Returns empty DB if file doesn't exist."""
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        db = cls(
            schema_version=data.get("schema_version", "1.0"),
            baselines=data.get("baselines", {"current": None, "history": []}),
            roi_pipeline=data.get("roi_pipeline", []),
            last_modified=data.get("last_modified", ""),
            checksum=data.get("checksum"),
        )
        for eid, rec in data.get("experiments", {}).items():
            db.experiments[eid] = ExperimentRecord(**rec)
        return db

    def save(self, path: Path) -> None:
        """Save to JSON file with integrity metadata. Ch4 §4.10."""
        raw = {
            "schema_version": self.schema_version,
            "experiments": {k: asdict(v) for k, v in self.experiments.items()},
            "baselines": self.baselines,
            "roi_pipeline": self.roi_pipeline,
            "last_modified": datetime.now(timezone.utc).isoformat(),
        }
        text = json.dumps(raw, indent=2, ensure_ascii=False)
        raw["checksum"] = hashlib.sha256(text.encode()).hexdigest()[:16]
        text_with_checksum = json.dumps(raw, indent=2, ensure_ascii=False)
        path.write_text(text_with_checksum, encoding="utf-8")
        self.checksum = raw["checksum"]

    def verify_integrity(self, path: Path) -> bool:
        """Verify state file integrity. Ch4 §4.10."""
        if not path.exists():
            return True
        stored = json.loads(path.read_text(encoding="utf-8"))
        stored_checksum = stored.pop("checksum", None)
        if stored_checksum is None:
            return True
        text = json.dumps(stored, indent=2, ensure_ascii=False)
        actual = hashlib.sha256(text.encode()).hexdigest()[:16]
        return actual == stored_checksum

    def create_experiment(self, record: ExperimentRecord) -> str:
        """
        Create a new experiment. Ch4 API: create_experiment().
        Invariant I1 — uniqueness enforced. §4.13.
        """
        if record.exp_id in self.experiments:
            raise InvariantViolation(f"Experiment ID {record.exp_id} already exists")
        self.experiments[record.exp_id] = record
        return record.exp_id

    def update_experiment(self, exp_id: str, patch: dict) -> None:
        """Partial update of an experiment record."""
        if exp_id not in self.experiments:
            from ..core.exceptions import LogicError
            raise LogicError(f"Experiment {exp_id} not found")
        rec = self.experiments[exp_id]
        for k, v in patch.items():
            if hasattr(rec, k):
                setattr(rec, k, v)
        self.experiments[exp_id] = rec

    def get_next_id(self) -> str:
        """Generate next experiment ID. Ch4 API: get_next_id()."""
        existing = [int(k.replace("exp_", "")) for k in self.experiments if k.startswith("exp_")]
        next_num = max(existing) + 1 if existing else 1
        return f"exp_{next_num}"

    def get_baseline(self) -> Optional[ExperimentRecord]:
        """Get current golden baseline. Ch4 API."""
        current_id = self.baselines.get("current")
        if current_id and current_id in self.experiments:
            return self.experiments[current_id]
        return None
