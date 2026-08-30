# Architecture and workflow

Project: SIH26027 · Thedevodyssey · Aditya University  
Team members: B. Rohith, Kavya Sharma, Shadiq, Sneha, S. Rohith, K. Anand Sai

## Stakeholders

- **Operating/control:** protects train paths and reviews traffic impact.
- **Engineering, S&T, Electrical:** submit jobs, duration, priority, prerequisites and crews.
- **Asset managers:** set condition/risk priorities and maintenance deadlines.
- **Safety/authorization roles:** approve possessions under applicable railway rules.
- **Divisional leadership:** reviews utilization, deferrals and operational trade-offs.

## Decision flow

```text
Timetable + assets + work requests + crews + rules
                         |
                 validation/normalization
                         |
            candidate time-window generation
                         |
              hard constraint / rule engine
                         |
                CP-SAT optimization engine
                         |
            independent conflict validation
                         |
   ranked recommendation + reasons + KPIs + audit trail
                         |
                 human review and approval
```

## Production-shaped architecture

1. **Adapters:** timetable, asset register, work management, crew/resource roster, temporary restrictions and disruption feeds.
2. **Canonical data layer:** versioned planning snapshot, provenance, time zones, IDs and validation errors.
3. **Rules service:** configurable safety margins, section topology, possession types, isolation and resource rules.
4. **Prediction services (optional):** calibrated duration, failure-risk and running-time distributions trained only when sufficient historical data exists.
5. **Optimizer:** rolling-horizon CP-SAT/MIP decomposition with warm starts and bounded solve time.
6. **Validator:** independently recomputes conflicts and generates an infeasibility explanation.
7. **Workflow:** draft → review → authorize → publish → monitor → re-plan, with role-based access and audit events.
8. **Dashboard/API:** scenario comparison, recommended plan, reasons, overrides, exports and operational monitoring.

## Inputs, outputs and difficulty

Inputs include topology/capacity, train occupations, maintenance duration/windows/priority, possession type, department, crews, equipment, isolations and policy rules. Outputs are a feasible block start/end, assigned resources, affected paths, deferrals, conflict reasons, KPIs and alternatives.

The problem is difficult because capacity is shared, constraints span departments, time is discrete but large, disruptions propagate, duration is uncertain, urgent work competes with planned work, and a plan must be safe, explainable and quickly repairable.

## Integration stance

The prototype uses CSV adapters. Named enterprise systems and APIs are deliberately not claimed. A production discovery phase must confirm authoritative sources, schemas, update latency, approval roles, cyber requirements and the exact interpretation of each operating rule.
