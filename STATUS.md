IN PROGRESS

Iteration 1
- Polished top case bar layout and added clear case action grouping.
- Improved KPI layout and added concise explanatory notes on analysis pages.
- Added formatted driver deltas and step guidance in the planning wizard.

Iteration 2
- Improved input tables with notes and percent display formatting.
- Reordered year tables for Excel-style scanning and hid table indices.
- Added brief context copy to analysis tables and grouped KPIs into columns.

Iteration 3
- Removed duplicate inputs between Quick and Advanced sections to prevent conflicts.
- Narrowed Advanced sheets to long-tail controls only.
- Added separators around key analysis notes.

Iteration 4
- Added clear separators between quick inputs and advanced sections.
- Reduced visual density on planning sheets with consistent spacing.

Iteration 5
- Acceptance review found jargon labels, missing input summaries, and weak currency/unit formatting on tables.
- Simplified labels across outputs/inputs, added read-only summaries to every planning page, and made Year 0 visually distinct.
- Standardized currency units to "€", added thousand separators, clarified loan language, and added plain-language case error prompts.
- Remaining violations: none observed after this pass.

Iteration 6
- Violations found: sidebar structure did not match required IA; case management controls were outside settings; statements lacked grouping and totals emphasis; currency and percent formatting lacked k€/m€ and % signs; Base Case was at risk of being overwritten by default.
- Changes made: rebuilt sidebar into sectioned radio navigation; moved case management and export into Settings pages; embedded the wizard into Revenue Model as the recommended start; added statement section headers and total emphasis; standardized money display to k€/m€ and percent display to 70.0%; auto-clone Base Case into Working Copy on first edit; added case badge and overview case selector.

Iteration 7
- Violations found: sidebar still used radio navigation; case selector appeared outside Settings; planning pages included output summaries; export page defaulted to raw JSON; navigation labels still contained P&L shorthand.
- Changes made: replaced sidebar radios with button navigation; removed overview case selector and planning summaries; reworked export page into key input/output summaries with raw JSON collapsed; removed P&L shorthand in navigation; kept case badge read-only across pages.

Iteration 8
- Violations found: sidebar navigation did not match link-based structure; outputs showed non-screenshot headings; planning pages included non-screenshot wizard; outputs included guidance text; model export lacked Model Facts/Structure split.
- Changes made: rebuilt sidebar as markdown links with active highlighting; removed planning wizard from Revenue Model; aligned output headings and statement labels; added assumptions blocks on output pages to match screenshots; rebuilt Model Export into Facts + Structure + Raw JSON; restored scenario view line and top “Financial Model” title.
- Still wrong: Other Assumptions layout differs from screenshot sections; Financing & Debt table does not match Bank View layout; Equity Case lacks split investor/management detail; statement tables need closer row order/labels to screenshots.

Iteration 9
- Changes made: aligned Revenue/Cost/Other input sections to screenshot structure, added derived consultant capacity table, added assumption blocks to Cashflow/Balance Sheet/Financing/Valuation, restored P&L labels (EBITDA/EBIT/Net Income) and statement headings, added Valuation KPIs and Balance Sheet KPI summary, and removed scenario text from settings pages.
- Still wrong: Financing & Debt output rows do not match Bank View content; Equity Case lacks separate management vs investor breakdown; Valuation page missing seller/buyer valuation sub-tables; sidebar highlight lacks vertical indicator like screenshot.

Iteration 10
- Changes made: rebuilt Financing & Debt output to show Bank View-style rows (EBITDA, Cash Taxes, CFADS, Debt Service, DSCR), added valuation subviews (seller multiple / buyer cash-based), and added assumption cards with notes across output pages.
- Still wrong: sidebar highlight lacks left rail indicator; equity case still shows total equity only; Other Assumptions does not include investor exit year or distribution rule from screenshot; exact row ordering still differs from screenshots in P&L/Cashflow/BS.

Iteration 11
- Changes made: added left-rail highlight indicator in sidebar, aligned Revenue/Cost/Other inputs to screenshot sectioning, added scenario controls for planning pages, and corrected financing bank view formatting.
- Still wrong: Equity Case lacks split management vs external investor detail; Other Assumptions missing investor exit year/distribution rule; valuation missing full seller/buyer bridge tables from screenshots.

Iteration 12
- Violations found: scenario selector placement mismatched screenshots on planning pages; output tables used "Year 0 (Entry)" and k€/m€ formatting; P&L/Cashflow/Balance Sheet statements lacked screenshot row order and section headers; assumption tables showed % symbols and abbreviated EUR values; equity case lacked management vs external split; valuation buyer view lacked structured rows; duplicate headings and separators reduced fidelity.
- Changes made: moved scenario selectors into Revenue/Cost pages, removed extra separators, standardized Year 0 labels, rebuilt P&L/CF/BS tables with section headers and KPI rows, aligned output formatting to m EUR, updated assumption tables to show full EUR and % without symbols, added equity split and headline outcomes, rebuilt valuation buyer table and KPI gap %, and added financing footnotes + balance sheet KPI summary.
- Still wrong: Wizard default entry (Acceptance) conflicts with screenshot rebuild; acceptance forbids radio controls but screenshots show scenario radios; acceptance demands G&V summary on input pages (not shown in screenshots); exact statement row labels/spacing may still diverge from missing screenshots; buyer valuation discount logic is a proxy (interest rate) due to missing discount rate input.
