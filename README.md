# codex-demo
Repository for Codex

## `okf` — Open Knowledge Format example

A small Python module (needs `pyyaml`) for reading, writing and validating
[Open Knowledge Format](https://www.mindstudio.ai/blog/what-is-open-knowledge-format-okf-google-ai-knowledge-bases)
(OKF v0.2) bundles: a directory of Markdown files, one concept per file, with YAML
frontmatter (`type` required) and plain Markdown links forming a knowledge graph.

```python
from okf import load_bundle, write_concept

bundle = load_bundle("examples/company-knowledge")
bundle.by_type("System")                       # query by type / tag
bundle.backlinks("systems/billing-api")        # who links here?
bundle.concepts["systems/billing-api"].verification_tier()  # human-reviewed / machine-confirmed / unverified
bundle.validate()                              # errors (no `type`) and warnings (broken links, stale, missing fields)

write_concept("my-bundle", "glossary/arr", {"type": "Term", "title": "ARR"}, "Annual recurring revenue.")
```

```
python -m okf examples/company-knowledge   # summary + validation report
python -m unittest discover -s tests       # run tests
```
