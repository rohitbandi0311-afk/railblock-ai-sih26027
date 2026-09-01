# 🚆 RailBlock AI

### AI-Powered Automatic Block Planning for Indian Railways

> **Smart India Hackathon 2026 · SIH26027**  
> **Team Thedevodyssey · Aditya University**

RailBlock AI is an **explainable AI-assisted decision-support prototype** for planning railway maintenance blocks while minimizing disruption to train operations.

It evaluates **maintenance requests, train paths, time windows, sections, crews, priorities and operational conflicts** to recommend a feasible and optimized block plan.

---

## 🎯 SIH Problem Statement

**SIH26027 — AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways**

### Our Objective

> **Maximize asset availability while minimizing operational disruption and respecting railway planning constraints.**

---

## 💡 Our Solution

```text
Maintenance Requests + Train Schedule + Constraints
                         ↓
                  RailBlock AI Engine
                         ↓
                Constraint Validation
                         ↓
                 CP-SAT Optimization
                         ↓
              Recommended Block Plan
                         ↓
          Timeline + KPIs + Explanation
```

### ✨ Key Features

- 🛠️ Maintenance requests with duration, priority, department, section, crew and window
- 🚆 Train-path awareness with protected and delay-tolerant paths
- 🧠 **Google OR-Tools CP-SAT** constraint optimization
- ⏱️ 15-minute candidate block start resolution
- 🚫 Hard constraints for train, section, window and crew conflicts
- 🎯 Priority-aware objective with operational-interaction penalties
- 🔍 Independent post-solve conflict validation
- 📊 Before/after planning KPIs
- 📅 Visual possession / block timeline
- 🔄 Scenario-based dynamic re-planning
- 💬 Explainable recommendations

---

## 🏗️ Solution Architecture

```text
┌──────────────────────────────┐
│ Railway Input Data           │
│ Trains • Assets • Requests   │
│ Crews • Maintenance Windows  │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Data Preparation & Rules     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ RailBlock AI Optimization    │
│ Google OR-Tools CP-SAT       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Independent Validation       │
│ Conflict & Feasibility Check │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Recommended Block Plan       │
│ Timeline • KPIs • Explanation│
└──────────────────────────────┘
```

---

## 🧮 Why Optimization Instead of Greedy Scheduling?

A greedy approach may simply choose the **earliest available slot**. Railway block planning, however, involves multiple interacting constraints.

RailBlock AI considers the planning problem globally across:

- maintenance priority;
- train movement conflicts;
- maintenance duration;
- section availability;
- crew availability;
- permitted maintenance windows;
- operational interaction penalties.

Therefore, the system searches for a **better overall feasible plan**, rather than making an isolated earliest-slot decision.

---

## ⚙️ Technology Stack

| Layer | Technology |
|---|---|
| Application | **Streamlit / AI Studio prototype** |
| Optimization | **Google OR-Tools CP-SAT** |
| Language | **Python** |
| Data | **Simulated railway scenarios** |
| Validation | **Constraint checks** |
| Testing | **Pytest** |
| Version Control | **GitHub** |

---

## 🌐 Live Prototype

### 🚀 [Open RailBlock AI Prototype](https://railopt-ai-sih26027.ai.studio/)

**RailOpt AI — SIH26027 Prototype**

This is the primary interactive prototype for the SIH solution, demonstrating the proposed railway block-planning workflow, optimization logic, scheduling decisions and explainable outputs.

> **Prototype note:** The demonstration uses simulated data and is intended for SIH evaluation and concept demonstration. It does not represent official Indian Railways operational data.

---

## 👥 Team — Thedevodyssey

**Institution:** Aditya University  
**Problem Statement:** SIH26027

| Team Member |
|---|
| B. Rohith |
| Kavya Sharma |
| Shadiq |
| Sneha |
| S. Rohith |
| K. Anand Sai |

---

## 📁 Project Structure

```text
railblock-ai-sih26027/
│
├── app.py                    # Application
├── railblock/
│   ├── optimizer.py          # CP-SAT optimization engine
│   ├── validation.py         # Independent validation
│   └── data.py               # Scenario/data loading
│
├── data/                     # Simulated demonstration data
├── tests/                    # Optimization & re-planning tests
├── docs/                     # Architecture, algorithm & SIH material
├── requirements.txt          # Runtime dependencies
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

---

## ▶️ Run Locally

```bash
git clone https://github.com/rohitbandi0311-afk/railblock-ai-sih26027.git
cd railblock-ai-sih26027
pip install -r requirements.txt
streamlit run app.py
```

Run tests:

```bash
pytest
```

---

## 🔬 Research & References

The project is informed by:

- Indian Railways material on line and integrated blocks
- Indian Railways Track Machine Manual and maintenance planning concepts
- Google OR-Tools CP-SAT constraint programming documentation
- Railway asset, maintenance and operational scheduling concepts

Detailed assumptions, formulation, integration considerations and SIH judge-preparation material are available in `docs/`.

---

## ⚠️ Prototype Disclaimer

This repository is an **SIH proof-of-concept prototype**.

- All train, asset, maintenance, time and result data are **simulated demonstration data**.
- The system does **not** represent official Indian Railways operational data.
- It does **not replace railway authorization, operating rules, safety procedures or human decision-making**.
- Real-world TMS/SMMS/TDMS integration would require appropriate authorization, interfaces, security controls and domain validation.

---

## 🚀 Vision

RailBlock AI aims to evolve into an **intelligent railway maintenance planning assistant** that combines operational information with maintenance requirements and continuously recommends safer, more efficient block plans.

> **Plan smarter. Maintain faster. Keep trains moving. 🚆🇮🇳**

---

<div align="center">

### 🇮🇳 SMART INDIA HACKATHON 2026

**SIH26027 · RailBlock AI · Thedevodyssey**

</div>
