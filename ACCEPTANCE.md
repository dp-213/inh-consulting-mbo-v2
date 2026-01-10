# Acceptance Criteria (non-negotiable)

A solution is ONLY acceptable if ALL of the following are true:

## Core User Goal
- The main user goal can be completed end-to-end without explanation
- No configuration or setup required by the user
- The happy path is obvious within 5 seconds

## Speed & Simplicity
- Fewer than 3 user actions to reach the main outcome
- No optional fields on the main path
- No jargon or technical wording in the UI

## UX Sanity Check
- If I handed this to a non-technical friend, they would not ask "what do I do now?"
- There is a clear primary action at all times
- No secondary features distract from the core goal

## Failure Handling
- Obvious user errors are handled gracefully
- Error messages explain what to do next in plain language

## Stop Rule
- If ANY criterion above is violated, the solution is NOT done

## Modeling-Specific Criteria (Non-Negotiable)

- The user always knows:
  - Am I planning or analyzing?
  - Are my changes already reflected in results?

- Inputs and outputs are NEVER mixed on the same visual level

- The tool can replace Excel for:
  - Scenario iteration
  - IC discussion
  - Case comparison

- No page exists “because the model has it”
  Every page must answer a decision-relevant question

- The Wizard is the default and recommended entry point for new cases

# ACCEPTANCE CRITERIA (NON-NEGOTIABLE)

A solution is ONLY acceptable if **ALL** criteria below are met.
If ANY criterion is violated → STOP. Not done.

---

## 1. Core User Goal (Decision First)

- The tool’s purpose is to support **investment and financing decisions** for a consulting MBO
- The user can answer the following within **30 seconds** on any page:
  - What decision is this page supporting?
  - Is the deal getting better or worse?
  - What breaks first?

- No screen exists for “completeness” or “because the model has it”
- Every screen answers **exactly ONE decision question**
  - More than one decision → screen is invalid

---

## 2. Planning vs. Analysis Clarity

- The user must ALWAYS know:
  - Am I entering assumptions (planning)?
  - Am I interpreting results (analysis)?

Rules:
- Inputs and outputs are NEVER mixed on the same visual level
- Input areas are visually separated (sidebar / collapsible / boxed)
- Outputs are immediately updated after input changes
- No “Apply”, “Run”, or “Recalculate” buttons

---

## 3. Speed & Cognitive Simplicity

- Main outcome reachable in ≤ 3 user actions
- No optional inputs on the main decision path
- No finance or technical jargon in labels
- If an explanation is needed, the UI already failed

---

## 4. Modeling-Specific UX Rules

### Inputs
- Percentages are entered as **70**, never **0.70**
- Currency inputs:
  - Thousand separators required
  - Unit always explicit (€, k€, m€)
- Dropdowns used only when they reduce ambiguity

### Tables
- Years are columns, not rows
- Year 0 is visually distinct
- Totals and subtotals clearly separated
- No dense tables without summaries

### Summaries
- Every input page ends with a **G&V-like summary**
- Summary must:
  - Be readable without scrolling
  - Clearly reconcile with inputs above
  - Highlight deltas vs. prior year

---

## 5. Graphics & Visuals (Decision-Oriented)

- Charts are used ONLY if they improve decision clarity
- No decorative charts
- Every chart must answer one of:
  - Where is the pressure?
  - What is the trend?
  - What breaks first?

Rules:
- Prefer line charts for evolution
- Prefer bar charts for composition
- No more than 1–2 charts per page
- Charts must be interpretable without captions

---

## 6. Streamlit-Specific Non-Negotiables

- Default Streamlit navigation patterns ONLY
  - Sidebar navigation
  - No custom tab logic
  - No opening new browser tabs
- Sidebar must:
  - Persist state
  - Clearly highlight the active page
- No page reloads triggered by navigation or inputs

---

## 7. Failure Handling

- Obvious user errors are handled gracefully
- Error messages explain:
  - What went wrong
  - What to do next
- Silent failures are unacceptable

---

## 8. Replacement Test (Excel Test)

The solution is ONLY acceptable if it can fully replace Excel for:
- Scenario iteration
- Investment committee discussion
- Purchase price negotiation

If Excel would still be used → FAIL.

---

## 9. Mandatory Self-Check Before STOP

Before declaring STOP you MUST:
1. Read this file fully
2. Explicitly list which criteria were violated
3. Fix them
4. Repeat until ZERO violations remain

If unsure → assume NOT acceptable.
