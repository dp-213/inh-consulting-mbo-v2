Re-read ACCEPTANCE.md.

Violations:
- None observed in code for Operating Model (P&L) structure, hierarchy, or navigation.

Changes:
- Added scenario selectors to relevant analysis pages with a consistent, subtle container.
- Removed all read-only labels/badges while keeping base-case persistence behavior.
- Polished sidebar active state and section headers for clearer, quieter emphasis.
- Added a break-even line chart to the Overview page.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` to confirm the app starts without errors.
- Visual checks for scenario selector placement and sidebar highlight not performed in this environment.
