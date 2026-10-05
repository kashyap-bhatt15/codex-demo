from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

RESERVED = {"index.md", "log.md"}
RECOMMENDED = ("title", "description", "resource", "tags")
STATUSES = {"draft", "stable", "deprecated"}
_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)(.*)\Z", re.DOTALL)
_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")


@dataclass
class Issue:
    level: str  # "error" | "warning"
    concept: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.concept}: {self.message}"


@dataclass
class Concept:
    id: str  # path relative to the bundle root, without ".md"
    meta: dict[str, Any]
    body: str
    links: list[str] = field(default_factory=list)  # target concept IDs

    @property
    def type(self) -> str:
        return str(self.meta.get("type", ""))

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.id)

    def stale(self, now: datetime | None = None) -> bool:
        """True if ``stale_after`` (ISO 8601 instant) has passed."""
        raw = self.meta.get("stale_after")
        if not raw:
            return False
        when = raw if isinstance(raw, datetime) else datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        return (now or datetime.now(timezone.utc)) >= when

    def verification_tier(self) -> str:
        """Derived trust tier: unverified, machine-confirmed or human-reviewed."""
        verified = self.meta.get("verified")
        if not isinstance(verified, dict) or not verified.get("by"):
            return "unverified"
        return "human-reviewed" if str(verified["by"]).startswith("human:") else "machine-confirmed"


@dataclass
class Bundle:
    root: Path
    concepts: dict[str, Concept]
    unparsable: dict[str, str]  # concept ID -> reason frontmatter could not be read
    okf_version: str | None = None

    def by_type(self, type_: str) -> list[Concept]:
        return sorted((c for c in self.concepts.values() if c.type == type_), key=lambda c: c.id)

    def by_tag(self, tag: str) -> list[Concept]:
        return sorted((c for c in self.concepts.values() if tag in (c.meta.get("tags") or [])), key=lambda c: c.id)

    def backlinks(self, concept_id: str) -> list[str]:
        return sorted(c.id for c in self.concepts.values() if concept_id in c.links)

    def validate(self, now: datetime | None = None) -> list[Issue]:
        issues = [Issue("error", cid, why) for cid, why in sorted(self.unparsable.items())]
        for c in self.concepts.values():
            if not c.type.strip():
                issues.append(Issue("error", c.id, "missing required frontmatter field `type`"))
            for name in RECOMMENDED:
                if not c.meta.get(name):
                    issues.append(Issue("warning", c.id, f"missing recommended field `{name}`"))
            status = c.meta.get("status")
            if status is not None and status not in STATUSES:
                issues.append(Issue("warning", c.id, f"unknown status {status!r}"))
            for target in c.links:
                if target not in self.concepts:
                    issues.append(Issue("warning", c.id, f"broken link to {target!r}"))
            if c.stale(now):
                issues.append(Issue("warning", c.id, f"stale since {c.meta['stale_after']}"))
        return sorted(issues, key=lambda i: (i.level != "error", i.concept, i.message))


def _resolve_link(source_id: str, href: str) -> str:
    """Resolve a Markdown link to a concept ID. Leading "/" means bundle root."""
    if href.startswith("/"):
        path = posixpath.normpath(href.lstrip("/"))
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(source_id), href))
    return path[: -len(".md")]


def parse_concept(concept_id: str, text: str) -> Concept:
    m = _FRONTMATTER.match(text)
    if not m:
        raise ValueError("no YAML frontmatter block")
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a mapping")
    body = m.group(2)
    links = sorted({_resolve_link(concept_id, h) for h in _LINK.findall(body) if "://" not in h})
    return Concept(concept_id, meta, body, links)


def load_bundle(root: str | Path) -> Bundle:
    root = Path(root)
    concepts: dict[str, Concept] = {}
    unparsable: dict[str, str] = {}
    okf_version = None
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        if path.name in RESERVED:
            if rel == "index.md":  # root index may declare okf_version
                m = _FRONTMATTER.match(text)
                if m:
                    okf_version = (yaml.safe_load(m.group(1)) or {}).get("okf_version")
            continue
        cid = rel[: -len(".md")]
        try:
            concepts[cid] = parse_concept(cid, text)
        except (ValueError, yaml.YAMLError) as exc:
            unparsable[cid] = str(exc).splitlines()[0]
    return Bundle(root, concepts, unparsable, str(okf_version) if okf_version else None)


def write_concept(root: str | Path, concept_id: str, meta: dict[str, Any], body: str) -> Path:
    """Write one concept file; ``type`` is required."""
    if not str(meta.get("type", "")).strip():
        raise ValueError("`type` is required")
    path = Path(root) / f"{concept_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, default_flow_style=None).strip()
    path.write_text(f"---\n{front}\n---\n\n{body.strip()}\n", encoding="utf-8")
    return path
