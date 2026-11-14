"""Self-contained evidence helper for measure.py.

Writes a tamper-evident record of a measurement run: each line of evidence.jsonl
carries a hash of the line before it (a chain), so changing any line breaks the
chain. verify re-walks the chain and re-checks the file hashes.

This is a standalone version with no external dependencies, so the published tools
run on their own. (In the full project this bridges to a MITRE ATLAS knowledge
base for defense lookups; here defenses_for returns an empty map.)
"""
import hashlib
import json
from pathlib import Path


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode()).hexdigest()


def defenses_for(atlas_ids):
    """Placeholder in the public repo. The full project returns MITRE ATLAS mitigations."""
    return {}


class _Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.sequence = 0
        self.head = "0" * 64
        self.stream = self.path.open("x", encoding="utf-8", newline="\n")

    def append(self, kind, payload):
        item = {"sequence": self.sequence, "previous": self.head, "kind": kind, "payload": payload}
        item["hash"] = digest(item)
        self.stream.write(canonical(item) + "\n")
        self.stream.flush()
        self.head = item["hash"]
        self.sequence += 1

    def close(self):
        self.stream.close()


def seal_measurement(folder, attack, model, runs, summary):
    folder = Path(folder)
    plan = {"schema_version": 1, "attack": attack["name"], "model": model,
            "atlas": attack.get("atlas", []), "messages": attack["messages"],
            "runs_planned": len(runs), "source": "measure.py"}
    _write_json(folder / "plan.json", plan)
    _write_json(folder / "summary.json", summary)
    ledger = _Ledger(folder / "evidence.jsonl")
    try:
        ledger.append("start", {"plan_sha256": digest(plan), "attack": attack["name"], "model": model})
        for i, run in enumerate(runs):
            ledger.append("run", {"index": i, "status": run["status"],
                                  "turn_ids": [t["turn_id"] for t in run["turns"] if t["turn_id"]],
                                  "sha256": digest(run)})
        ledger.append("finish", {"summary_sha256": digest(summary), "runs": len(runs)})
    finally:
        ledger.close()
    manifest = {"schema_version": 1, "ledger_head": ledger.head, "records": ledger.sequence,
                "artifacts": {name: digest((folder / name).read_bytes())
                              for name in ("plan.json", "summary.json", "evidence.jsonl")},
                "assurance": "Local hash-chain consistency check. Keep this manifest digest separately."}
    _write_json(folder / "manifest.json", manifest)
    code = digest(manifest)
    _verify_chain(folder, manifest)
    return code


def _verify_chain(folder, manifest):
    head, count = "0" * 64, 0
    with (Path(folder) / "evidence.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            item = json.loads(line)
            claimed = item.pop("hash")
            if item["sequence"] != count or item["previous"] != head or digest(item) != claimed:
                raise ValueError(f"Evidence chain is broken at record {count}.")
            head = claimed
            count += 1
    if head != manifest["ledger_head"] or count != manifest["records"]:
        raise ValueError("Evidence chain does not match its manifest.")


def _write_json(path, value):
    # Keep evidence hashes stable across Windows, macOS, and Linux checkouts.
    with Path(path).open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(_json(value))


def _json(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"
