"""
Hermes v1.0 — Repository Index
Ch2 Component: Repository Index (Layer 2 Knowledge)
Ch4 §4.5.2
"""

from __future__ import annotations
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ConfigEntry:
    """Index entry for a single config file."""
    filename: str
    type: str = "experiment"            # baseline | experiment | deprecated
    purpose: str = ""
    status: str = "active"              # active | stale | archived
    experiment_id: Optional[str] = None
    parent: Optional[str] = None
    diff: Optional[str] = None
    last_verified: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RepoIndex:
    """
    Repository Index. Ch4 §4.5.2.
    Tracks config files, inference scripts, and custom modules.
    Lazy refresh strategy. Stale entries marked after 7 days.
    """
    schema_version: str = "1.0"
    configs: dict[str, ConfigEntry] = field(default_factory=dict)
    inference_scripts: dict[str, ConfigEntry] = field(default_factory=dict)
    custom_modules: dict[str, dict] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def load(cls, path: Path) -> "RepoIndex":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        idx = cls(schema_version=data.get("schema_version", "1.0"))
        for k, v in data.get("configs", {}).items():
            idx.configs[k] = ConfigEntry(**v)
        for k, v in data.get("inference_scripts", {}).items():
            idx.inference_scripts[k] = ConfigEntry(**v)
        idx.custom_modules = data.get("custom_modules", {})
        idx.last_updated = data.get("last_updated", "")
        return idx

    def save(self, path: Path) -> None:
        raw = {
            "schema_version": self.schema_version,
            "configs": {k: v.__dict__ for k, v in self.configs.items()},
            "inference_scripts": {k: v.__dict__ for k, v in self.inference_scripts.items()},
            "custom_modules": self.custom_modules,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")

    def mark_stale_if_older_than(self, days: int = 7) -> list[str]:
        """Mark configs as stale if not verified within N days."""
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        stale = []
        for name, entry in self.configs.items():
            try:
                verified = datetime.fromisoformat(entry.last_verified)
                if now - verified > timedelta(days=days):
                    entry.status = "stale"
                    stale.append(name)
            except (ValueError, TypeError):
                entry.status = "stale"
                stale.append(name)
        return stale
