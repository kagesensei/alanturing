import unittest

from persona_validation import (
    ClaimCategory,
    Confidence,
    EvidenceType,
    classify_claim,
    load_json,
    validate_all,
    validate_chronology,
    validate_conversational_style,
    validate_interests,
    validate_ipip_items,
    validate_ocean_profile,
    validate_personas,
    validate_relationships,
    validate_sources,
)

DATA_FILES = (
    "sources.json",
    "chronology.json",
    "relationships.json",
    "interests.json",
    "conversational_style.json",
    "ocean_profile.json",
    "ipip_neo_120.json",
    "persona.json",
)


class TestJsonParsesAndFullDatasetIsValid(unittest.TestCase):
    def test_every_data_file_parses(self):
        for filename in DATA_FILES:
            with self.subTest(filename=filename):
                doc = load_json(filename)
                self.assertIsInstance(doc, dict)

    def test_full_bundled_dataset_has_no_validation_issues(self):
        issues = validate_all()
        self.assertEqual(issues, [], msg="\n".join(str(issue) for issue in issues))


class TestClassifyClaim(unittest.TestCase):
    def test_direct_is_historical_fact(self):
        self.assertEqual(
            classify_claim(EvidenceType.DIRECT, Confidence.HIGH), ClaimCategory.HISTORICAL_FACT,
        )

    def test_contemporary_and_scholarly_are_biographical_evidence(self):
        self.assertEqual(
            classify_claim(EvidenceType.CONTEMPORARY, Confidence.MEDIUM),
            ClaimCategory.BIOGRAPHICAL_EVIDENCE,
        )
        self.assertEqual(
            classify_claim(EvidenceType.SCHOLARLY, Confidence.HIGH),
            ClaimCategory.BIOGRAPHICAL_EVIDENCE,
        )

    def test_inferred_with_low_confidence_is_persona_extrapolation(self):
        self.assertEqual(
            classify_claim(EvidenceType.INFERRED, Confidence.LOW),
            ClaimCategory.PERSONA_EXTRAPOLATION,
        )

    def test_inferred_with_higher_confidence_is_evidence_based_inference(self):
        self.assertEqual(
            classify_claim(EvidenceType.INFERRED, Confidence.MEDIUM),
            ClaimCategory.EVIDENCE_BASED_INFERENCE,
        )
        self.assertEqual(
            classify_claim(EvidenceType.INFERRED, Confidence.HIGH),
            ClaimCategory.EVIDENCE_BASED_INFERENCE,
        )

    def test_unknown_is_never_silently_a_stronger_category(self):
        self.assertEqual(
            classify_claim(EvidenceType.UNKNOWN, Confidence.UNKNOWN), ClaimCategory.UNKNOWN,
        )


class TestSourcesValidation(unittest.TestCase):
    def test_bundled_sources_have_no_issues_and_are_unique(self):
        issues, source_ids = validate_sources(load_json("sources.json"))
        self.assertEqual(issues, [])
        self.assertEqual(len(source_ids), len(set(source_ids)))

    def test_rejects_missing_required_field(self):
        broken = {"sources": [{"source_id": "SX", "title": "t"}]}
        issues, _ = validate_sources(broken)
        self.assertTrue(any("author" in str(issue) for issue in issues))

    def test_rejects_duplicate_source_id(self):
        one = {
            "source_id": "SX", "title": "t", "author": "a", "date": "2000",
            "source_type": "book", "primary_or_secondary": "primary",
        }
        broken = {"sources": [one, dict(one)]}
        issues, _ = validate_sources(broken)
        self.assertTrue(any("duplicate" in str(issue) for issue in issues))


class TestEvidenceConfidenceConsistency(unittest.TestCase):
    def test_unknown_evidence_type_cannot_pair_with_scored_confidence(self):
        broken = {"events": [{
            "event_id": "EX", "year": 1940, "title": "t", "description": "d",
            "evidence_type": "UNKNOWN", "confidence": "high", "source_ids": [],
        }]}
        issues, _ = validate_chronology(broken)
        self.assertTrue(any("UNKNOWN/unknown together" in str(issue) for issue in issues))

    def test_scored_evidence_type_cannot_pair_with_unknown_confidence(self):
        broken = {"events": [{
            "event_id": "EX", "year": 1940, "title": "t", "description": "d",
            "evidence_type": "DIRECT", "confidence": "unknown", "source_ids": ["S001"],
        }]}
        issues, _ = validate_chronology(broken)
        self.assertTrue(any("UNKNOWN/unknown together" in str(issue) for issue in issues))

    def test_rejects_invalid_evidence_type_value(self):
        broken = {"relationships": [{
            "relationship_id": "RX", "person_name": "x", "relationship_type": "x",
            "period": "x", "description": "x", "evidence_type": "VIBES",
            "confidence": "high", "source_ids": ["S001"],
        }]}
        issues = validate_relationships(broken)
        self.assertTrue(any("invalid evidence_type" in str(issue) for issue in issues))


class TestSourcingAndInferenceRules(unittest.TestCase):
    def test_direct_claim_without_source_is_rejected(self):
        broken = {"interests": [{
            "interest_id": "IX", "category": "x", "evidence_type": "DIRECT",
            "confidence": "high", "source_ids": [],
        }]}
        issues = validate_interests(broken)
        self.assertTrue(any("no source_ids" in str(issue) for issue in issues))

    def test_inferred_claim_without_rationale_is_rejected(self):
        broken = {"traits": [{
            "trait_id": "TX", "name": "x", "description": "x", "evidence_type": "INFERRED",
            "confidence": "medium", "source_ids": [], "rationale": None,
        }]}
        issues = validate_conversational_style(broken)
        self.assertTrue(any("no rationale" in str(issue) for issue in issues))

    def test_unknown_interest_cannot_also_assert_a_claim(self):
        broken = {"interests": [{
            "interest_id": "IX", "category": "x", "claim": "a definite claim",
            "evidence_type": "UNKNOWN", "confidence": "unknown", "source_ids": [],
        }]}
        issues = validate_interests(broken)
        self.assertTrue(any("must not assert a claim" in str(issue) for issue in issues))


class TestOceanFacetDomainRelationships(unittest.TestCase):
    def test_bundled_ocean_profile_has_no_issues(self):
        issues = validate_ocean_profile(load_json("ocean_profile.json"))
        self.assertEqual(issues, [])

    def test_rejects_facet_assigned_to_wrong_domain(self):
        broken = {"domains": [{
            "domain": "openness", "evidence_type": "UNKNOWN", "confidence": "unknown",
            "source_ids": [], "facets": [{"facet_code": "C1", "facet_name": "Self-Efficacy"}],
        }]}
        issues = validate_ocean_profile(broken)
        self.assertTrue(any("belongs to domain" in str(issue) for issue in issues))

    def test_rejects_unknown_facet_code(self):
        broken = {"domains": [{
            "domain": "openness", "evidence_type": "UNKNOWN", "confidence": "unknown",
            "source_ids": [], "facets": [{"facet_code": "Z9", "facet_name": "Nonsense"}],
        }]}
        issues = validate_ocean_profile(broken)
        self.assertTrue(any("unknown facet_code" in str(issue) for issue in issues))


class TestIpipItems(unittest.TestCase):
    def test_bundled_ipip_items_have_no_issues(self):
        issues = validate_ipip_items(load_json("ipip_neo_120.json"))
        self.assertEqual(issues, [])

    def test_all_120_items_are_present_and_unscored_by_default(self):
        doc = load_json("ipip_neo_120.json")
        self.assertEqual(len(doc["items"]), 120)
        self.assertTrue(all(item["status"] == "unscored" for item in doc["items"]))
        self.assertTrue(all(item["evidence_type"] == "UNKNOWN" for item in doc["items"]))

    def test_unscored_status_must_match_unknown_evidence_type(self):
        broken = {"items": [{
            "item_id": "O1_1", "domain": "openness", "facet_code": "O1",
            "evidence_type": "UNKNOWN", "confidence": "unknown", "status": "scored",
        }]}
        issues = validate_ipip_items(broken)
        self.assertTrue(any("unscored" in str(issue) for issue in issues))

    def test_rejects_wrong_item_count(self):
        issues = validate_ipip_items({"items": []})
        self.assertTrue(any("exactly 120 items" in str(issue) for issue in issues))


class TestTemporalPersonaKnowledgeCutoff(unittest.TestCase):
    def test_bundled_personas_have_no_issues(self):
        persona_doc = load_json("persona.json")
        _, event_years = validate_chronology(load_json("chronology.json"))
        issues = validate_personas(persona_doc, event_years)
        self.assertEqual(issues, [])

    def test_historical_persona_cannot_know_a_future_event(self):
        event_years = {"E999": 1954}
        broken = {"temporal_personas": [{
            "persona_id": "turing_1936", "is_fictional": False, "knowledge_cutoff_year": 1936,
            "description": "d", "known_events": ["E999"],
        }]}
        issues = validate_personas(broken, event_years)
        self.assertTrue(any("postdates" in str(issue) for issue in issues))

    def test_fictional_persona_must_not_set_a_cutoff(self):
        broken = {"temporal_personas": [{
            "persona_id": "turing_a1", "is_fictional": True, "knowledge_cutoff_year": 2024,
            "description": "d", "known_events": [],
        }]}
        issues = validate_personas(broken, {})
        self.assertTrue(
            any("should not set a knowledge_cutoff_year" in str(issue) for issue in issues)
        )

    def test_historical_persona_must_set_a_cutoff(self):
        broken = {"temporal_personas": [{
            "persona_id": "turing_1936", "is_fictional": False, "knowledge_cutoff_year": None,
            "description": "d", "known_events": [],
        }]}
        issues = validate_personas(broken, {})
        self.assertTrue(any("must set a knowledge_cutoff_year" in str(issue) for issue in issues))


class TestCrossFileSourceReferences(unittest.TestCase):
    def test_full_dataset_has_no_dangling_source_ids(self):
        # validate_all() already checks this across every file; a targeted
        # regression check that a bad reference is actually caught:
        issues = validate_all()
        dangling = [issue for issue in issues if "unknown source_id" in str(issue)]
        self.assertEqual(dangling, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
