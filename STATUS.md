Re-read ACCEPTANCE.md.

Violations:
- None observed in code for Operating Model (P&L) structure, hierarchy, or navigation.

Changes:
- Standardized page titles to the top-level heading and removed the global "Financial Model" header.
- Added scenario selectors across analysis pages and applied a consistent, subtle selector container.
- Added page-specific quick-adjust drivers with a reset-to-planning button for P&L, Overview, Cashflow, Balance Sheet, and Valuation.
- Refined sidebar active state with a darker blue highlight and clearer section headers.
- Added a break-even line chart to the Overview page.
- Removed opening cash quick-adjusts from Cashflow and Balance Sheet to prevent balance sheet errors.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` to confirm the app starts without errors.
- Visual checks for quick-adjust placement and sidebar highlight not performed in this environment.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Calmed the Streamlit sidebar by lightening the palette, tightening the nav section spacing, and flattening button padding while keeping every control left-aligned for a dense, Excel-like feel.
- Switched the active navigation state to a neutral fill with a dark left accent so the current page reads as a location marker rather than a CTA while avoiding bright colors.

Manual verification:
- Mental smoke test: sidebar styling tweaks do not affect logic, so the app should still start cleanly, all pages render, and inputs continue to drive outputs.
