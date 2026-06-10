# MRTA Benchmark Dataset

## Compact Outline

- Taxonomy-driven design: define the benchmark by three MRTA axes, namely robot capability, task requirement, and assignment temporality.
- Instance composition: organize 200 instances into eight categories, with 25 instances per category.
- Instance fields: include natural-language descriptions, robot and task positions, task requirements, temporal windows, function templates, and ground-truth outputs.
- Evaluation value: support cross-category generalization, transferability, scalability, success-rate analysis, and execution-time evaluation.
- Concrete example: illustrate one `MT_MR_TA` instance so that reviewers can understand the data format and optimization target.

## Dataset Description

**Taxonomy-driven design.**  
We construct a taxonomy-driven MRTA benchmark that covers eight canonical multi-robot task assignment settings. The taxonomy is defined along three orthogonal dimensions: robot capability, task requirement, and assignment temporality. For robot capability, we distinguish single-task robots (`ST`), where each robot can execute at most one task at a time, from multi-task robots (`MT`), where a robot may be assigned to multiple tasks across the assignment process. For task requirement, we distinguish single-robot tasks (`SR`), which require exactly one robot, from multi-robot tasks (`MR`), which require multiple robots to cooperate on the same task. For assignment temporality, we consider instant assignment (`IA`), where tasks are assigned without future scheduling, and temporal assignment (`TA`), where tasks must be completed within valid time windows. Combining these dimensions yields eight MRTA categories: `ST_SR_IA`, `ST_MR_IA`, `MT_SR_IA`, `MT_MR_IA`, `ST_SR_TA`, `ST_MR_TA`, `MT_SR_TA`, and `MT_MR_TA`.

**Instance composition.**  
The benchmark contains 200 problem instances, with 25 instances in each MRTA category. Each instance is formulated as an executable optimization-oriented code-generation task and consists of three components: a natural-language task description, a function template specifying the required input-output interface, and a JSON test sample containing the input data and ground-truth output. The input fields describe the MRTA scenario, including robot positions, task positions, the number of robots, the number of tasks, robot capability assumptions, task requirements, collaboration constraints, and, for temporal settings, earliest and latest executable time steps. The ground truth is provided as either an optimal allocation structure or an optimal objective value, depending on the category. In particular, some instant multi-task settings require returning explicit task-to-robot assignments, whereas temporal optimization settings typically require returning the minimum total Euclidean travel distance.

**Why this benchmark is useful.**  
This benchmark is designed to evaluate whether LLM-based agents can solve MRTA problems beyond isolated problem instances. Because the eight categories share common spatial, combinatorial, and optimization structures while varying robot capability, task collaboration, and temporal constraints, the benchmark naturally supports cross-category generalization and transferability analysis. It also enables systematic evaluation of scalability across different problem sizes, success rate under executable testing, and execution time of generated solvers. For memory-augmented agents, the taxonomy further makes it possible to study whether experience acquired from one MRTA category can be reused to improve solving performance on related categories.

**Representative example instance.**  
For the main paper, a representative entry can be selected from `dataset/MT_MR_TA/prob_0` because it simultaneously contains multi-task robot capability, multi-robot task requirements, and temporal assignment constraints. This makes the example compact but expressive: it shows spatial reasoning, cooperative task requirements, scheduling within time windows, and an executable ground-truth objective.

| Field | Value |
| --- | --- |
| Category | `MT_MR_TA` |
| Scenario | Temporal multi-robot task assignment in a 2D Cartesian workspace |
| Robots | 3 robots at `[[0.0, 4.0], [1.0, 3.0], [2.0, 0.0]]` |
| Tasks | 3 tasks at `[[0.0, 3.0], [2.0, 1.0], [2.0, 2.0]]` |
| Robot capability | Multi-task robots, with at most one task per robot at each time step |
| Task requirement | `TaskRequirements = [2, 1, 1]`, where Task 0 requires two robots and Tasks 1-2 require one robot each |
| Temporal constraint | `EarliestStep = [0, 0, 1]`, `LatestStep = [1, 2, 2]`, `TimeSteps = 3` |
| Objective | Minimize the total Euclidean travel distance |
| Ground truth | Optimal objective value: `4.0` |

The corresponding JSON sample is:

```json
{
  "input": {
    "RobotPositions": [[0.0, 4.0], [1.0, 3.0], [2.0, 0.0]],
    "TaskPositions": [[0.0, 3.0], [2.0, 1.0], [2.0, 2.0]],
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

## Claim-Evidence Map

| Claim | Evidence | Status |
| --- | --- | --- |
| The dataset covers eight canonical MRTA settings. | The repository contains eight dataset folders corresponding to all combinations of `ST/MT`, `SR/MR`, and `IA/TA`. | Supported |
| The benchmark contains 200 instances. | Each of the eight categories contains 25 problem folders, yielding 200 instances in total. | Supported |
| Each instance includes natural-language and executable components. | Each problem folder contains `description.txt`, `code_example.py`, and `sample.json`. | Supported |
| Outputs vary between allocation structures and objective values. | `MT_SR_IA` and `MT_MR_IA` samples include assignment outputs, while many temporal categories provide optimal distance values. | Supported |
| The benchmark supports cross-category transfer and scalability evaluation. | The taxonomy shares core MRTA structure across categories while varying capability, collaboration, temporality, and problem size. | Supported |

## Self-Review Checklist

- Clarity: The dataset taxonomy is introduced before category names are used.
- Flow: The section moves from design rationale, to instance construction, to evaluation value, to a concrete example.
- Terminology consistency: `ST`, `MT`, `SR`, `MR`, `IA`, and `TA` are defined once and then reused consistently.
- Unsupported claims: Claims about performance improvement should be backed by experimental results elsewhere in the paper.
- Missing evidence: If the paper reports scalability, success rate, or execution time, add a table or figure in the experiments section that directly supports those claims.
