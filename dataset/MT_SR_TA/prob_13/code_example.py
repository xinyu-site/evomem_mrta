def prob_13(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps):
    """ 
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        EarliestStep: a list, earliest time step for each task
        LatestStep: a list, latest time step for each task
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
        TimeSteps: an integer, number of time steps
    Returns:
        total_distance: a float, the minimized sum of Euclidean distances between robots and tasks over all time steps
    """
    import numpy as np
    from gurobipy import Model, GRB, quicksum

    def euclidean_distance(p1, p2):
        return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # Precompute distances
    robot_task_dist = np.zeros((NumRobots, NumTasks))
    for i in range(NumRobots):
        for j in range(NumTasks):
            robot_task_dist[i][j] = euclidean_distance(RobotPositions[i], TaskPositions[j])

    task_task_dist = np.zeros((NumTasks, NumTasks))
    for j1 in range(NumTasks):
        for j2 in range(NumTasks):
            task_task_dist[j1][j2] = euclidean_distance(TaskPositions[j1], TaskPositions[j2])

    # Adjust time windows
    adj_earliest = [max(EarliestStep[j], 0) for j in range(NumTasks)]
    adj_latest = [min(LatestStep[j], TimeSteps-1) for j in range(NumTasks)]

    model = Model("MT_SR_TA")
    x = {}  # x[i,t,j] = 1 if robot i starts task j at time t
    for i in range(NumRobots):
        for j in range(NumTasks):
            for t in range(adj_earliest[j], adj_latest[j] + 1):
                x[i,t,j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{t}_{j}")

    # Sequence variables: y[i,j1,j2] = 1 if robot i does j1 before j2
    y = {}
    for i in range(NumRobots):
        for j1 in range(NumTasks):
            for j2 in range(NumTasks):
                if j1 != j2:
                    y[i,j1,j2] = model.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j1}_{j2}")

    # New variables: s[i,j] = 1 if task j is the first task for robot i
    s = {}
    for i in range(NumRobots):
        for j in range(NumTasks):
            s[i,j] = model.addVar(vtype=GRB.BINARY, name=f"s_{i}_{j}")

    # Constraints
    # Each task assigned to exactly one robot and time
    for j in range(NumTasks):
        model.addConstr(
            quicksum(x[i,t,j] for i in range(NumRobots) 
                     for t in range(adj_earliest[j], adj_latest[j]+1)) == 1,
            f"Task_{j}_assigned"
        )

    # One task per robot per time
    for i in range(NumRobots):
        for t in range(TimeSteps):
            tasks_in_window = [j for j in range(NumTasks) 
                              if adj_earliest[j] <= t <= adj_latest[j]]
            model.addConstr(
                quicksum(x[i,t,j] for j in tasks_in_window) <= 1,
                f"Robot_{i}_time_{t}"
            )

    # Sequencing constraints
    for i in range(NumRobots):
        for j1 in range(NumTasks):
            for j2 in range(NumTasks):
                if j1 != j2:
                    for t1 in range(adj_earliest[j1], adj_latest[j1]+1):
                        for t2 in range(adj_earliest[j2], adj_latest[j2]+1):
                            if t1 < t2:
                                model.addConstr(
                                    y[i,j1,j2] >= x[i,t1,j1] + x[i,t2,j2] - 1
                                )
                    model.addConstr(
                        y[i,j1,j2] + y[i,j2,j1] <= 1
                    )

    # First task constraints
    for i in range(NumRobots):
        # Each robot can have at most one first task
        model.addConstr(quicksum(s[i,j] for j in range(NumTasks)) <= 1, f"FirstTaskLimit_{i}")

        for j in range(NumTasks):
            # s[i,j] can only be 1 if robot i performs task j
            model.addConstr(s[i,j] <= quicksum(x[i,t,j] for t in range(adj_earliest[j], adj_latest[j]+1)),
                            f"sLink_{i}_{j}")

            # s[i,j] must be 1 if task j is the first task for robot i
            for t in range(adj_earliest[j], adj_latest[j]+1):
                # Sum over all tasks j' !=j and times t' <t
                sum_prev = quicksum(
                    x[i,t_prime,j_prime] 
                    for j_prime in range(NumTasks) 
                    if j_prime != j 
                    for t_prime in range(adj_earliest[j_prime], adj_latest[j_prime]+1)
                    if t_prime < t
                )
                model.addConstr(s[i,j] >= x[i,t,j] - sum_prev, f"sTrigger_{i}_{j}_{t}")

    # Objective: total distance
    total_dist = 0

    # Add initial distances for first tasks
    for i in range(NumRobots):
        for j in range(NumTasks):
            total_dist += robot_task_dist[i][j] * s[i,j]

    # Add distances between consecutive tasks
    for i in range(NumRobots):
        for j1 in range(NumTasks):
            for j2 in range(NumTasks):
                if j1 != j2:
                    total_dist += task_task_dist[j1][j2] * y[i,j1,j2]

    model.setObjective(total_dist, GRB.MINIMIZE)
    model.optimize()

    # Process results
    if model.status == GRB.OPTIMAL:
        assignments = {}
        total_distance = 0
        first_tasks = {}
        for i in range(NumRobots):
            for j in range(NumTasks):
                if s[i,j].X > 0.5:
                    first_tasks[i] = j
                    total_distance += robot_task_dist[i][j]

        # Calculate task-to-task distances
        for i in range(NumRobots):
            for j1 in range(NumTasks):
                for j2 in range(NumTasks):
                    if j1 != j2 and y[i,j1,j2].X > 0.5:
                        total_distance += task_task_dist[j1][j2]

        # Extract assignments
        for var in model.getVars():
            if 'x_' in var.VarName and var.X > 0.5:
                _, i_str, t_str, j_str = var.VarName.split('_')
                assignments[int(j_str)] = (int(i_str), int(t_str))

        return total_distance
    else:
        return float('inf'), {}