from backend.services.classifier import classify_clauses, get_clause_summary

doc = """
Employment Agreement between ABC Tech Pvt Ltd and Arjun Kumar.

1. Notice Period: 90 days mandatory notice before resignation.

2. Service Bond: Employee agrees to serve for 3 years.
Penalty for early exit: Rs 2,00,000.

3. Non-Compete: Employee shall not join any competitor for 2 years.

4. Annual Leave: 12 days paid leave per year.

5. Variable Pay: 25% of CTC is performance-linked variable pay.
"""

clauses = classify_clauses(doc)

print("\nDetected Clauses:\n")

for c in clauses:

    if c["risk_level"] == "high":
        icon = "HIGH"
    elif c["risk_level"] == "medium":
        icon = "MEDIUM"
    else:
        icon = "LOW"

    print(f"{icon} | {c['clause_type']}")
    print(f"Text: {c['text']}")
    print(f"Why: {c['explanation']}")
    print()

summary = get_clause_summary(clauses)

print("Summary:")
print(summary)