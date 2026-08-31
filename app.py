"""RailBlock AI — SIH26027 demonstration dashboard."""

from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from railblock.data import hhmm, load_demo_data
from railblock.optimizer import baseline_plan, optimize_blocks


ROOT = Path(__file__).resolve().parent
DEMO_DATE = "2026-08-30"
DEPARTMENT_COLORS = {
    "Engineering": "#3B82F6",
    "S&T": "#A78BFA",
    "Electrical": "#F59E0B",
}

st.set_page_config(
    page_title="RailBlock AI · SIH26027",
    page_icon=":material/train:",
    layout="wide",
    initial_sidebar_state="auto",
)
st.html(ROOT / "assets" / "railblock.css")


@st.cache_data
def demo_data() -> dict[str, pd.DataFrame]:
    """Load the deterministic demo inputs once per application process."""
    return load_demo_data()


def plan_snapshot(plan: pd.DataFrame) -> pd.DataFrame:
    """Return the UI fields needed for an honest previous/current comparison."""
    return plan[["request_id", "status", "start_min", "end_min"]].copy()


def compare_plans(previous: pd.DataFrame | None, current: pd.DataFrame) -> pd.DataFrame:
    """Describe schedule changes without altering the planning result."""
    if previous is None or previous.empty:
        return pd.DataFrame(columns=["Request", "Previous plan", "Updated plan", "Change"])

    def label(row: pd.Series) -> str:
        if row["status"] != "Scheduled" or pd.isna(row["start_min"]):
            return "Deferred"
        return f"{hhmm(row['start_min'])}–{hhmm(row['end_min'])}"

    previous_rows = previous.set_index("request_id")
    current_rows = current.set_index("request_id")
    changes: list[dict[str, str]] = []
    for request_id in current_rows.index:
        before = previous_rows.loc[request_id]
        after = current_rows.loc[request_id]
        before_label = label(before)
        after_label = label(after)
        if before_label == after_label:
            continue
        if before["status"] == "Scheduled" and after["status"] == "Scheduled":
            shift = int(after["start_min"] - before["start_min"])
            change = f"Shifted {shift:+d} min"
        elif after["status"] == "Scheduled":
            change = "Now scheduled"
        else:
            change = "Now deferred"
        changes.append(
            {
                "Request": request_id,
                "Previous plan": before_label,
                "Updated plan": after_label,
                "Change": change,
            }
        )
    return pd.DataFrame(changes)


def scenario_label(cancelled: set[str]) -> str:
    if not cancelled:
        return "Base simulated scenario"
    return f"Cancellation · {next(iter(cancelled))}"


def apply_replan() -> None:
    selected = st.session_state.cancelled_train_selection
    st.session_state.previous_plan_snapshot = st.session_state.get("active_plan_snapshot")
    st.session_state.previous_scenario_label = scenario_label(st.session_state.cancelled)
    st.session_state.cancelled = set() if selected == "None" else {selected}
    st.session_state.replan_pending = True
    st.session_state.reset_notice = False


def reset_scenario() -> None:
    st.session_state.cancelled = set()
    st.session_state.cancelled_train_selection = "None"
    st.session_state.replan_pending = False
    st.session_state.replan_summary = None
    st.session_state.reset_notice = True


def render_header() -> None:
    st.html(
        """
        <header class="rb-hero">
          <div class="rb-brand-lockup">
            <div class="rb-mark" aria-hidden="true">
              <span class="material-symbols-rounded">train</span>
            </div>
            <div>
              <div class="rb-eyebrow">AI-powered maintenance block planning</div>
              <h1>RailBlock <span>AI</span></h1>
              <p>Constraint-aware possession planning for safer, more available railway assets.</p>
            </div>
          </div>
          <div class="rb-hero-meta">
            <span class="rb-demo-dot"><i></i> Simulation / demo</span>
            <strong>SIH26027</strong>
            <span>Thedevodyssey · Aditya University</span>
          </div>
        </header>
        """
    )


def render_data_notice() -> None:
    st.html(
        """
        <div class="rb-data-notice" role="status">
          <span class="material-symbols-rounded" aria-hidden="true">verified_user</span>
          <div><strong>Deterministic simulation</strong><br>
          Every asset, train, time window and KPI is simulated/demo data—not official Indian Railways operational data.</div>
        </div>
        """
    )


def render_section_heading(eyebrow: str, title: str, description: str) -> None:
    st.html(
        f"""
        <div class="rb-section-heading">
          <span>{escape(eyebrow)}</span>
          <h2>{escape(title)}</h2>
          <p>{escape(description)}</p>
        </div>
        """
    )


def render_kpis(result, baseline) -> None:
    kpis = [
        ("event_available", "Requests planned", f"{result.metrics['scheduled_requests']}/{result.metrics['total_requests']}", "Priority-aware schedule", "success"),
        ("shield", "Protected conflicts", str(result.metrics["protected_train_conflicts"]), f"From {len(baseline.conflicts)} baseline issues", "success"),
        ("construction", "Maintenance coverage", f"{result.metrics['maintenance_completion_pct']}%", "Requested minutes · simulated", "success"),
        ("swap_horiz", "Operational interaction", str(result.metrics["weighted_disruption_minutes"]), "Weighted minutes · simulated", "neutral"),
        ("timer", "Solver time", f"{result.solve_seconds:.3f}s", "Current demo run", "neutral"),
    ]
    cards = "".join(
        f"""
        <article class="rb-kpi-card rb-kpi-{tone}">
          <div class="rb-kpi-top"><span class="material-symbols-rounded">{icon}</span><i></i></div>
          <div class="rb-kpi-label">{escape(label)}</div>
          <div class="rb-kpi-value">{escape(value)}</div>
          <div class="rb-kpi-note">{escape(note)}</div>
        </article>
        """
        for icon, label, value, note, tone in kpis
    )
    st.html(f'<div class="rb-kpi-grid">{cards}</div>')


def render_before_after(result, baseline) -> None:
    st.html(
        f"""
        <section class="rb-comparison" aria-label="Simulated before and after comparison">
          <div class="rb-comparison-head">
            <div><span>Decision impact</span><h2>Before vs after</h2></div>
            <span class="rb-sim-chip">Simulated demo result</span>
          </div>
          <div class="rb-comparison-grid">
            <article class="rb-before-card">
              <div class="rb-result-label"><span class="material-symbols-rounded">warning</span> Before</div>
              <div class="rb-result-value">{len(baseline.conflicts)}</div>
              <div class="rb-result-unit">conflicts</div>
              <p>Naive earliest-start baseline schedules first and detects conflicts afterward.</p>
            </article>
            <div class="rb-optimize-bridge">
              <span class="material-symbols-rounded">arrow_forward</span>
              <strong>Optimize</strong>
              <small>CP-SAT + rules</small>
            </div>
            <article class="rb-after-card">
              <div class="rb-result-label"><span class="material-symbols-rounded">verified</span> After</div>
              <div class="rb-result-value">{len(result.conflicts)}</div>
              <div class="rb-result-unit">validator conflicts</div>
              <p>Recommended plan is checked independently after optimization.</p>
            </article>
          </div>
          <div class="rb-result-strip">
            <div><strong>{result.metrics['scheduled_requests']}/{result.metrics['total_requests']}</strong><span>requests scheduled</span></div>
            <div><strong>{result.metrics['maintenance_completion_pct']}%</strong><span>simulated maintenance coverage</span></div>
            <div><strong>{escape(result.status)}</strong><span>solver status</span></div>
          </div>
        </section>
        """
    )


def render_replan_summary(summary: dict | None) -> None:
    if not summary:
        return
    changes = summary["changes"]
    change_count = len(changes)
    st.html(
        f"""
        <section class="rb-scenario-result">
          <div class="rb-scenario-icon"><span class="material-symbols-rounded">published_with_changes</span></div>
          <div class="rb-scenario-copy">
            <span>Scenario updated</span>
            <h3>Plan re-optimized successfully</h3>
            <p>{escape(summary['previous_scenario'])} → {escape(summary['current_scenario'])}</p>
          </div>
          <div class="rb-scenario-stats">
            <div><strong>{escape(summary['status'])}</strong><span>solver</span></div>
            <div><strong>{summary['conflicts']}</strong><span>conflicts</span></div>
            <div><strong>{summary['planned']}</strong><span>planned</span></div>
            <div><strong>{change_count}</strong><span>changed</span></div>
          </div>
        </section>
        """
    )
    if change_count:
        with st.expander(
            f"Inspect {change_count} changed request{'s' if change_count != 1 else ''}",
            icon=":material/compare_arrows:",
        ):
            st.dataframe(
                changes,
                hide_index=True,
                width="stretch",
                column_config={
                    "Request": st.column_config.TextColumn(width="small", pinned=True),
                    "Previous plan": st.column_config.TextColumn(width="medium"),
                    "Updated plan": st.column_config.TextColumn(width="medium"),
                    "Change": st.column_config.TextColumn(width="medium"),
                },
            )
    else:
        st.info(
            "The selected cancellation was not a binding constraint for the recommended schedule, so request timings did not change.",
            icon=":material/info:",
        )


data = demo_data()
st.session_state.setdefault("cancelled", set())
st.session_state.setdefault("cancelled_train_selection", "None")
st.session_state.setdefault("active_plan_snapshot", None)
st.session_state.setdefault("previous_plan_snapshot", None)
st.session_state.setdefault("previous_scenario_label", "Base simulated scenario")
st.session_state.setdefault("replan_pending", False)
st.session_state.setdefault("replan_summary", None)
st.session_state.setdefault("reset_notice", False)

result = optimize_blocks(
    data["requests"],
    data["trains"],
    data["windows"],
    cancelled_train_ids=st.session_state.cancelled,
)
baseline = baseline_plan(data["requests"], data["trains"])

if st.session_state.replan_pending:
    changes = compare_plans(st.session_state.previous_plan_snapshot, result.plan)
    st.session_state.replan_summary = {
        "previous_scenario": st.session_state.previous_scenario_label,
        "current_scenario": scenario_label(st.session_state.cancelled),
        "status": result.status,
        "conflicts": len(result.conflicts),
        "planned": f"{result.metrics['scheduled_requests']}/{result.metrics['total_requests']}",
        "changes": changes,
    }
    st.session_state.replan_pending = False

st.session_state.active_plan_snapshot = plan_snapshot(result.plan)


with st.sidebar:
    st.html(
        """
        <div class="rb-control-title">
          <span class="material-symbols-rounded">tune</span>
          <div><span>Operations console</span><strong>Control panel</strong></div>
        </div>
        """
    )
    with st.container(border=True, key="scenario_info"):
        st.caption("ACTIVE DEMO SCENARIO")
        st.markdown("**One simulated division**")
        st.caption("3 sections · 12-hour planning horizon")
        status_color = "green" if result.status in {"OPTIMAL", "FEASIBLE"} else "orange"
        st.badge(result.status, icon=":material/check_circle:", color=status_color)
        st.caption("Current CP-SAT solver status")

    st.caption("SCENARIO CHANGE")
    train_names = data["trains"].set_index("train_id")["train_name"].to_dict()
    train_sections = data["trains"].set_index("train_id")["section_id"].to_dict()

    def format_train(train_id: str) -> str:
        if train_id == "None":
            return "No train cancellation"
        return f"{train_id} · {train_names[train_id]} · {train_sections[train_id]}"

    selected_train = st.selectbox(
        "Simulated train cancellation",
        ["None"] + data["trains"].train_id.tolist(),
        key="cancelled_train_selection",
        format_func=format_train,
        help="Select a simulated train path to remove, then apply re-planning.",
    )
    selected_cancelled = set() if selected_train == "None" else {selected_train}
    if selected_cancelled != st.session_state.cancelled:
        st.warning(
            "Scenario change staged. Apply re-planning to update the recommendation.",
            icon=":material/pending_actions:",
        )
    elif st.session_state.cancelled:
        st.success(
            f"Scenario applied · {selected_train} cancelled in simulation",
            icon=":material/check_circle:",
        )
    else:
        st.caption("Base scenario is currently applied.")

    st.button(
        "Re-plan scenario",
        type="primary",
        width="stretch",
        icon=":material/refresh:",
        on_click=apply_replan,
        key="replan_action",
    )
    st.button(
        "Reset base scenario",
        width="stretch",
        icon=":material/restart_alt:",
        on_click=reset_scenario,
        key="reset_action",
    )

    if st.session_state.reset_notice:
        st.toast("Base scenario restored", icon=":material/check_circle:")
        st.session_state.reset_notice = False

    with st.container(border=True, key="safety_boundary"):
        st.markdown(":material/health_and_safety: **Prototype boundary**")
        st.caption(
            "Planning recommendation only. Human authorization and railway safety procedures remain mandatory."
        )

    st.caption("OFFICIAL TEAM")
    st.markdown("**Thedevodyssey** · Aditya University")
    st.caption("B. Rohith · Kavya Sharma · Shadiq · Sneha · S. Rohith · K. Anand Sai")


render_header()
render_data_notice()

overview, planning, inputs, logic, limits = st.tabs(
    [
        ":material/space_dashboard: Command overview",
        ":material/route: Block plan",
        ":material/database: Input data",
        ":material/account_tree: How it works",
        ":material/shield: Limits & integration",
    ]
)

with overview:
    render_section_heading(
        "Current recommendation",
        "Operational snapshot",
        "A ten-second view of the deterministic simulated planning result.",
    )
    render_replan_summary(st.session_state.replan_summary)
    render_kpis(result, baseline)
    render_before_after(result, baseline)

    with st.expander("Inspect conflict comparison chart", icon=":material/bar_chart:"):
        comparison = pd.DataFrame(
            {
                "Plan": ["Naive baseline", "Optimized recommendation"],
                "Detected conflicts": [len(baseline.conflicts), len(result.conflicts)],
                "Scheduled requests": [len(baseline.plan), result.metrics["scheduled_requests"]],
            }
        )
        comparison_chart = px.bar(
            comparison,
            x="Plan",
            y="Detected conflicts",
            color="Plan",
            text_auto=True,
            color_discrete_sequence=["#F97366", "#2DD4A8"],
        )
        comparison_chart.update_layout(
            height=320,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None,
            yaxis_title="Validator conflicts",
            font=dict(color="#DCE8F2"),
        )
        comparison_chart.update_yaxes(gridcolor="rgba(151,170,190,0.16)", rangemode="tozero")
        st.plotly_chart(comparison_chart, width="stretch", config={"displayModeBar": False})

with planning:
    render_section_heading(
        "Recommended possession plan",
        "Block plan",
        "Optimized maintenance blocks across the simulated sections and planning horizon.",
    )
    if st.session_state.replan_summary:
        render_replan_summary(st.session_state.replan_summary)

    scheduled = result.plan[result.plan.status == "Scheduled"].copy()
    if not scheduled.empty:
        scheduled = scheduled.merge(
            data["assets"][["asset_id", "asset_name"]], on="asset_id", how="left"
        )
        scheduled["Start"] = scheduled.start_min.map(hhmm)
        scheduled["End"] = scheduled.end_min.map(hhmm)
        scheduled["timeline_start"] = pd.to_datetime(DEMO_DATE) + pd.to_timedelta(
            scheduled.start_min, unit="m"
        )
        scheduled["timeline_end"] = pd.to_datetime(DEMO_DATE) + pd.to_timedelta(
            scheduled.end_min, unit="m"
        )
        scheduled["section_label"] = scheduled["section_id"].map(lambda value: f"Section {value}")

        st.html(
            """
            <div class="rb-panel-caption">
              <div><span class="material-symbols-rounded">calendar_month</span><strong>Possession timeline</strong></div>
              <span>Hover over a block for complete request details</span>
            </div>
            """
        )
        timeline = px.timeline(
            scheduled,
            x_start="timeline_start",
            x_end="timeline_end",
            y="section_label",
            color="department",
            text="request_id",
            custom_data=[
                "request_id",
                "asset_name",
                "asset_id",
                "work_type",
                "crew_id",
                "Start",
                "End",
                "priority",
                "disruption",
                "window_id",
            ],
            color_discrete_map=DEPARTMENT_COLORS,
            category_orders={"section_label": ["Section SEC-A", "Section SEC-B", "Section SEC-C"]},
        )
        timeline.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            marker_line_color="rgba(255,255,255,0.28)",
            marker_line_width=1,
            hovertemplate=(
                "<b>%{customdata[0]} · %{customdata[3]}</b><br>"
                "Asset: %{customdata[1]} (%{customdata[2]})<br>"
                "Crew: %{customdata[4]}<br>"
                "Block: %{customdata[5]}–%{customdata[6]}<br>"
                "Priority: %{customdata[7]}<br>"
                "Weighted disruption: %{customdata[8]} min<br>"
                "Candidate window: %{customdata[9]}<extra></extra>"
            ),
        )
        timeline.update_yaxes(
            autorange="reversed",
            title=None,
            gridcolor="rgba(151,170,190,0.12)",
            tickfont=dict(size=13),
        )
        timeline.update_xaxes(
            title="Simulated planning horizon · HH:MM",
            tickformat="%H:%M",
            dtick=60 * 60 * 1000,
            gridcolor="rgba(151,170,190,0.14)",
            showline=True,
            linecolor="rgba(151,170,190,0.24)",
        )
        timeline.update_layout(
            height=430,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(10,24,36,0.38)",
            font=dict(color="#DCE8F2"),
            legend=dict(
                title="Maintenance department",
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="left",
                x=0,
            ),
            margin=dict(l=20, r=20, t=62, b=40),
            bargap=0.34,
            hoverlabel=dict(bgcolor="#102333", font_color="#F4F8FB", bordercolor="#34506A"),
        )
        st.plotly_chart(
            timeline,
            width="stretch",
            config={"displaylogo": False, "scrollZoom": False, "responsive": True},
        )
        st.caption(
            "Blocks, train interactions and windows are derived only from deterministic simulated CSV inputs."
        )

        st.html(
            """
            <div class="rb-panel-caption rb-table-heading">
              <div><span class="material-symbols-rounded">table_rows</span><strong>Request schedule</strong></div>
              <span>Sorted by section and optimized start time</span>
            </div>
            """
        )
        plan_table = result.plan.merge(
            data["assets"][["asset_id", "asset_name"]], on="asset_id", how="left"
        ).copy()
        plan_table["Status"] = plan_table["status"].map(
            {"Scheduled": "● Scheduled", "Deferred": "○ Deferred"}
        )
        plan_table["Request"] = plan_table["request_id"]
        plan_table["Asset"] = plan_table.apply(
            lambda row: f"{row['asset_name']} · {row['asset_id']}", axis=1
        )
        plan_table["Work type"] = plan_table["work_type"]
        plan_table["Section"] = plan_table["section_id"]
        plan_table["Department"] = plan_table["department"]
        plan_table["Crew"] = plan_table["crew_id"]
        plan_table["Start"] = plan_table.apply(
            lambda row: hhmm(row.start_min) if row.status == "Scheduled" else "—", axis=1
        )
        plan_table["End"] = plan_table.apply(
            lambda row: hhmm(row.end_min) if row.status == "Scheduled" else "—", axis=1
        )
        plan_table["Duration"] = plan_table["duration_min"]
        plan_table["Priority"] = plan_table["priority"]
        plan_table["Disruption"] = plan_table["disruption"]
        display_columns = [
            "Status",
            "Request",
            "Asset",
            "Work type",
            "Section",
            "Department",
            "Crew",
            "Start",
            "End",
            "Duration",
            "Priority",
            "Disruption",
        ]
        st.dataframe(
            plan_table.sort_values(["section_id", "start_min"])[display_columns],
            hide_index=True,
            width="stretch",
            height=320,
            column_config={
                "Status": st.column_config.TextColumn(width="medium", pinned=True),
                "Request": st.column_config.TextColumn(width="small", pinned=True),
                "Asset": st.column_config.TextColumn(width="large"),
                "Work type": st.column_config.TextColumn(width="large"),
                "Section": st.column_config.TextColumn(width="small"),
                "Department": st.column_config.TextColumn(width="medium"),
                "Crew": st.column_config.TextColumn(width="small"),
                "Start": st.column_config.TextColumn(width="small"),
                "End": st.column_config.TextColumn(width="small"),
                "Duration": st.column_config.NumberColumn("Duration (min)", width="small"),
                "Priority": st.column_config.NumberColumn(width="small"),
                "Disruption": st.column_config.NumberColumn(
                    "Weighted disruption (min)", width="small"
                ),
            },
        )

    deferred = result.plan[result.plan.status == "Deferred"]
    if not deferred.empty:
        st.warning(
            f"{len(deferred)} request(s) were deferred because no selected option improved the constrained objective.",
            icon=":material/schedule:",
        )

    with st.container(border=True, key="validator_panel"):
        st.markdown("#### :material/fact_check: Independent conflict validation")
        if result.conflicts:
            st.error(
                f"The independent validator detected {len(result.conflicts)} conflict(s).",
                icon=":material/error:",
            )
            st.dataframe(pd.DataFrame(result.conflicts), hide_index=True, width="stretch")
        else:
            st.success(
                "Conflict-free recommendation: no protected-train, request-window, section-capacity or crew conflicts detected.",
                icon=":material/verified:",
            )

with inputs:
    render_section_heading(
        "Transparent demo inputs",
        "Input data",
        "Inspect every deterministic simulated table used by the optimizer and validator.",
    )
    st.info(
        "These datasets are read-only in the dashboard and editable only through the repository CSV files.",
        icon=":material/info:",
    )
    input_tables = [
        ("Assets", "assets", ":material/precision_manufacturing:"),
        ("Maintenance requests", "requests", ":material/construction:"),
        ("Train paths", "trains", ":material/train:"),
        ("Candidate windows", "windows", ":material/date_range:"),
        ("Crews", "resources", ":material/groups:"),
    ]
    for title, key, icon in input_tables:
        with st.expander(
            f"{title} · {len(data[key])} records",
            expanded=key == "requests",
            icon=icon,
        ):
            st.dataframe(data[key], hide_index=True, width="stretch")

with logic:
    render_section_heading(
        "Explainable decision pipeline",
        "How it works",
        "Optimization, railway rules and validation remain separate and auditable.",
    )
    pipeline_steps = [
        ("construction", "Maintenance requests"),
        ("rule", "Railway constraints"),
        ("calculate", "CP-SAT optimization"),
        ("fact_check", "Independent validator"),
        ("route", "Recommended block plan"),
        ("approval", "Human approval"),
        ("refresh", "Re-planning"),
    ]
    pipeline_html = "".join(
        f"""
        <div class="rb-pipeline-step"><span class="material-symbols-rounded">{icon}</span><strong>{escape(label)}</strong></div>
        {'' if index == len(pipeline_steps) - 1 else '<span class="rb-pipeline-arrow material-symbols-rounded">arrow_forward</span>'}
        """
        for index, (icon, label) in enumerate(pipeline_steps)
    )
    st.html(f'<div class="rb-pipeline">{pipeline_html}</div>')

    approach_left, approach_right = st.columns(2, gap="large")
    with approach_left:
        with st.container(border=True, height="stretch", key="optimization_card"):
            st.markdown("#### :material/calculate: What is implemented")
            st.markdown(
                """
                - **CP-SAT constraint optimization:** selects compatible 15-minute candidate starts.
                - **Railway rules:** enforce request windows, protected trains, section capacity and crew availability.
                - **Independent validation:** checks the proposed plan after solving.
                - **Explainability:** exposes selected window, crew, disruption, solver status and validation result.
                """
            )
    with approach_right:
        with st.container(border=True, height="stretch", key="ai_boundary_card"):
            st.markdown("#### :material/psychology_alt: AI boundary")
            st.warning(
                "CP-SAT is constraint optimization—not machine learning.",
                icon=":material/priority_high:",
            )
            st.markdown(
                "RailBlock AI is an **AI-assisted intelligent planning system** built from optimization, explicit rules and validation. No trained ML model is implemented or claimed in this prototype."
            )

    with st.container(border=True, key="objective_card"):
        st.markdown("#### :material/target: Objective aligned to asset availability")
        st.code(
            "maximize 100 × priority × maintenance minutes\n"
            "       − 12 × weighted train-overlap minutes\n"
            "       − start lateness",
            language="text",
        )
        st.caption(
            "The objective rewards priority-weighted maintenance completion inside safe windows while penalizing operational interaction and late starts. This supports the PS goal of maximizing asset availability without claiming measured field impact."
        )

with limits:
    render_section_heading(
        "Safety and deployment boundary",
        "Limits & integration",
        "A credible prototype is explicit about what is implemented and what remains future work.",
    )
    limit_columns = st.columns(3, gap="medium")
    with limit_columns[0]:
        with st.container(border=True, height="stretch"):
            st.markdown("#### :material/check_circle: Current prototype")
            st.markdown(
                "Deterministic single-day decision support over simulated CSV data, with CP-SAT optimization and independent validation."
            )
    with limit_columns[1]:
        with st.container(border=True, height="stretch"):
            st.markdown("#### :material/block: Not claimed")
            st.markdown(
                "No live railway connectivity, official operational data, production deployment, safety certification, trained ML model, predictive accuracy or measured field impact."
            )
    with limit_columns[2]:
        with st.container(border=True, height="stretch"):
            st.markdown("#### :material/route: Future integration path")
            st.markdown(
                "Authenticated timetable, asset, crew and possession adapters; configurable division rules; audit logs; role-based approval; rolling-horizon re-planning; shadow-mode validation."
            )

    st.warning(
        "All operational data and KPIs are deterministic simulated/demo data. Human authorization and railway safety procedures remain mandatory.",
        icon=":material/health_and_safety:",
    )
