# Optimization formulation

Project: SIH26027 · Thedevodyssey · Aditya University

## Current demo

For maintenance request `i` and feasible candidate start `t`, binary variable `x(i,t)=1` means the block is selected at that time. Candidates are generated every 15 minutes inside both the request window and a section candidate window.

Hard constraints:

1. at most one candidate is selected per request;
2. candidates overlapping a protected train are removed;
3. overlapping candidates cannot share the same section;
4. overlapping candidates cannot share the same crew.

The demo maximizes this integer score:

```text
sum x(i,t) * [100 * priority(i) * duration(i)
              - 12 * weighted_train_overlap(i,t)
              - minutes_after_earliest_start(i,t)]
```

This makes safety/capacity non-negotiable while allowing the objective to trade maintenance value against permitted operational interaction. We report solver status and validate the output independently.

## What is and is not AI

Constraint optimization is the correct intelligent search technique here: it evaluates a combinatorial plan space under explicit rules. We do not attach a classifier merely for an “AI” label. In a future system, ML is useful only for evidence-based estimates such as duration distributions, asset failure risk and train-running uncertainty. Prediction outputs would feed the optimizer with confidence bounds, remain separately evaluated, and never relax a safety rule.

## Scaling path

- rolling planning horizons and section-based decomposition;
- precomputed candidate windows and dominance pruning;
- warm starts from the published plan;
- lexicographic objectives (safety feasibility, urgent work, disruption, utilization, stability);
- robust/scenario optimization for uncertainty;
- fixed solver time with incumbent/optimality-gap reporting;
- human-override reasons retained in the audit trail.

## Known simplifications

The demo has no detailed network topology, headway propagation, bidirectional line logic, isolation zones, equipment movement, possessions spanning midnight, probabilistic duration, precedence, or formal rule catalogue. These are future configuration/modeling tasks, not hidden claims.
