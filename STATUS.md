Re-read ACCEPTANCE.md.

Violations:
- None observed in code for Operating Model (P&L) structure, hierarchy, or navigation.

Changes:
- Adjusted sidebar styling for a lighter, persistent active-state highlight and tighter typography.
- Main P&L reduced to an executive view; KPIs appended in-table as secondary rows.
- Consolidated detail analysis into a single expander with full P&L and logic/bridges.
- Added a collapsed “Key P&L Drivers (Quick Adjust)” input block above the P&L and clarified its temporary scope.
- Applied the executive layout pattern to Cashflow, Balance Sheet, and Valuation pages with a single Detailed analysis expander.

Manual verification:
- Ran `streamlit run app.py` (headless) to confirm the app starts without errors.
- Visual checks for sidebar highlight and scroll-free tables not performed in this environment.
