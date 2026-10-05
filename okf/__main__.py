"""``python -m okf <bundle-dir>`` prints a summary and validation report."""

import sys

from .bundle import load_bundle


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m okf <bundle-dir>", file=sys.stderr)
        return 2
    bundle = load_bundle(argv[0])
    print(f"Bundle {bundle.root} (okf_version={bundle.okf_version or 'unspecified'}): "
          f"{len(bundle.concepts)} concepts")
    for c in sorted(bundle.concepts.values(), key=lambda c: c.id):
        back = bundle.backlinks(c.id)
        print(f"  {c.id:34} {c.type:10} [{c.verification_tier()}] "
              f"-> {len(c.links)} links, <- {len(back)} backlinks")
    issues = bundle.validate()
    print(f"\n{len(issues)} issue(s)")
    for issue in issues:
        print(f"  {issue}")
    return 1 if any(i.level == "error" for i in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
