import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from okf import load_bundle, write_concept

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "company-knowledge"


class ExampleBundleTest(unittest.TestCase):
    def setUp(self):
        self.bundle = load_bundle(EXAMPLE)

    def test_loads_concepts_and_skips_reserved_files(self):
        self.assertEqual(self.bundle.okf_version, "0.2")
        self.assertEqual(
            sorted(self.bundle.concepts),
            ["metrics/monthly-recurring-revenue", "playbooks/failed-payment", "systems/billing-api"],
        )

    def test_link_graph(self):
        mrr = self.bundle.concepts["metrics/monthly-recurring-revenue"]
        self.assertEqual(mrr.links, ["playbooks/failed-payment", "systems/billing-api"])
        self.assertEqual(
            self.bundle.backlinks("systems/billing-api"),
            ["metrics/monthly-recurring-revenue", "playbooks/failed-payment"],
        )

    def test_queries_and_trust(self):
        self.assertEqual([c.id for c in self.bundle.by_type("System")], ["systems/billing-api"])
        self.assertEqual(len(self.bundle.by_tag("billing")), 2)
        tiers = {c.id: c.verification_tier() for c in self.bundle.concepts.values()}
        self.assertEqual(tiers["metrics/monthly-recurring-revenue"], "human-reviewed")
        self.assertEqual(tiers["systems/billing-api"], "machine-confirmed")
        self.assertEqual(tiers["playbooks/failed-payment"], "unverified")

    def test_validation_reports_broken_link_but_no_errors(self):
        issues = self.bundle.validate()
        self.assertFalse([i for i in issues if i.level == "error"])
        self.assertTrue(any("playbooks/refunds" in i.message for i in issues))

    def test_staleness(self):
        mrr = self.bundle.concepts["metrics/monthly-recurring-revenue"]
        self.assertFalse(mrr.stale())
        self.assertTrue(mrr.stale(datetime(2100, 1, 1, tzinfo=timezone.utc)))


class WriteAndErrorsTest(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            write_concept(d, "glossary/arr", {"type": "Term", "title": "ARR", "tags": ["finance"]}, "12 x [MRR](../x.md)")
            c = load_bundle(d).concepts["glossary/arr"]
            self.assertEqual((c.type, c.title, c.meta["tags"]), ("Term", "ARR", ["finance"]))

    def test_type_required_on_write_and_validate(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                write_concept(d, "a", {"title": "x"}, "body")
            (Path(d) / "a.md").write_text("---\ntitle: x\n---\nbody\n")
            (Path(d) / "b.md").write_text("no frontmatter\n")
            errors = [str(i) for i in load_bundle(d).validate() if i.level == "error"]
            self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
