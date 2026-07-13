# Architecture Documentation

## Objective
Generate compelling, visually accurate diagrams and accompanying Markdown texts summarizing the holistic system for non-technical stakeholders and new engineering hires.

----------------------------------------------------

## Representative Prompt

```text
Objective: Create professional architecture documentation for the project.

Requirements:
- Outline the split between the Offline Pipeline and the Online Pipeline.
- Write a Python rendering script to output the diagram programmatically to prevent dependence on external GUI tools.
- Export the visual architecture to three formats: `architecture.drawio` (XML), `architecture.svg` (vector), and `architecture.png` (raster).
- Ensure the text emphasizes *why* Hybrid Retrieval is the necessary foundation.
- Output everything to `docs/`.
```

----------------------------------------------------

## Outcome
- Produced beautiful, strictly formatted architecture visualizations.
- Eliminated the need for third-party diagramming subscription services by utilizing raw XML and Python plotting.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Architecture documentation inherently drifts from implementation if not easily updatable. Producing a standardized script to generate diagrams guarantees visual consistency across revisions.
- **Review Steps:** Checked the output XML format of `.drawio` to ensure it could actually be consumed by the Draw.io parsing engine.
- **Validation Approach:** Verified that the PNG exported cleanly without GUI rendering crashes during execution.
