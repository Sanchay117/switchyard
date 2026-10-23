"""
Meterless Engine 2: World Model (agent/engines/world_model.py)
Follows the Meterless World Model specification (meterless.ai/engines.html):
- Maintains a structured, versioned representation of entities, sourced facts,
  and cross-system conflicts shared across collaborating agents.
- Enforces optimistic concurrency control so parallel or sequential agents
  (Reconciler, Conflict Critic, Risk Escalator) never overwrite each other's updates.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Any


@dataclass
class SourcedFact:
    fact_id: str
    entity_id: str
    source_table: str
    record_key: str
    attribute: str
    value: Any
    recorded_by_agent: str
    sql_used: str
    confidence: float = 1.0
    version_added: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SourceConflict:
    conflict_id: str
    entity_id: str
    dimension: str
    source_a: str
    claim_a: str
    source_b: str
    claim_b: str
    status: str  # DETECTED | CHALLENGED_BY_CRITIC | RESOLVED | UNRESOLVED_ESCALATED
    flagged_by_agent: str
    authoritative_source: str | None = None
    resolution_explanation: str | None = None
    corroborating_sources: List[str] = field(default_factory=list)
    critic_notes: str | None = None
    version_updated: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConcurrencyConflictError(RuntimeError):
    """Raised when an agent attempts a stale state update against the World Model."""


class WorldModelEngine:
    """
    Meterless World Model Engine: single source of truth for entities, facts,
    and cross-source conflicts during a multi-agent investigation.
    """

    def __init__(self) -> None:
        self.version: int = 0
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.facts: Dict[str, SourcedFact] = {}
        self.conflicts: Dict[str, SourceConflict] = {}
        self.mutation_log: List[Dict[str, Any]] = []

    def _bump_version(self, agent_name: str, action: str, detail: str) -> int:
        self.version += 1
        self.mutation_log.append(
            {
                "version": self.version,
                "agent": agent_name,
                "action": action,
                "detail": detail,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        return self.version

    def register_entity(
        self,
        entity_id: str,
        entity_type: str,
        attributes: Dict[str, Any],
        agent_name: str,
        expected_version: int | None = None,
    ) -> int:
        if expected_version is not None and expected_version != self.version:
            raise ConcurrencyConflictError(
                f"WorldModel version mismatch: expected v{expected_version}, current is v{self.version}"
            )
        existing = self.entities.get(entity_id, {"entity_id": entity_id, "entity_type": entity_type})
        existing.update(attributes)
        self.entities[entity_id] = existing
        return self._bump_version(agent_name, "register_entity", f"Updated entity {entity_id} ({entity_type})")

    def record_fact(
        self,
        entity_id: str,
        source_table: str,
        record_key: str,
        attribute: str,
        value: Any,
        agent_name: str,
        sql_used: str,
        confidence: float = 1.0,
        expected_version: int | None = None,
    ) -> SourcedFact:
        if expected_version is not None and expected_version != self.version:
            raise ConcurrencyConflictError(
                f"WorldModel version mismatch: expected v{expected_version}, current is v{self.version}"
            )
        ver = self._bump_version(
            agent_name,
            "record_fact",
            f"[{source_table}#{record_key}] {entity_id}.{attribute} = {value}",
        )
        fact_id = f"FACT-{len(self.facts) + 1:03d}"
        fact = SourcedFact(
            fact_id=fact_id,
            entity_id=entity_id,
            source_table=source_table,
            record_key=record_key,
            attribute=attribute,
            value=value,
            recorded_by_agent=agent_name,
            sql_used=sql_used,
            confidence=confidence,
            version_added=ver,
        )
        self.facts[fact_id] = fact
        return fact

    def flag_conflict(
        self,
        entity_id: str,
        dimension: str,
        source_a: str,
        claim_a: str,
        source_b: str,
        claim_b: str,
        agent_name: str,
    ) -> SourceConflict:
        ver = self._bump_version(
            agent_name,
            "flag_conflict",
            f"Conflict on {entity_id} ({dimension}): {source_a} vs {source_b}",
        )
        conflict_id = f"CONF-{len(self.conflicts) + 1:02d}"
        conflict = SourceConflict(
            conflict_id=conflict_id,
            entity_id=entity_id,
            dimension=dimension,
            source_a=source_a,
            claim_a=claim_a,
            source_b=source_b,
            claim_b=claim_b,
            status="DETECTED",
            flagged_by_agent=agent_name,
            version_updated=ver,
        )
        self.conflicts[conflict_id] = conflict
        return conflict

    def challenge_conflict(self, conflict_id: str, critic_notes: str, agent_name: str) -> SourceConflict:
        if conflict_id not in self.conflicts:
            raise KeyError(f"Unknown conflict_id: {conflict_id}")
        ver = self._bump_version(
            agent_name,
            "challenge_conflict",
            f"Critic challenged {conflict_id}: {critic_notes[:80]}",
        )
        c = self.conflicts[conflict_id]
        c.status = "CHALLENGED_BY_CRITIC"
        c.critic_notes = critic_notes
        c.version_updated = ver
        return c

    def resolve_conflict(
        self,
        conflict_id: str,
        authoritative_source: str,
        resolution_explanation: str,
        corroborating_sources: List[str],
        agent_name: str,
    ) -> SourceConflict:
        if conflict_id not in self.conflicts:
            raise KeyError(f"Unknown conflict_id: {conflict_id}")
        ver = self._bump_version(
            agent_name,
            "resolve_conflict",
            f"Resolved {conflict_id} in favor of {authoritative_source}",
        )
        c = self.conflicts[conflict_id]
        c.status = "RESOLVED"
        c.authoritative_source = authoritative_source
        c.resolution_explanation = resolution_explanation
        c.corroborating_sources = list(corroborating_sources)
        c.version_updated = ver
        return c

    def get_unresolved_conflicts(self) -> List[SourceConflict]:
        return [c for c in self.conflicts.values() if c.status != "RESOLVED"]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "entity_count": len(self.entities),
            "fact_count": len(self.facts),
            "conflict_count": len(self.conflicts),
            "resolved_conflict_count": sum(1 for c in self.conflicts.values() if c.status == "RESOLVED"),
            "entities": self.entities,
            "facts": [f.to_dict() for f in self.facts.values()],
            "conflicts": [c.to_dict() for c in self.conflicts.values()],
            "mutation_log": self.mutation_log,
        }
