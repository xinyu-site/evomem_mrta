# Representative Dataset Instance

## 1. Raw Data

**Source:** `dataset/MT_MR_TA/prob_10`

### Natural-Language Description

In an urban environment mapped onto a two-dimensional XY Cartesian coordinate system, there are 3 air quality monitoring drones and 3 pollution sensing zones. These entities are designated as Robots and Tasks, respectively. Both robots and tasks are indexed starting from 0 (e.g., Robot 0, Robot 1, Robot 2, Task 0, Task 1, Task 2). The monitoring operation spans 3 discrete time steps, indexed from 0 to 2. The fleet handles multiple tasks across the schedule, and each drone can handle at most one sensing zone at any given time step. However, certain large pollution zones require multiple drones to scan them simultaneously (MR) to ensure accurate data collection; therefore, each sensing zone task specifies a required number of drones. Each task must be completed within a single time step that falls within its specific valid time window (defined by EarliestStep and LatestStep). The goal is to minimize the total Euclidean distance traveled by the drones while ensuring that every sensing zone receives its required number of simultaneous drones within its allowed timeframe.

### JSON Sample

```json
{
  "input": {
    "RobotPositions": [
      [0.0, 4.0],
      [1.0, 3.0],
      [2.0, 0.0]
    ],
    "TaskPositions": [
      [0.0, 3.0],
      [2.0, 1.0],
      [2.0, 2.0]
    ],
    "EarliestStep": [0, 0, 1],
    "LatestStep": [1, 2, 2],
    "NumRobots": 3,
    "NumTasks": 3,
    "TimeSteps": 3,
    "TaskRequirements": [2, 1, 1]
  },
  "output": [4.0]
}
```

## 2. Recommended Figure/Table Organization

Use this instance as a compact boxed example in the dataset section. The box should avoid excessive implementation details and instead expose the problem structure.

| Component | Recommended Content |
| --- | --- |
| Scenario title | Urban air-quality monitoring with cooperative drones |
| Category | `MT_MR_TA` |
| Robots | 3 drones: `R0=(0,4)`, `R1=(1,3)`, `R2=(2,0)` |
| Tasks | 3 pollution sensing zones: `T0=(0,3)`, `T1=(2,1)`, `T2=(2,2)` |
| Collaboration | `T0` requires 2 drones; `T1` and `T2` require 1 drone each |
| Time windows | `T0: [0,1]`, `T1: [0,2]`, `T2: [1,2]` |
| Planning horizon | 3 time steps: `t=0,1,2` |
| Objective | Minimize total Euclidean travel distance |
| Ground truth | Optimal objective value: `4.0` |

### Suggested Visual Layout

```text
Urban Air-Quality Monitoring Instance (MT_MR_TA)

Robots:
  R0 = (0, 4)
  R1 = (1, 3)
  R2 = (2, 0)

Pollution sensing zones:
  T0 = (0, 3), requires 2 drones, valid at t = 0..1
  T1 = (2, 1), requires 1 drone,  valid at t = 0..2
  T2 = (2, 2), requires 1 drone,  valid at t = 1..2

Goal:
  assign drones to zones within time windows
  minimize total travel distance
```

For the figure, draw a 2D coordinate plane with drones and sensing zones as different markers. Annotate each sensing zone with its requirement and time window, e.g., `T0: req=2, [0,1]`. This is enough for readers to understand the dataset item without reading the JSON.

## 3. Paper-Ready Explanation

**Short version for a figure caption.**  
An example `MT_MR_TA` instance from the benchmark. Three air-quality monitoring drones must be assigned to three pollution sensing zones over three discrete time steps. The first zone requires two drones simultaneously, while the other two zones require one drone each. Each zone has a valid execution time window, and the objective is to minimize the total Euclidean travel distance. The ground-truth optimal objective value is `4.0`.

**Paragraph version for the dataset section.**  
Figure X illustrates a representative instance from the `MT_MR_TA` category. The scenario is an urban air-quality monitoring task in which three drones must monitor three pollution sensing zones in a two-dimensional workspace. The instance combines several sources of MRTA difficulty: drones are scheduled over discrete time steps, tasks have individual validity windows, and one pollution zone requires two drones to be assigned simultaneously. The input therefore requires the solver to jointly reason about spatial distance, cooperative task demand, and temporal feasibility. The benchmark provides the corresponding ground-truth objective value, enabling execution-based verification of generated optimization code.

**More compact main-text version.**  
As a representative example, an `MT_MR_TA` instance describes an urban air-quality monitoring problem with three drones and three pollution sensing zones. The task requires spatial assignment, multi-robot cooperation, and scheduling within task-specific time windows. The solver must assign drones to zones while minimizing total Euclidean travel distance, with the optimal objective value provided as executable ground truth.

## 4. Why This Instance Works Well as the Paper Example

- It is concrete: drones and pollution sensing zones are easy for reviewers to understand.
- It is compact: only 3 robots, 3 tasks, and 3 time steps.
- It reflects difficulty: it includes spatial optimization, cooperation requirements, and time windows.
- It matches the taxonomy: it demonstrates `MT`, `MR`, and `TA` in a single instance.
- It is visually drawable: coordinates, requirements, and time windows can fit into one small figure.
