def prob_11(RobotPositions, TaskPositions, EarliestStep, LatestStep, TaskRequirements, NumRobots, NumTasks, TimeSteps):
    """ 
    Args:
        RobotPositions: list of lists, positions of robots in Cartesian coordinates
        TaskPositions: list of lists, positions of tasks in Cartesian coordinates
        EarliestStep: list, earliest allowed time step for each task
        LatestStep: list, latest allowed time step for each task
        TaskRequirements: list, number of robots required for each task
        NumRobots: integer, number of robots
        NumTasks: integer, number of tasks
        TimeSteps: integer, total scheduling time steps
    
    Returns:
        total_distance: float, minimized total Euclidean distance
    """
    
    import numpy as np
    from gurobipy import Model, GRB, quicksum

    def euclidean_distance(p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # Precompute distance matrix
    dist_matrix = np.zeros((NumRobots, NumTasks))
    for i in range(NumRobots):
        for j in range(NumTasks):
            dist_matrix[i][j] = euclidean_distance(RobotPositions[i], TaskPositions[j])

    # Validate time windows
    adj_earliest = []
    adj_latest = []
    for j in range(NumTasks):
        latest = min(LatestStep[j], TimeSteps-1)
        earliest = max(EarliestStep[j], 0)
        if earliest > latest:  # Handle invalid time windows
            earliest = latest
        adj_earliest.append(earliest)
        adj_latest.append(latest)

    # Create optimization model
    model = Model("ST_MR_TA")
    x = {}  # Decision variables x[i,t,j]

    # Create variables with distance as coefficient
    for j in range(NumTasks):
        for i in range(NumRobots):
            for t in range(adj_earliest[j], adj_latest[j]+1):
                x[i,t,j] = model.addVar(
                    vtype=GRB.BINARY,
                    name=f"x_{i}_{t}_{j}",
                    obj=dist_matrix[i][j]  # Distance directly added to objective
                )

    # Constraints
    # 1. Each task must be assigned to the required number of robots at valid time steps
    for j in range(NumTasks):
        model.addConstr(
            quicksum(x[i,t,j] for i in range(NumRobots) 
                    for t in range(adj_earliest[j], adj_latest[j]+1)) == TaskRequirements[j],
            f"Task_{j}_assignment"
        )

    # 2. Each robot handles at most one task per time step
    for i in range(NumRobots):
        for t in range(TimeSteps):
            valid_tasks = [j for j in range(NumTasks) 
                          if adj_earliest[j] <= t <= adj_latest[j]]
            model.addConstr(
                quicksum(x[i,t,j] for j in valid_tasks) <= 1,
                f"Robot_{i}_Time_{t}_Capacity"
            )

    # Solve and process results
    model.setParam('OutputFlag', 0)
    model.optimize()

    assignments = {}
    if model.status == GRB.OPTIMAL:
        # Parse assignment results
        for var in model.getVars():
            if var.X > 0.5:
                _, robot_str, time_str, task_str = var.VarName.split('_')
                assignments[int(task_str)] = (int(robot_str), int(time_str))
        total_distance = model.objVal
        return total_distance
    else:
        return float('inf'), {}
