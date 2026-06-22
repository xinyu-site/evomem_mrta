# MRTA Benchmark Dataset

This directory contains a taxonomy-driven benchmark for multi-robot task allocation (MRTA). The dataset is organized by three MRTA dimensions: robot capability, task requirement, and assignment temporality. It contains 200 executable code-generation instances across eight canonical MRTA categories.

## Dataset Overview

The benchmark contains eight categories, with 25 problem instances in each category.

| Category | Robot capability | Task requirement | Temporality |
| --- | --- | --- | --- |
| `ST_SR_IA` | Single-task robots | Single-robot tasks | Instant assignment |
| `ST_MR_IA` | Single-task robots | Multi-robot tasks | Instant assignment |
| `MT_SR_IA` | Multi-task robots | Single-robot tasks | Instant assignment |
| `MT_MR_IA` | Multi-task robots | Multi-robot tasks | Instant assignment |
| `ST_SR_TA` | Single-task robots | Single-robot tasks | Temporal assignment |
| `ST_MR_TA` | Single-task robots | Multi-robot tasks | Temporal assignment |
| `MT_SR_TA` | Multi-task robots | Single-robot tasks | Temporal assignment |
| `MT_MR_TA` | Multi-task robots | Multi-robot tasks | Temporal assignment |

The abbreviations mean:

- `ST`: a robot can execute at most one task at a time.
- `MT`: a robot may serve multiple tasks across the assignment process.
- `SR`: each task requires one robot.
- `MR`: at least one task requires multiple robots simultaneously.
- `IA`: assignments are made for an instant/static setting.
- `TA`: tasks must be scheduled within valid time windows.

## Directory Structure

Each category folder contains 25 problem folders:

```text
dataset/
  MT_MR_TA/
    prob_0/
      description.txt
      code_example.py
      sample.json
    ...
  ST_SR_IA/
    prob_0/
      description.txt
      code_example.py
      sample.json
    ...
```

Each problem folder contains:

| File | Description |
| --- | --- |
| `description.txt` | Natural-language MRTA problem description. |
| `code_example.py` | Function signature and reference-style solver template for the required input-output interface. |
| `sample.json` | Test input and ground-truth output used for execution-based evaluation. |

## Instance Format

The input fields vary by MRTA category, but commonly include:

- `RobotPositions`: 2D positions of robots.
- `TaskPositions`: 2D positions of tasks.
- `NumRobots`: number of robots.
- `NumTasks`: number of tasks.
- `TaskRequirements`: number of robots required by each task, used in multi-robot-task settings.
- `EarliestStep` and `LatestStep`: valid execution windows, used in temporal-assignment settings.
- `TimeSteps`: planning horizon length, used in temporal-assignment settings.

The output is stored as a list in `sample.json`. Depending on the category, it may represent an optimal objective value, such as minimum total Euclidean distance, or an allocation structure.

## Representative Example

`MT_MR_TA/prob_0` is a compact representative example because it combines multi-task robot capability, multi-robot task requirements, and temporal assignment constraints.

```json
[
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
]
```

In this instance, Task 0 requires two robots, Tasks 1 and 2 require one robot each, and every task must be completed within its time window. The objective is to minimize the total Euclidean travel distance; the optimal value is `4.0`.

## Reading The Dataset

The following snippet loads all problem instances:

```python
import json
from pathlib import Path

dataset_root = Path("dataset")

for category_dir in sorted(p for p in dataset_root.iterdir() if p.is_dir()):
    for problem_dir in sorted(p for p in category_dir.iterdir() if p.is_dir()):
        description = (problem_dir / "description.txt").read_text(encoding="utf-8")
        code_template = (problem_dir / "code_example.py").read_text(encoding="utf-8")
        samples = json.loads((problem_dir / "sample.json").read_text(encoding="utf-8"))

        print(category_dir.name, problem_dir.name, len(description), len(samples))
```

## Evaluation Use

The benchmark is designed for executable evaluation of LLM-generated MRTA solvers. A model receives the natural-language description and function interface, generates Python code, and is evaluated by running the generated function against the test sample. This setup supports category-wise success-rate analysis, cross-category transfer experiments, ablation studies, and error diagnosis across different MRTA structures.
