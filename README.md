# Team Deep Leak — Break the Model

**Event:** Entropy Alignment Security Hackathon  
**Target:** Healthcare AI Assistant ("Riley") on **DeepSeek V4 Pro**  
**Team:** Jannis Gerardis · Hasnat Qadir · Joel Augustus · Leo Grützner · John Braun

Research, evidence, and defensive tooling from the authorized hackathon challenge against an assistant for a fictional hospital.

## Repository structure

- [`attempt_1/`](attempt_1/) — DeepSeek and Qwen attempt logs.
- [`attempt_2/`](attempt_2/) — early attack script and recorded responses.
- [`attempt_3/`](attempt_3/) — intermediate attempt notes.
- [`attempt_4/`](attempt_4/) — measured DeepSeek V4 Pro finding, evidence, and deterministic SQL guardrail.
- [`leaked_data/`](leaked_data/) — team-curated extracted records.
- [`research_archive/`](research_archive/) — complete sanitized snapshot from [entropy-results.leogruetzner.com](https://entropy-results.leogruetzner.com/), including extracted datasets, reports, raw audit results, and session evidence.
- [`presentation/`](presentation/) — presentation images.

## Published data and reports

The consolidated archive contains 622 generated artifacts and 13 sanitized session exports. See [`research_archive/README.md`](research_archive/README.md) for provenance and direct links to the extraction methodology, database dumps, and security comparison report.

> **Scope:** All hospital and patient records in this repository are fictional exercise data. The work documents authorized testing and defensive remediation.
