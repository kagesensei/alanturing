"""Validation for the Alan Turing evidence-based persona dataset.

This project's persona files (sources.json, chronology.json, relationships.json,
interests.json, conversational_style.json, ocean_profile.json, ipip_neo_120.json,
persona.json) are hand-authored evidence records, not generated output. This
module is the safety net that keeps that authoring honest: every claim must
carry a valid evidence_type/confidence pair, every evidence-backed claim must
cite a real source_id, every inferred claim must explain its own reasoning,
and no historical temporal persona may claim knowledge of an event past its
own knowledge_cutoff_year.

Nothing here decides *what* the persona is -- see the JSON files and their
README for that. This only decides whether the data is internally consistent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent


class EvidenceType(str, Enum):
    """Provenance of a claim -- see persona.json's evidence_type_taxonomy."""

    DIRECT = "DIRECT"
    CONTEMPORARY = "CONTEMPORARY"
    SCHOLARLY = "SCHOLARLY"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ClaimCategory(str, Enum):
    """The 5-way distinction the Turing Test Simulator must surface to a user."""

    HISTORICAL_FACT = "historical_fact"
    BIOGRAPHICAL_EVIDENCE = "biographical_evidence"
    EVIDENCE_BASED_INFERENCE = "evidence_based_inference"
    PERSONA_EXTRAPOLATION = "persona_extrapolation"
    UNKNOWN = "unknown"


def classify_claim(evidence_type: EvidenceType, confidence: Confidence) -> ClaimCategory:
    """Derive the simulator-facing claim category from (evidence_type, confidence).

    This mapping is the single source of truth for the distinction -- claim
    category is never stored as an independent field in the data files, so it
    can never drift out of sync with the evidence_type/confidence it's based on.
    """
    if evidence_type == EvidenceType.UNKNOWN:
        return ClaimCategory.UNKNOWN
    if evidence_type == EvidenceType.DIRECT:
        return ClaimCategory.HISTORICAL_FACT
    if evidence_type in (EvidenceType.CONTEMPORARY, EvidenceType.SCHOLARLY):
        return ClaimCategory.BIOGRAPHICAL_EVIDENCE
    if confidence == Confidence.LOW:
        return ClaimCategory.PERSONA_EXTRAPOLATION
    return ClaimCategory.EVIDENCE_BASED_INFERENCE


@dataclass
class ValidationIssue:
    context: str
    message: str

    def __str__(self) -> str:
        return f"{self.context}: {self.message}"


def load_json(filename: str) -> dict:
    """Read and parse one of this project's persona JSON files."""
    path = DATA_DIR / filename
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _require_fields(record: dict, fields: tuple, context: str) -> list[ValidationIssue]:
    issues = []
    for field in fields:
        if field not in record:
            issues.append(ValidationIssue(context, f"missing required field {field!r}"))
    return issues


def _validate_evidence_confidence(
    evidence_type: object, confidence: object, context: str
) -> list[ValidationIssue]:
    """Check evidence_type/confidence are valid enum values and consistent:
    UNKNOWN evidence must pair with unknown confidence, and vice versa -- an
    UNKNOWN item must never masquerade as scored evidence.
    """
    issues = []
    valid_evidence = {member.value for member in EvidenceType}
    valid_confidence = {member.value for member in Confidence}
    if evidence_type not in valid_evidence:
        issues.append(ValidationIssue(context, f"invalid evidence_type {evidence_type!r}"))
        return issues
    if confidence not in valid_confidence:
        issues.append(ValidationIssue(context, f"invalid confidence {confidence!r}"))
        return issues
    is_unknown_evidence = evidence_type == EvidenceType.UNKNOWN.value
    is_unknown_confidence = confidence == Confidence.UNKNOWN.value
    if is_unknown_evidence != is_unknown_confidence:
        issues.append(ValidationIssue(
            context,
            f"evidence_type and confidence must be UNKNOWN/unknown together "
            f"(got evidence_type={evidence_type!r}, confidence={confidence!r})",
        ))
    return issues


def _validate_sourcing(
    evidence_type: str, source_ids: list, rationale: object, context: str
) -> list[ValidationIssue]:
    """DIRECT/CONTEMPORARY/SCHOLARLY claims must cite at least one source.
    INFERRED claims must explain themselves via a non-empty rationale, so an
    inference can never silently pass as an unexplained assertion.
    """
    issues = []
    sourced_types = {
        EvidenceType.DIRECT.value, EvidenceType.CONTEMPORARY.value, EvidenceType.SCHOLARLY.value,
    }
    if evidence_type in sourced_types and not source_ids:
        issues.append(ValidationIssue(context, f"{evidence_type} claim has no source_ids"))
    if evidence_type == EvidenceType.INFERRED.value and not rationale:
        issues.append(ValidationIssue(context, "INFERRED claim has no rationale"))
    return issues


def validate_sources(sources_doc: dict) -> tuple[list[ValidationIssue], set]:
    """Validate sources.json; returns (issues, set of valid source_ids)."""
    issues: list[ValidationIssue] = []
    source_ids: set = set()
    required = ("source_id", "title", "author", "date", "source_type", "primary_or_secondary")
    for record in sources_doc.get("sources", []):
        context = f"sources.json[{record.get('source_id', '?')}]"
        issues.extend(_require_fields(record, required, context))
        source_id = record.get("source_id")
        if source_id in source_ids:
            issues.append(ValidationIssue(context, f"duplicate source_id {source_id!r}"))
        if source_id:
            source_ids.add(source_id)
        if record.get("primary_or_secondary") not in ("primary", "secondary"):
            issues.append(ValidationIssue(
                context, "primary_or_secondary must be primary/secondary",
            ))
    return issues, source_ids


def _validate_evidence_record(record: dict, required: tuple, context: str) -> list[ValidationIssue]:
    """Shared per-record validation for the claim-bearing files: required
    fields, evidence_type/confidence validity, and sourcing/rationale rules.
    """
    issues = _require_fields(record, required, context)
    if "evidence_type" in record and "confidence" in record:
        issues.extend(_validate_evidence_confidence(
            record["evidence_type"], record["confidence"], context,
        ))
        issues.extend(_validate_sourcing(
            record["evidence_type"], record.get("source_ids", []), record.get("rationale"), context,
        ))
    return issues


def validate_chronology(doc: dict) -> tuple[list[ValidationIssue], dict]:
    """Validate chronology.json; returns (issues, event_id -> year map)."""
    issues: list[ValidationIssue] = []
    events_by_id: dict = {}
    required = (
        "event_id", "year", "title", "description", "evidence_type", "confidence", "source_ids",
    )
    for record in doc.get("events", []):
        context = f"chronology.json[{record.get('event_id', '?')}]"
        issues.extend(_validate_evidence_record(record, required, context))
        event_id = record.get("event_id")
        if event_id:
            events_by_id[event_id] = record.get("year")
    return issues, events_by_id


def validate_relationships(doc: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = (
        "relationship_id", "person_name", "relationship_type", "period",
        "description", "evidence_type", "confidence", "source_ids",
    )
    for record in doc.get("relationships", []):
        context = f"relationships.json[{record.get('relationship_id', '?')}]"
        issues.extend(_validate_evidence_record(record, required, context))
    return issues


def validate_interests(doc: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = ("interest_id", "category", "evidence_type", "confidence", "source_ids")
    for record in doc.get("interests", []):
        context = f"interests.json[{record.get('interest_id', '?')}]"
        issues.extend(_validate_evidence_record(record, required, context))
        is_unknown = record.get("evidence_type") == EvidenceType.UNKNOWN.value
        if is_unknown and record.get("claim") is not None:
            issues.append(ValidationIssue(context, "UNKNOWN interest must not assert a claim"))
    return issues


def validate_conversational_style(doc: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = ("trait_id", "name", "description", "evidence_type", "confidence", "source_ids")
    for record in doc.get("traits", []):
        context = f"conversational_style.json[{record.get('trait_id', '?')}]"
        issues.extend(_validate_evidence_record(record, required, context))
    for dialogue in doc.get("sample_dialogue", []):
        context = f"conversational_style.json[{dialogue.get('dialogue_id', '?')}]"
        if dialogue.get("label") != "SIMULATED_DIALOGUE_NOT_A_HISTORICAL_QUOTE":
            issues.append(ValidationIssue(
                context, "sample dialogue must carry the simulated-dialogue label",
            ))
        if dialogue.get("is_simulated") is not True:
            issues.append(ValidationIssue(context, "sample dialogue must set is_simulated: true"))
    return issues


FACET_DOMAIN = {
    "O1": "openness", "O2": "openness", "O3": "openness",
    "O4": "openness", "O5": "openness", "O6": "openness",
    "C1": "conscientiousness", "C2": "conscientiousness", "C3": "conscientiousness",
    "C4": "conscientiousness", "C5": "conscientiousness", "C6": "conscientiousness",
    "E1": "extraversion", "E2": "extraversion", "E3": "extraversion",
    "E4": "extraversion", "E5": "extraversion", "E6": "extraversion",
    "A1": "agreeableness", "A2": "agreeableness", "A3": "agreeableness",
    "A4": "agreeableness", "A5": "agreeableness", "A6": "agreeableness",
    "N1": "neuroticism", "N2": "neuroticism", "N3": "neuroticism",
    "N4": "neuroticism", "N5": "neuroticism", "N6": "neuroticism",
}


def validate_ocean_profile(doc: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = ("domain", "facets", "evidence_type", "confidence", "source_ids")
    for record in doc.get("domains", []):
        context = f"ocean_profile.json[{record.get('domain', '?')}]"
        issues.extend(_require_fields(record, required, context))
        if "evidence_type" in record and "confidence" in record:
            issues.extend(_validate_evidence_confidence(
                record["evidence_type"], record["confidence"], context,
            ))
        for facet in record.get("facets", []):
            facet_context = f"{context}.{facet.get('facet_code', '?')}"
            expected_domain = FACET_DOMAIN.get(facet.get("facet_code"))
            if expected_domain is None:
                issues.append(ValidationIssue(facet_context, "unknown facet_code"))
            elif expected_domain != record.get("domain"):
                actual_domain = record.get("domain")
                issues.append(ValidationIssue(
                    facet_context,
                    f"facet_code belongs to domain {expected_domain!r}, not {actual_domain!r}",
                ))
    return issues


def validate_ipip_items(doc: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = ("item_id", "domain", "facet_code", "evidence_type", "confidence", "status")
    seen_ids: set = set()
    for record in doc.get("items", []):
        context = f"ipip_neo_120.json[{record.get('item_id', '?')}]"
        issues.extend(_require_fields(record, required, context))
        item_id = record.get("item_id")
        if item_id in seen_ids:
            issues.append(ValidationIssue(context, f"duplicate item_id {item_id!r}"))
        seen_ids.add(item_id)
        expected_domain = FACET_DOMAIN.get(record.get("facet_code"))
        if expected_domain is not None and expected_domain != record.get("domain"):
            issues.append(ValidationIssue(context, "domain does not match facet_code"))
        if "evidence_type" in record and "confidence" in record:
            issues.extend(_validate_evidence_confidence(
                record["evidence_type"], record["confidence"], context,
            ))
        is_unscored = record.get("status") == "unscored"
        is_unknown_evidence = record.get("evidence_type") == EvidenceType.UNKNOWN.value
        if is_unscored != is_unknown_evidence:
            issues.append(ValidationIssue(
                context, "status 'unscored' must pair with evidence_type UNKNOWN, and vice versa",
            ))
    if len(doc.get("items", [])) != 120:
        issues.append(ValidationIssue("ipip_neo_120.json", "must contain exactly 120 items"))
    return issues


def validate_personas(doc: dict, event_years: dict) -> list[ValidationIssue]:
    """Validate persona.json's temporal_personas, including the rule that a
    non-fictional historical persona may never reference a chronology event
    that postdates its own knowledge_cutoff_year.
    """
    issues: list[ValidationIssue] = []
    required = (
        "persona_id", "is_fictional", "knowledge_cutoff_year", "description", "known_events",
    )
    for record in doc.get("temporal_personas", []):
        context = f"persona.json[{record.get('persona_id', '?')}]"
        issues.extend(_require_fields(record, required, context))
        is_fictional = record.get("is_fictional")
        cutoff = record.get("knowledge_cutoff_year")
        if is_fictional and cutoff is not None:
            issues.append(ValidationIssue(
                context, "fictional persona should not set a knowledge_cutoff_year",
            ))
        if not is_fictional and cutoff is None:
            issues.append(ValidationIssue(
                context, "historical persona must set a knowledge_cutoff_year",
            ))
        if is_fictional:
            continue
        for event_id in record.get("known_events") or []:
            event_year = event_years.get(event_id)
            if event_year is None:
                issues.append(ValidationIssue(
                    context, f"known_events references unknown event {event_id!r}",
                ))
            elif cutoff is not None and event_year > cutoff:
                issues.append(ValidationIssue(
                    context,
                    f"known event {event_id!r} (year {event_year}) postdates "
                    f"knowledge_cutoff_year {cutoff}",
                ))
    return issues


def _validate_source_references(
    issues_and_docs: list[tuple[str, list[dict]]], valid_source_ids: set
) -> list[ValidationIssue]:
    """Cross-file check: every source_id referenced anywhere must exist in sources.json."""
    id_fields = (
        "source_id", "item_id", "event_id", "relationship_id",
        "interest_id", "trait_id", "domain",
    )
    issues: list[ValidationIssue] = []
    for filename, records in issues_and_docs:
        for record in records:
            record_id = next((record[f] for f in id_fields if record.get(f)), "?")
            context = f"{filename}[{record_id}]"
            for source_id in record.get("source_ids", []) or []:
                if source_id not in valid_source_ids:
                    issues.append(ValidationIssue(context, f"unknown source_id {source_id!r}"))
    return issues


def validate_all() -> list[ValidationIssue]:
    """Load and validate every persona data file, including cross-file
    source_id references and temporal-persona knowledge-cutoff checks.
    """
    issues: list[ValidationIssue] = []

    sources_doc = load_json("sources.json")
    source_issues, valid_source_ids = validate_sources(sources_doc)
    issues.extend(source_issues)

    chronology_doc = load_json("chronology.json")
    chronology_issues, event_years = validate_chronology(chronology_doc)
    issues.extend(chronology_issues)

    relationships_doc = load_json("relationships.json")
    issues.extend(validate_relationships(relationships_doc))

    interests_doc = load_json("interests.json")
    issues.extend(validate_interests(interests_doc))

    style_doc = load_json("conversational_style.json")
    issues.extend(validate_conversational_style(style_doc))

    ocean_doc = load_json("ocean_profile.json")
    issues.extend(validate_ocean_profile(ocean_doc))

    ipip_doc = load_json("ipip_neo_120.json")
    issues.extend(validate_ipip_items(ipip_doc))

    persona_doc = load_json("persona.json")
    issues.extend(validate_personas(persona_doc, event_years))

    issues.extend(_validate_source_references([
        ("chronology.json", chronology_doc.get("events", [])),
        ("relationships.json", relationships_doc.get("relationships", [])),
        ("interests.json", interests_doc.get("interests", [])),
        ("conversational_style.json", style_doc.get("traits", [])),
        ("ocean_profile.json", ocean_doc.get("domains", [])),
        ("ipip_neo_120.json", ipip_doc.get("items", [])),
    ], valid_source_ids))

    return issues


if __name__ == "__main__":
    found_issues = validate_all()
    if not found_issues:
        print("persona dataset: all validation checks passed")
    else:
        print(f"persona dataset: {len(found_issues)} validation issue(s) found")
        for issue in found_issues:
            print(f"  - {issue}")
