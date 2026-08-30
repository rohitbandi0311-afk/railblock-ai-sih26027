"""RailBlock AI — SIH26027 demonstration dashboard."""
import pandas as pd
import plotly.express as px
import streamlit as st
from railblock.data import hhmm, load_demo_data
from railblock.optimizer import baseline_plan, optimize_blocks

st.set_page_config(page_title="RailBlock AI", page_icon=":material/train:", layout="wide")
st.markdown("""<style>
.stApp{background:linear-gradient(145deg,#07111f 0%,#0b1728 56%,#101d2e 100%);color:#eef5ff}
[data-testid="stMetric"]{background:#10243a;border:1px solid #24445e;border-radius:14px;padding:14px}
.label{display:inline-block;background:#f5a623;color:#111827;padding:5px 10px;border-radius:999px;font-size:.76rem;font-weight:800}
.hero{padding:12px 0 6px}.hero h1{font-size:2.55rem;margin:.35rem 0}.muted{color:#9fb3c8}
.ok{border-left:4px solid #38d39f;background:#0e2c2b;padding:12px;border-radius:8px}.warn{border-left:4px solid #f5a623;background:#2d2514;padding:12px;border-radius:8px}
</style>""", unsafe_allow_html=True)

@st.cache_data
def demo_data(): return load_demo_data()

data = demo_data()
st.session_state.setdefault("cancelled", set())
st.session_state.setdefault("cancelled_train_selection", "None")

def apply_replan() -> None:
    selected = st.session_state.cancelled_train_selection
    st.session_state.cancelled = set() if selected == "None" else {selected}

def reset_scenario() -> None:
    st.session_state.cancelled = set()
    st.session_state.cancelled_train_selection = "None"

result = optimize_blocks(data["requests"], data["trains"], data["windows"], cancelled_train_ids=st.session_state.cancelled)
baseline = baseline_plan(data["requests"], data["trains"])

st.markdown('<div class="hero"><span class="label">SIH26027 · THEDEVODYSSEY · ADITYA UNIVERSITY</span><h1>RailBlock AI</h1><p class="muted">Explainable maintenance block planning that protects train paths and makes scarce possession time count.</p></div>', unsafe_allow_html=True)
st.info("DATA NOTICE · Every asset, train, time window and KPI shown here is deterministic simulated/demo data—not official Indian Railways operational data.", icon="ℹ️")

with st.sidebar:
    st.header("Control room")
    st.caption("Scenario: one simulated division, 3 sections, 12-hour horizon")
    st.metric("Solver status", result.status)
    st.selectbox(
        "Simulate train cancellation",
        ["None"] + data["trains"].train_id.tolist(),
        key="cancelled_train_selection",
    )
    st.button(
        "Re-plan scenario",
        type="primary",
        width="stretch",
        icon=":material/refresh:",
        on_click=apply_replan,
    )
    st.button("Reset", width="stretch", on_click=reset_scenario)
    st.divider()
    st.caption("Prototype boundary")
    st.write("Planning recommendation only. Human authorization and railway safety procedures remain mandatory.")
    st.divider()
    st.caption("Official team")
    st.write("**Thedevodyssey** · Aditya University")
    st.caption("B. Rohith · Kavya Sharma · Shadiq · Sneha · S. Rohith · K. Anand Sai")

overview, planning, inputs, logic, limits = st.tabs(["Command overview", "Block plan", "Input data", "How it works", "Limits & integration"])

with overview:
    metric_columns = [*st.columns(3), *st.columns(2)]
    values = [
        ("Requests planned", f"{result.metrics['scheduled_requests']}/{result.metrics['total_requests']}", "priority-aware"),
        ("Protected conflicts", result.metrics["protected_train_conflicts"], f"from {len(baseline.conflicts)} baseline issues"),
        ("Maintenance coverage", f"{result.metrics['maintenance_completion_pct']}%", "requested minutes"),
        ("Operational interaction", result.metrics["weighted_disruption_minutes"], "weighted min · simulated"),
        ("Solver time", f"{result.solve_seconds:.3f}s", "local demo run"),
    ]
    for column, (label, value, delta) in zip(metric_columns, values): column.metric(label, value, delta)
    st.subheader("Before → after")
    before, arrow, after = st.columns([5,1,5])
    with before:
        st.markdown('<div class="warn"><b>Manual earliest-start baseline</b><br>Schedules every request immediately; conflicts are detected after the fact.</div>', unsafe_allow_html=True)
        st.metric("Detected baseline conflicts", len(baseline.conflicts))
    with arrow: st.markdown("<h2 style='text-align:center;padding-top:35px'>→</h2>", unsafe_allow_html=True)
    with after:
        st.markdown('<div class="ok"><b>Optimized recommendation</b><br>Searches feasible windows and validates the recommended schedule.</div>', unsafe_allow_html=True)
        st.metric("Validated recommendation conflicts", len(result.conflicts))
    comparison = pd.DataFrame({"Plan":["Naive baseline","Optimized"], "Detected conflicts":[len(baseline.conflicts),len(result.conflicts)], "Scheduled requests":[len(baseline.plan),result.metrics["scheduled_requests"]]})
    st.plotly_chart(px.bar(comparison, x="Plan", y="Detected conflicts", color="Plan", text_auto=True, color_discrete_sequence=["#f16b6b","#38d39f"]), width="stretch")

with planning:
    st.subheader("Recommended block plan")
    scheduled = result.plan[result.plan.status == "Scheduled"].copy()
    if not scheduled.empty:
        scheduled["Start"] = scheduled.start_min.map(hhmm)
        scheduled["End"] = scheduled.end_min.map(hhmm)
        scheduled["timeline_start"] = pd.to_datetime("2026-08-30") + pd.to_timedelta(scheduled.start_min, unit="m")
        scheduled["timeline_end"] = pd.to_datetime("2026-08-30") + pd.to_timedelta(scheduled.end_min, unit="m")
        fig = px.timeline(scheduled, x_start="timeline_start", x_end="timeline_end", y="section_id", color="department", hover_name="request_id", hover_data=["work_type","Start","End","crew_id"], color_discrete_map={"Engineering":"#2f80ed","S&T":"#a96ff1","Electrical":"#f5a623"})
        fig.update_yaxes(autorange="reversed", title=None); fig.update_xaxes(title="Demo planning horizon")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(scheduled[["request_id","asset_id","work_type","section_id","department","crew_id","Start","End","priority","disruption"]], hide_index=True, width="stretch")
    deferred = result.plan[result.plan.status == "Deferred"]
    if not deferred.empty: st.warning(f"{len(deferred)} request(s) deferred because no selected option improved the constrained objective.")
    st.subheader("Independent conflict validation")
    if result.conflicts: st.dataframe(pd.DataFrame(result.conflicts), hide_index=True, width="stretch")
    else: st.success("No protected-train, request-window, section-capacity, or crew conflicts detected.")

with inputs:
    st.caption("All tables below are simulated and editable only in the CSV files for this prototype.")
    for title, key in [("Assets","assets"),("Maintenance requests","requests"),("Train paths","trains"),("Candidate windows","windows"),("Crews","resources")]:
        with st.expander(title, expanded=key == "requests"): st.dataframe(data[key], hide_index=True, width="stretch")

with logic:
    st.subheader("Why constraint optimization—not AI theatre")
    st.write("Block planning is a finite-domain scheduling problem. CP-SAT enumerates 15-minute candidate starts, removes unsafe options, then selects a globally compatible set.")
    st.markdown("""
**Hard constraints** · stay inside permitted windows; never overlap protected trains; one possession per section; one task per crew.

**Objective (integer score)** · maximize `100 × priority × maintenance minutes − 12 × weighted train-overlap minutes − start lateness`.

**Explainability** · each result exposes its window, crew, disruption score, solver status, and post-solve validation.

**Where ML belongs later** · predicting job duration, failure risk, and train-running uncertainty from historical systems. Those predictions are not fabricated in this prototype.
""")

with limits:
    st.subheader("Deployment boundary and integration path")
    st.markdown("""
- **Now:** deterministic single-day decision-support demo over synthetic CSV data.
- **Assumed:** discretized time, one capacity unit per section, simplified train interaction, crews represented by IDs.
- **Not claimed:** live railway connectivity, production safety certification, official data, measured field impact, or predictive accuracy.
- **Future integration:** authenticated adapters for timetable, asset, crew and possession systems; rule configuration by division; audit logs; role-based approval; rolling-horizon re-planning; shadow-mode validation before operational use.
""")
