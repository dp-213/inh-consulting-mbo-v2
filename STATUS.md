Re-read ACCEPTANCE.md.

Violations:
- None observed in code for Operating Model (P&L) structure, hierarchy, or navigation.

Changes:
- Standardized page titles to the top-level heading and removed the global "Financial Model" header.
- Added scenario selectors across analysis pages and applied a consistent, subtle selector container.
- Added page-specific quick-adjust drivers with a reset-to-planning button for P&L, Overview, Cashflow, Balance Sheet, and Valuation.
- Refined sidebar active state with a darker blue highlight and clearer section headers.
- Added a break-even line chart to the Overview page.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` to confirm the app starts without errors.
- Visual checks for quick-adjust placement and sidebar highlight not performed in this environment.
