def prob_13(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements):
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

    model = Model("MT_MR_TA")

    # Create assignment variables
    x = {}
    for r in range(NumRobots):
        for k in range(NumTasks):
            for t in range(TimeSteps):
                if EarliestStep[k] <= t <= LatestStep[k]:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, name=f'x_{r}_{k}_{t}')
                else:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, ub=0, name=f'x_{r}_{k}_{t}')

    # Create position variables
    pos_x = {}
    pos_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps + 1):
            pos_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_x_{r}_{t}')
            pos_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_y_{r}_{t}')

    # Initial positions
    for r in range(NumRobots):
        model.addConstr(pos_x[r, 0] == RobotPositions[r][0], name=f'init_pos_x_{r}')
        model.addConstr(pos_y[r, 0] == RobotPositions[r][1], name=f'init_pos_y_{r}')

    # Position updates based on assignments
    for r in range(NumRobots):
        for t in range(TimeSteps):
            assigned = model.addVar(vtype=GRB.BINARY, name=f'assigned_{r}_{t}')
            model.addConstr(assigned == quicksum(x[r, k, t] for k in range(NumTasks)), name=f'assigned_constr_{r}_{t}')

            for k in range(NumTasks):
                model.addGenConstrIndicator(
                    x[r, k, t],
                    True,
                    pos_x[r, t+1] == TaskPositions[k][0],
                    name=f'pos_x_update_{r}_{k}_{t}'
                )
                model.addGenConstrIndicator(
                    x[r, k, t],
                    True,
                    pos_y[r, t+1] == TaskPositions[k][1],
                    name=f'pos_y_update_{r}_{k}_{t}'
                )

            model.addGenConstrIndicator(
                assigned,
                False,
                pos_x[r, t+1] == pos_x[r, t],
                name=f'pos_x_stay_{r}_{t}'
            )
            model.addGenConstrIndicator(
                assigned,
                False,
                pos_y[r, t+1] == pos_y[r, t],
                name=f'pos_y_stay_{r}_{t}'
            )

    # 引入新变量y[k,t]表示任务k在时间t执行
    y = {}
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            y[k, t] = model.addVar(vtype=GRB.BINARY, name=f'y_{k}_{t}')

    # 每个任务必须在一个时间步执行
    for k in range(NumTasks):
        model.addConstr(
            quicksum(y[k, t] for t in range(EarliestStep[k], LatestStep[k] + 1)) == 1,
            name=f'task_{k}_exact_time'
        )

    # 约束任务在选中的时间步分配正确数量的机器人
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            # 如果y[k,t]=1，则分配TaskRequirements[k]个机器人
            model.addGenConstrIndicator(
                y[k, t],
                True,
                quicksum(x[r, k, t] for r in range(NumRobots)) == TaskRequirements[k],
                name=f'task_{k}_t_{t}_req'
            )
            # 如果y[k,t]=0，则分配0个机器人
            model.addGenConstrIndicator(
                y[k, t],
                False,
                quicksum(x[r, k, t] for r in range(NumRobots)) == 0,
                name=f'task_{k}_t_{t}_no_req'
            )

    # 每个机器人每时间步最多分配到一个任务
    for r in range(NumRobots):
        for t in range(TimeSteps):
            model.addConstr(
                quicksum(x[r, k, t] for k in range(NumTasks)) <= 1,
                name=f'robot_{r}_time_{t}_max_one'
            )

    # 定义位移变量
    delta_x = {}
    delta_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps):
            delta_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_x_{r}_{t}')
            delta_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_y_{r}_{t}')
            model.addConstr(delta_x[r, t] == pos_x[r, t+1] - pos_x[r, t], name=f'delta_x_constr_{r}_{t}')
            model.addConstr(delta_y[r, t] == pos_y[r, t+1] - pos_y[r, t], name=f'delta_y_constr_{r}_{t}')

    # 计算总距离
    total_distance = 0
    for r in range(NumRobots):
        for t in range(TimeSteps):
            dist = model.addVar(name=f'dist_{r}_{t}')
            model.addGenConstrNorm(dist, [delta_x[r, t], delta_y[r, t]], 2, name=f'dist_norm_{r}_{t}')
            total_distance += dist

    model.setObjective(total_distance, GRB.MINIMIZE)
    model.Params.NonConvex = 2
    model.Params.LogToConsole = 0

    model.optimize()

    total_distance = 0
    
    return total_distance