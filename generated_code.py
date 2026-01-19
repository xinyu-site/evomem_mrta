def prob_0(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements):
    """
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        EarliestStep: a list, earliest time step for each task
        LatestStep: a list, latest time step for each task
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
        TimeSteps: an integer, number of time steps
        TaskRequirements: list, number of robots required for each task
    Returns:
        total_distance: a float, the minimized sum of Euclidean distances between robots and tasks over all time steps
    """
    import math
    from gurobipy import Model, GRB, quicksum

    model = Model("RobotTaskAssignment")

    # Precompute Euclidean distances between robots and tasks
    distances = {}
    for r in range(NumRobots):
        for k in range(NumTasks):
            dx = RobotPositions[r][0] - TaskPositions[k][0]
            dy = RobotPositions[r][1] - TaskPositions[k][1]
            distances[r, k] = math.sqrt(dx**2 + dy**2)

    # Create assignment variables
    x = {}
    for r in range(NumRobots):
        for k in range(NumTasks):
            for t in range(TimeSteps):
                if EarliestStep[k] <= t <= LatestStep[k]:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, name=f'x_{r}_{k}_{t}')
                else:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, ub=0, name=f'x_{r}_{k}_{t}')

    # Task assignment constraints
    for k in range(NumTasks):
        model.addConstr(
            quicksum(x[r, k, t] for r in range(NumRobots) 
                    for t in range(EarliestStep[k], LatestStep[k] + 1)) == TaskRequirements[k],
            name=f'task_{k}_requirement'
        )

    # Robot capacity constraints (one task per robot per time step)
    for r in range(NumRobots):
        for t in range(TimeSteps):
            model.addConstr(
                quicksum(x[r, k, t] for k in range(NumTasks)) <= 1,
                name=f'robot_{r}_time_{t}_capacity'
            )

    # Objective: minimize total distance traveled
    total_distance = quicksum(
        distances[r, k] * x[r, k, t]
        for r in range(NumRobots)
        for k in range(NumTasks)
        for t in range(TimeSteps)
    )
    model.setObjective(total_distance, GRB.MINIMIZE)

    # Solve the model
    model.Params.LogToConsole = 0
    model.optimize()

    if model.status == GRB.OPTIMAL:
        return model.objVal
    else:
        return float('inf')