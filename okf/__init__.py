"""Minimal reader/writer/validator for the Open Knowledge Format (OKF) v0.2.

An OKF bundle is a directory of UTF-8 Markdown files. Each file is one concept:
YAML frontmatter (only ``type`` is required) followed by a Markdown body.
The file path (minus ``.md``) is the concept's ID, and ordinary Markdown links
between files form a graph.
"""

from .bundle import Bundle, Concept, Issue, load_bundle, write_concept

__all__ = ["Bundle", "Concept", "Issue", "load_bundle", "write_concept"]
