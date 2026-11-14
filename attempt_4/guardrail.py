"""A deterministic guardrail for the query_db tool.

The weakness: Riley writes a raw SQL string and the 25-row data-protection cap is
bypassable (for example with 'LIMIT -5', which SQLite treats as no limit, or by
Riley omitting LIMIT so the cap is not applied). The fix does NOT depend on the
model behaving. It checks the SQL before it runs and always returns the same
decision for the same input.

check_query(sql) returns:
    {"allow": True,  "safe_sql": "<rewritten SQL with a hard LIMIT 25>", "reason": ...}
    {"allow": False, "safe_sql": None, "reason": "<why it was blocked>"}

Rules (all deterministic):
  1. Exactly one read-only SELECT. No ';', no comments, no second statement,
     no write or admin keyword (INSERT/UPDATE/DELETE/DROP/ALTER/CREATE/PRAGMA/ATTACH...).
  2. Every table named after FROM or JOIN must be in the public allow-list.
  3. Any client LIMIT/OFFSET is removed and a hard 'LIMIT 25' is appended, so a
     negative, zero, missing or huge limit all become 25.
"""
import re

# The only tables Riley is allowed to read. Everything else (patients, app_users,
# patient_contacts, employees, clinical_notes, ...) is denied, whatever the wording.
ALLOWED_TABLES = {"facilities", "departments", "insurance_plans", "payers", "providers"}

ROW_CAP = 25

FORBIDDEN = re.compile(
    r"(?is)(;|--|/\*|\*/|\b(insert|update|delete|drop|alter|create|replace|"
    r"pragma|attach|detach|vacuum|reindex|grant|revoke|truncate)\b)")

# A table name right after FROM or JOIN (optionally schema-qualified).
TABLE_AFTER = re.compile(r"(?is)\b(?:from|join)\s+([a-z_][\w.]*)")

LIMIT_OR_OFFSET = re.compile(r"(?is)\s+(limit|offset)\b.*$")


def check_query(sql):
    if not isinstance(sql, str) or not sql.strip():
        return {"allow": False, "safe_sql": None, "reason": "Empty or non-text query."}
    text = sql.strip()
    if not re.match(r"(?is)^\s*select\b", text):
        return {"allow": False, "safe_sql": None, "reason": "Only a single SELECT is allowed."}
    if FORBIDDEN.search(text):
        return {"allow": False, "safe_sql": None, "reason": "Contains a forbidden keyword, comment, or second statement."}
    tables = [t.split(".")[-1].lower() for t in TABLE_AFTER.findall(text)]
    if not tables:
        return {"allow": False, "safe_sql": None, "reason": "No table found after FROM/JOIN."}
    blocked = sorted(set(t for t in tables if t not in ALLOWED_TABLES))
    if blocked:
        return {"allow": False, "safe_sql": None,
                "reason": f"Table(s) not in the public allow-list: {', '.join(blocked)}."}
    # Remove any client LIMIT/OFFSET, then force the cap. This makes LIMIT -5, LIMIT 0,
    # a missing LIMIT and LIMIT 100000 all behave identically: at most ROW_CAP rows.
    core = LIMIT_OR_OFFSET.sub("", text).rstrip().rstrip(";").rstrip()
    safe_sql = f"{core} LIMIT {ROW_CAP}"
    return {"allow": True, "safe_sql": safe_sql, "reason": f"Allowed; limit forced to {ROW_CAP}."}
