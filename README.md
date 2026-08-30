# RailBlock AI

An explainable decision-support prototype for **SIH26027: AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways**.

## Official team information

- **Institution:** Aditya University
- **Team:** Thedevodyssey
- **Members:** B. Rohith, Kavya Sharma, Shadiq, Sneha, S. Rohith, K. Anand Sai
- **PS ID:** SIH26027

No member roles or personal contact details are assigned or inferred in this project.

> Data notice: every train, asset, request, time, and result in this repository is simulated demonstration data. Nothing is presented as an official Indian Railways record, measured operational impact, deployed integration, or field-validated accuracy.

## What the prototype demonstrates

- maintenance requests with duration, priority, department, window, section and crew;
- simulated train paths, including protected and delay-tolerant paths;
- CP-SAT selection of feasible block start times at 15-minute resolution;
- hard train, section, window and crew constraints;
- priority-aware objective with explicit operational-interaction penalties;
- independent post-solve conflict validation;
- before/after KPIs and a visual possession timeline;
- event-driven re-planning when a demo train path is removed.

The app is a planner recommendation layer. It does not replace railway authorization, operating rules, or safety procedures.

## Quick start

Requires Python 3.11+.

```bash
uv sync --extra dev
uv run streamlit run app.py
uv run pytest
```

Open the local URL printed by Streamlit.

## Public deployment

The repository is ready for Streamlit Community Cloud and requires no secrets.

1. In Streamlit Community Cloud, select **Create app**.
2. Choose the `railblock-ai-sih26027` GitHub repository and the `main` branch.
3. Set the entry file to `app.py`.
4. Use Python 3.11 or newer; Python 3.11 is the recommended deployment baseline.
5. Leave the app URL and other advanced settings at their defaults, then deploy.

The platform installs the runtime packages from `requirements.txt`. Demo CSV files are resolved relative to the repository through `pathlib`, so the app does not depend on a Windows working directory or local absolute paths.

## Demo in 90 seconds

1. On **Command overview**, point to the orange simulated-data notice.
2. Compare the naive earliest-start baseline with the validated optimized plan.
3. Open **Block plan** and explain the colored section timeline, selected crews and independent validator.
4. Open **How it works** and explain hard constraints before the weighted objective.
5. In the sidebar, cancel a simulated train and click **Re-plan scenario** to show rolling re-optimization.
6. Close with **Limits & integration** to make the prototype boundary credible.

## Structure

- `app.py` — Streamlit demo and narrative
- `railblock/optimizer.py` — CP-SAT candidate selection and objective
- `railblock/validation.py` — independent safety/conflict checks
- `railblock/data.py` — deterministic CSV loading
- `data/` — explicitly simulated demo scenario
- `tests/` — core optimization and re-planning checks
- `docs/` — architecture, algorithm, data, pitch, Q&A, slide content

## Public references used for problem framing

- Indian Railways training material defines line blocks and integrated blocks: <https://scr.indianrailways.gov.in/cris/uploads/files/1338377919151-REF.SM.pdf>
- Indian Railways Track Machine Manual, Chapter 7, discusses block working and planning maintenance within block spells: <https://rdso.indianrailways.gov.in/works/uploads/File/IRTMM%202019%20CHAPTER%207.pdf>
- Google OR-Tools documents CP-SAT as suitable for discrete scheduling with constraints: <https://developers.google.com/optimization/cp>

See `docs/` for assumptions, formulation, integration path, risks, and judge preparation.
