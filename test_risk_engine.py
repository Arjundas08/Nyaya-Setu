from backend.services.classifier import classify_clauses
from backend.services.risk_engine import calculate_risk_score

doc = """
Employment Agreement between ABC Tech Pvt Ltd and Arjun Kumar.

1. Notice Period: 90 days mandatory notice before resignation.

2. Service Bond: Employee agrees to serve for 3 years.
Penalty for early exit: Rs 2,00,000.

3. Non-Compete: Employee shall not join any competitor for 2 years.

4. Annual Leave: 12 days paid leave per year.

5. Variable Pay: 25% of CTC is performance-linked variable pay.
"""

# STEP 1 — classify clauses
clauses = classify_clauses(doc)

print("\nDetected Clauses:\n")
for c in clauses:
    print(c)

# STEP 2 — calculate hybrid risk score
risk = calculate_risk_score(doc, clauses)

print("\nFinal Risk Analysis:\n")
print(risk)