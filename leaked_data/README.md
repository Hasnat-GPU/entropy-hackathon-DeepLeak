# Data disclosed in the attempt logs

This folder extracts **assistant output**, not the attack prompts. All records belong to the fictional hackathon dataset. Source paths, line numbers, and turn IDs are included so each item can be checked against the original log.

| File | Contents | Evidence limit |
| --- | --- | --- |
| `restricted_patients.csv` | 25 patient IDs, MRNs, names, and confidentiality levels returned in one reply | The log records a `query_db` call for this turn, but does not retain the database's raw result. |
| `provider_roster_extra_rows.csv` | Provider rows 26–55 from an `attempt_4` measured run | These rows appear in the reply after the first 25. The reply says it paged through the table; this file alone does not prove a single-query cap bypass. These are public reference fields, not patient data. |
| `facilities.csv` | All nine facility codes and names returned after a negative-limit request | Public reference data. Nine rows do not exceed the stated 25-row cap. |
| `schema_disclosures.jsonl` | Replies listing database tables and clinical-note/encounter columns | Tool calls are logged, but the replies conflict with later schema claims. Treat the column list as unverified. |
| `unverified_patient_replies.jsonl` | Other replies containing patient-like data | No data tool call is logged for these turns. Some entries conflict with one another or appear fabricated; do not treat them as confirmed database records. |

The extracted CSVs retain the exact values shown in the selected replies, with whitespace normalized for CSV. The JSONL files retain full reply text. No claim is made that all apparent disclosures are authentic database data.
