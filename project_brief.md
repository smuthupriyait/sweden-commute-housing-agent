# My agent: Sweden Housing & Commute Navigator
One-liner: A conversational agent that helps workers and newcomers in Sweden find and evaluate affordable housing within a realistic commute of their workplace, rendering rich A2UI cards and remembering user preferences across sessions.

Tool coverage:
- Memory: Remembers workplace location, net income & budget constraints, household composition, maximum acceptable commute time, and preferred transit modes across sessions.
- Tools: Official Statistics Sweden (SCB) rent per m² and tax lookup, rail/metro transit corridor travel time calculator, Konsumentverket baseline budget engine, verified municipal queue directory.
- Catalog/UI: Multi-criteria ranked residential areas, apartment listings, and municipal queue cards rendered as interactive A2UI cards/tables.
- Image gen: Generates visual neighborhood lifestyle previews and architectural impressions for recommended municipalities.
- Sandbox: Deterministic "Kvar att leva på" residual income and municipal tax rate calculations.

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Vertex AI Memory Bank, A2UI rich card renderer, Cloud Trace observability, Google Maps API transit routing.
