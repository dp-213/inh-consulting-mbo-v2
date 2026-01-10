# ACCEPTANCE CRITERIA (NON-NEGOTIABLE)

A solution is ONLY acceptable if **ALL** criteria below are met.
If ANY criterion is violated → NOT DONE.




## 3. Navigation & Flow

* Sidebar is the primary navigation
* Sidebar navigation:

  * Streamlit-native only
  * No new browser tabs
  * Active page clearly highlighted
* Max. **one interaction** to switch pages

Default flow for new users:
**Overview → Planning → Analysis → Valuation**

---

## 4. Financial Statement Fidelity (Critical)

P&L, Cashflow, Balance Sheet MUST:

* Visually resemble professional Excel models
* Have:

  * Clear section headers
  * Subtotals and totals emphasized
  * Logical spacing (“Häppchen fürs Auge”)
* Be fully readable **without internal scrolling**

If a statement does not look IC-ready → FAIL.

---

## 5. Tables & Formatting Rules

* Years are columns, not rows
* Year 0 (Entry) is visually distinct
* Totals clearly separated from line items
* Default units: k€ / m€
* Thousand separators required
* Percentages entered as **70**, never **0.70**

---

## 6. Speed & Simplicity

* Main outcome reachable in ≤ 3 user actions
* No “Apply”, “Run”, or “Recalculate” buttons
* Changes reflect immediately
* No jargon in labels

If explanation is required → UI failed.



---

## 9. STOP RULE

Before writing STOP you MUST:

1. Re-read this file
2. List violated criteria (if any)
3. Fix them
4. Repeat until ZERO violations remain
then commit und push to github
