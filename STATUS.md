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
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added explicit Transaction Outflows (Closing) lines for purchase price and transaction costs in the Cashflow & Liquidity table, keeping sign conventions consistent.
- Reconciled net cashflow display to the full financing + transaction bridge and wired equity contribution from the case assumptions.
- Updated cashflow calculation logic copy to include equity contribution and transaction outflows.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and cashflow table reconciliation uses the new lines without breaking navigation or layout.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Restructured Valuation & Purchase Price to emphasize Seller Price Expectation and demote buyer checks to reference-only language.
- Removed intrinsic/exit narratives and equity-value wording, keeping only multiple-based and DCF mechanics under Detailed analysis.
- Updated explanatory copy to reinforce negotiation anchors and avoid precision language.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and the valuation page remains navigable with the simplified sections.

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

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Revenue Drivers now hide Revenue Growth inputs in capacity-driven mode and force revenue growth to 0% in that mode.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Cost Model units are now consistently in k€ with numeric-only values; added inflation note clarifying application to monetary inputs only.
- Pricing assumption display now supports k€ / % units with correct scaling.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Revenue Capacity Allocation now clamps external share inputs to 0–100% and always calculates group share as 100% minus external.
- Revenue Growth is fully removed from Revenue Model entry points and forced to 0% in quick inputs to keep planning strictly capacity-driven.
- Base case assumptions now set revenue growth to 0% across all scenarios to avoid hidden top-down overlays.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Revenue Model now includes the standard Worst/Base/Best scenario selector at the top, aligned with the Operating Model pattern.
- Scenario selection updates the visible and editable revenue inputs for the selected case immediately.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added a subtle note under the Revenue Model scenario selector clarifying scenario meaning vs. structural cost/financing anchors.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Updated base case revenue assumptions to a stable ~20m EUR profile with 3,750 EUR day rates, no growth overlays, and explicit group/external mix ramps per scenario.
- Aligned cost inputs to a historical GuV profile with 63 consultants and conservative, sticky costs; kept inflation at 2% with base-year values repeated across years.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- DCF and intrinsic valuation now use business free cashflow excluding acquisition outflows, keeping DCF independent of purchase price mechanics.
- Added a subtle footnote in Valuation overview and clarified the calculation logic text to reflect the operating-only cashflow basis.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Multiple-based valuation now derives enterprise value directly from Reference EBIT × seller multiple and uses it consistently in overview and detailed tables.
- Net debt labels now correctly indicate end of transition year.
- Buyer affordability display is relabeled as an illustrative exit equity value sensitivity, aligning labels with the underlying calculation.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Overview decision block now separates value perspectives (DCF intrinsic, market reference, affordability ceiling) from purchase price positioning.
- Negotiation gap is explicitly defined vs. market reference, with purchase price positioned against affordability and market reference.
- Added helper text clarifying these are perspectives, not a valuation range, and that affordability is a financing/liquidity ceiling.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Rewrote all explanation expanders to a decision-grade IC structure covering business question, scope, calculation logic, interpretation, red flags, and dependencies.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Explanation boxes now use compact bullet lists with formula-style calculation logic for transparency and reduced length.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Added spacing between sections in all explanation expanders for readability while keeping compact bullets and formulas.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- JSON export now outputs only the assumptions schema (no metadata or derived results) and respects the active scenario selection from session state.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Excel export now respects active session scenario selection and recalculates export results accordingly.
- Valuation sheet aligns with app logic (reference EBIT multiple, DCF excluding acquisition outflow, net debt at transition year, pension adjustments, illustrative exit only).
- Debt sheet now uses working capital change in CFADS and includes DSCR headroom (x).
- Assumptions sheet includes valuation reference year and valuation start year for traceable Excel formulas.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Programmatically generated Excel export via `export_ic_excel` for base case (bytes generated successfully).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Revenue Bridge now matches required structure and guarantee logic visibility (modeled group, floor, effective group, external, total).
- Consultant FTE display is plain integer without currency formatting.
- Guarantee note appears only when modeled group revenue falls below the guaranteed floor.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Session state now holds the single source of truth for assumptions via st.session_state["case"], avoiding reloads on render and preserving edits across navigation.
- Scenario selection is applied to the session case for export and view-only pages without resetting assumptions.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Operational Steering Levers now write only to st.session_state["operational_steering"] and are applied at runtime without persisting into st.session_state["case"].
- Navigating into the P&L page clears operational steering values, while case assumptions remain intact.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Operational Steering Levers refactored into a compact Operational Stress Overlay with utilization, pricing, and cost inflation factors only.
- Overlay applies multiplicative runtime adjustments without writing back to case assumptions and resets to 1.00 values.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Cashflow table now separates operating cash generation from transaction/financing effects and labels free cashflow as pre-financing only.
- Transition Year header includes a one-off transaction/financing note for clarity.
- Net cashflow is labeled as after financing in both financing and liquidity sections.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Valuation page now focuses on seller price expectation and buyer sanity checks, removing exit/upside values.
- Seller valuation is a single-column table with reference EBIT, PV of 3-year EBIT, pensions, and seller expectation.
- Multiple-based and DCF labels updated to negotiation anchor and cashflow coverage respectively.

Manual verification:
- Ran `python -m streamlit run app.py --server.headless true --server.port 8502` (startup successful; command timed out after launch).
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed for navigation, statement fidelity, or formatting rules.

Changes:
- Reframed Equity Case into management-first sections with capital at risk, upside sources, and entry ownership context.
- Added cash-to-equity retention note, de-emphasized exit economics, and moved MOIC/IRR into a detailed analysis expander labeled indicative only.
- Added Investor Snapshot (Context Only) and softened pension impact highlight plus neutralized interpretation copy.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation or content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Rebuilt Valuation & Purchase Price to a seller price build-up with explicit year-by-year discounting from transition-year EBIT.
- Added indented substeps for discount factors and present values, highlighting only the final seller price expectation.
- Simplified buyer sanity checks to reference-only multiples and DCF cash coverage, with a compact interpretation block.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and the valuation page remains navigable with the new seller build-up and reference checks.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Removed intrinsic-valuation wording from the seller price build-up subheading for compliance with the valuation narrative constraints.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and the valuation page copy change does not affect layout or navigation.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Split the Overview decision core into valuation perspectives and a dedicated financing limit block.
- Rewired the financing ceiling to use debt capacity, equity at close, and minimum cash balance instead of exit value.
- Replaced gap labels with discount/headroom wording and updated the interpretation logic to keep positive = good.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and no navigation/content regressions introduced.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Rebuilt Valuation & Purchase Price around seller anchor, buyer value perspectives, and deal attractiveness with the required wording and separation.
- Removed seller discounting mechanics and detailed PV tables; anchor now uses reference EBIT and a simple multiple plus pension obligations.
- Added a clear price-vs-value block with enterprise/equity price, discounts to intrinsic and market reference, and implied multiple positioning.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and valuation navigation/content remain intact with the new structure.

Re-read ACCEPTANCE.md.

Violations:
- None observed.

Changes:
- Reinstated seller PV logic as a 3-year discounted EBIT anchor plus pensions; removed seller multiple from the seller block.
- Added a separate market multiple assumption and used it for market reference value while keeping buyer DCF intact.
- Expanded deal attractiveness to show EUR and % discounts with premium/discount labeling and added a detailed mechanics appendix.

Manual verification:
- Mental smoke test: app should start without errors, all pages render, inputs still affect outputs, and valuation tables/expanders render without navigation regressions.
