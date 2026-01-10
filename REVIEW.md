# Review Log

Use this file to append findings and decisions after each iteration.

## Iteration 1
- Findings: Case bar lacked hierarchy; KPI blocks stacked vertically; driver deltas were hard to scan; wizard steps lacked focus guidance.
- Decisions: Rebuilt case bar layout with columns and action grouping; moved KPI blocks into columns; formatted driver deltas; added short step descriptions and impact preview context.

## Iteration 2
- Findings: Percent inputs displayed as decimals; planning tables were hard to scan; notes were absent for key drivers; KPIs lacked consistent grouping.
- Decisions: Added percent display conversion with safe parsing; reordered year tables to mimic Excel; added driver notes; grouped KPIs into columns with short table context.

## Iteration 3
- Findings: Quick and Advanced sections duplicated inputs, risking conflicting edits; advanced sections still felt heavy.
- Decisions: Removed duplicated controls, kept only long-tail fields in Advanced, and added section separators to reduce cognitive load.

## Iteration 4
- Findings: Planning sheets still felt visually dense with little separation between quick and advanced areas.
- Decisions: Added consistent separators after quick inputs to improve scanning and reduce clutter.

## Iteration 5
- Findings: Residual jargon in labels, missing read-only summaries on planning pages, and inconsistent unit/formatting cues for currency and Year 0.
- Decisions: Simplified labels to plain language, added read-only summary blocks on every input page, standardized € units with thousand separators, and made Year 0 visually distinct.

## Iteration 6
- Findings: Sidebar structure diverged from required IA, case controls were too visible outside settings, statements lacked grouping emphasis, and number formatting did not meet k€/m€ and % rules.
- Decisions: Rebuilt sidebar into sectioned radio nav, moved case management/export into settings pages, added statement section headers and total emphasis, standardized k€/m€ and percent display, and added Base Case auto-clone protection.

## Iteration 7
- Findings: Sidebar still used radio navigation, case selector appeared outside Settings, planning pages displayed outputs, and export page defaulted to raw JSON.
- Decisions: Switched to button-based sidebar navigation, removed overview case selector and planning summaries, restructured export into key input/output summaries with collapsed raw JSON, and aligned navigation labels to full wording.

## Iteration 8
- Findings: Navigation did not match link-based sidebar; output headings diverged from screenshots; planning wizard appeared in Revenue Model; export lacked structured model facts/structure split.
- Decisions: Rebuilt sidebar as markdown links, aligned headings and statement labels, removed wizard from Revenue Model, added read-only assumption blocks to output pages, and restructured Model Export into Facts + Structure + Raw JSON.

## Iteration 9
- Findings: Input pages still diverged from screenshot sectioning; output pages lacked assumption blocks; valuation lacked KPI strip; balance sheet missed KPI summary.
- Decisions: Reorganized input sections, added derived capacity table, added assumption blocks to outputs, restored financial statement labels, and added valuation KPIs + balance sheet KPI summary.

## Iteration 10
- Findings: Financing page lacked Bank View layout; valuation page lacked seller/buyer subviews.
- Decisions: Rebuilt financing output into Bank View rows and added valuation expanders for seller and buyer views.

## Iteration 11
- Findings: Sidebar highlight needed left rail indicator; planning inputs still diverged from screenshot structure; financing Bank View formatting needed correction.
- Decisions: Added left-rail highlight, restructured planning inputs into screenshot sections, and aligned Bank View row formatting.

## Iteration 12
- Findings: Scenario controls were placed above planning titles; Year 0 labels and currency abbreviations did not match screenshots; statement tables lacked full section grouping; assumption tables showed % symbols and abbreviated EUR; equity case lacked management vs external split; valuation buyer view lacked structured rows.
- Decisions: Moved scenario selectors into Revenue/Cost pages, standardized Year 0 labels, rebuilt P&L/CF/BS tables with section headers and KPI rows, switched outputs to m EUR formatting and inputs to full EUR, added equity split/headline outcomes, rebuilt valuation buyer table with discount factors, and added financing footnotes plus balance sheet KPI summary.
