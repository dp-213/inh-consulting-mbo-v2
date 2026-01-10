Re-read ACCEPTANCE.md.

Violations:
- None observed in code for Operating Model (P&L) structure, hierarchy, or navigation.

Changes:
- Standardized page titles to the top-level heading and removed the global "Financial Model" header.
- Added scenario selectors across analysis pages and applied a consistent, subtle selector container.
- Added quick-adjust drivers to Overview, Cashflow, Balance Sheet, and Valuation with temporary scope.
- Refined sidebar active state and section headers for clearer selection visibility.
- Added a break-even line chart to the Overview page.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` to confirm the app starts without errors.
- Visual checks for scenario selector placement, quick-adjust expanders, and sidebar highlight not performed in this environment.
