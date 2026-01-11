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

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Rebuilt the sidebar presentation with a compact, app-like title, tighter section spacing, and dense buttons to reduce empty vertical space.
- Added per-page emoji icons in the existing sidebar items and reinforced the active state with a strong fill, left accent, and subtle inset outline.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` and stopped after startup output.
- Mental smoke test: app should still start without errors, all pages render, inputs drive outputs, and navigation remains unchanged with clearer active state.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Increased sidebar section header size and reduced nav item font size/height for a stronger hierarchy and denser list.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` and stopped after startup output.
- Mental smoke test: app should still start without errors, all pages render, inputs drive outputs, and navigation remains unchanged with clearer active state.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Forced sidebar button inner layout and text to left-align for all nav items.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` and stopped after startup output.
- Mental smoke test: app should still start without errors, all pages render, inputs drive outputs, and navigation remains unchanged with clearer active state.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Increased section header size/contrast and tightened sidebar padding/margins for a more compact, left-aligned layout.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` and stopped after startup output.
- Mental smoke test: app should still start without errors, all pages render, inputs drive outputs, and navigation remains unchanged with clearer active state.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Removed non-settings icons and tightened sidebar alignment/spacing while keeping labels unchanged.
- Added icon-only styling for Settings items via CSS pseudo-elements and strengthened the active highlight with a clear background and left accent bar.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` and stopped after startup output.
- Mental smoke test: app should still start without errors, all pages render, inputs drive outputs, and navigation remains unchanged with clearer active state.

Re-read ACCEPTANCE.md.

Violations:
- None.

Changes:
- Applied the required `.fin-table` CSS for financial statements.
- Updated financial statement rendering to use `.fin-table` with label/number alignment, negative highlighting, and Year 0 column emphasis using existing classes.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation/content regressions are introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for the Operating Model (P&L) page structure, navigation, or formatting.

Changes:
- Restructured the P&L summary into four operating sections with explicit revenue, people, scale, and resilience signals.
- Added a static interpretation box above the table for operational guidance.
- Renamed the quick-adjust panel to Operational Steering Levers and grouped inputs by capacity, pricing, people costs, and overhead.
- Highlighted personnel-driven rows and made EBITDA/Net Income more scannable in the summary table.
- Labeled Year 0 as Current Operating Reality and future years as Scaled Operations across P&L tables.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Softened People Cost Engine emphasis with a neutral gray tint and removed alert-like coloring.
- Simplified section headers to bank-style labels without A/B/C/D notation.
- Added subtle key-metric emphasis and a quiet footnote for Net Contribution.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Rendered Personnel Cost Ratio in a normal italic style to read as a KPI percentage without bold emphasis.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt Cashflow & Liquidity into four bank-style blocks focused on cash survival, with clear subtotals and a strong Closing Cash line.
- Reduced KPI summary to minimum cash balance, years with negative cash, and peak funding gap.
- Removed detailed KPI tables and explanatory blocks from the default view.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Restructured the balance sheet into asset structure, debt structure, equity evolution, and consistency check blocks.
- Reduced KPI summary to Net Debt, Equity Ratio, and Net Debt / EBITDA only.
- Simplified balance sheet assumptions label and removed explanatory text from the default view.
- Emphasized Cash as the dominant asset line and kept equity evolution as a clear bridge.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Restructured Valuation & Purchase Price into four bank-style blocks separating value, range, affordability, and negotiation levers.
- Replaced the metric grid with method-specific valuation and range tables to keep value vs price distinct.
- Simplified detailed analysis to factual net-debt and seller-view tables only.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt Valuation & Purchase Price into five structured blocks with detailed method breakdowns, summary comparison, range interpretation, affordability ceiling, and negotiation logic.
- Replaced all valuation tables with the financial statement table style for traceability and consistency.
- Kept assumptions and supporting detail in the collapsible section without dashboard-style cards.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt Financing & Debt into four bank-style blocks focused on CFADS, debt service, covenant coverage, and risk summary.
- Removed KPI clutter and explanatory text from the main view to keep the bank view mechanical and traceable.
- Added explicit DSCR headroom and a debt risk summary with required bank metrics only.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt Equity Case into five required blocks: capital at risk, ownership & control, cash flow to equity, exit bridge, and returns summary.
- Replaced KPI cards with financial-statement tables for all sections to keep the page printable and traceable.
- Removed narrative text from the page header to keep the view factual.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Removed standalone Other Assumptions from navigation and added per-page collapsed Key Assumptions blocks for Cashflow, Balance Sheet, Financing & Debt, Valuation, and Equity.
- Added explicit assumption fields (balance sheet minimum cash, valuation reference/discount/start/transaction costs, equity exit/participation) and wired them to UI and data.
- Standardized assumption tables to the same visual style as statements and ensured valuation discount rate is assumption-driven.
- Adjusted page flows to save updated assumptions from their respective pages while keeping results above assumptions.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Removed quick-adjust sections from Cashflow, Balance Sheet, Valuation, Financing & Debt, and Equity Case; each now uses only its Key Assumptions block.
- Retired the Other Assumptions page content and removed its input logic; assumptions now live only on their respective pages.
- Hardened key-assumption editing with required-field checks to avoid hidden defaults and applied statement-style table visuals.
- Updated valuation discount rate usage and assumption export wiring to use explicit model assumptions.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Removed Quick Steering from the Overview page so only the Operating Model retains it.
- Cleaned Overview to use the base scenario output without quick adjust overrides.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Retired the Financing Inputs page to remove legacy input fields and direct users to the Financing & Debt page.
- Retired the Other Assumptions page content to avoid duplicate assumption entry.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added explicit Purchase Price and Management Equity Contribution to the Equity Case assumptions and wired them into ownership logic.
- Added Opening Loan Balance to Financing & Debt assumptions to avoid hidden debt inputs.
- Hardened required-value checks to prevent blank assumptions.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Moved Key Assumptions expanders to the top of Balance Sheet, Financing & Debt, and Valuation pages (collapsed by default).
- Reframed Valuation to a Value Today / Price Today flow with summary and negotiation logic above the fold; moved method bridges into Detailed analysis and exit-only items into an optional expander.
- Fixed DSCR Headroom formatting to display in x terms and aligned coverage rows to ratio formatting.
- Added a balance sheet note clarifying negative cash as a funding gap without altering logic.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Aligned Balance Sheet Opening Equity with Opening Cash to prevent balance check crashes, with explicit on-page note.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added centralized year labeling for Transition Year and Business Plan Years across statement and KPI tables.
- Restructured Valuation overview to separate valuation methods from affordability, added intrinsic cash-based view, and expanded detailed analysis bridges.
- Added subtle CFADS/DSCR footnotes and page-level logic explanation expanders for transparency.
- Moved Key Assumptions to the top on Cashflow & Liquidity and aligned balance sheet KPIs to new year headers.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Extended Transition/Business Plan year labeling into assumption input tables and Revenue Model derived-capacity table.
- Replaced remaining “Year 0” references in explanatory copy with transition-year language.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt the Overview page as an executive decision screen with compact deal snapshot, operating reality KPIs, cash survival view, bank view, and value vs. price summary.
- Removed scenario selector and any inputs from Overview; added minimal range bar and interpretation lines without new UI components.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rebuilt Overview as a strict IC decision screen with deal mechanics, steady-state economics, liquidity risk, bank view, and value vs. price framing.
- Removed scenario selector and any inputs; added read-only Key Assumptions expander.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Expanded Financing & Debt explanation block into structured IC-grade documentation with definitions, formulas, interpretation guidance, and dependencies.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added pension obligation assumption and wired it through balance sheet display, valuation today logic, overview snapshot, and debt/ equity informational notes.
- Rebuilt valuation today sections to subtract pension obligations from equity value and added purchase price logic block with explicit pension line.
- Extended Overview deal mechanics with pension obligations and a price composition bridge.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Upgraded all “Explain business & calculation logic” blocks to IC-grade structured documentation across Cashflow, Balance Sheet, Financing & Debt, Valuation, and Equity Case.
- Added Seller Valuation Logic (Reference) block on Valuation with discounted EBIT year 0–2, pensions, and seller price expectation.
- Improved assumptions UX with m€ units and dropdowns for categorical fields in key assumption sections and relevant wizard inputs.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added alignment safeguards for Opening Loan Balance to match Debt Amount to prevent Year 0 drawdown mismatches.
- Continued m€ scaling and dropdown usage for financing assumptions to avoid free-text categorical inputs.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Removed Repayment Type controls and defaulted all financing inputs to Linear repayment to avoid crashes.
- Kept Year 0 drawdown consistency checks aligned with Debt Amount.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added an executive footnote clarifying linear repayment is fixed for comparability and should be treated as a separate financing scenario if altered.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Removed Model Settings from navigation and routing.
- Aligned Excel export year labels and added pension obligations across assumptions, balance sheet, valuation, and overview sheets.
- Added seller valuation logic block and pension-aware equity value formulas in Excel valuation export.
- Expanded JSON export to include a full model_result snapshot for reloadability.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Aligned `balance_sheet.opening_equity_eur` with `cashflow.opening_cash_balance_eur` in `data/base_case.json` to prevent balance sheet imbalance.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added load-time balance alignment so opening equity drives opening cash to prevent balance sheet errors.
- Updated revenue pricing inputs to k€ with correct scaling and added a Revenue Bridge statement on the Revenue Model page.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added a calculated capacity share table beneath Capacity Allocation and clarified Revenue Growth usage in the Revenue Model inputs.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Revenue Model now shows Consultant Capacity in the standard statement table style.
- Capacity Allocation enforces external share as input and computes group share as 1 minus external, with a calculated display.
- Revenue Drivers now include an explicit planning mode toggle with revenue growth locked at 0% for capacity-driven planning.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.
