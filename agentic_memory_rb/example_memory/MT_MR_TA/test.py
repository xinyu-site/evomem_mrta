def prob_5(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements):
    """
    Solves the robot-task assignment problem with multiple robots per task and time windows,
    minimizing total Euclidean distance traveled.

    Args:
        RobotPositions: List of [x,y] positions for each robot
        TaskPositions: List of [x,y] positions for each task
        EarliestStep: List of earliest possible assignment steps for each task
        LatestStep: List of latest possible assignment steps for each task
        NumRobots: Number of robots
        NumTasks: Number of tasks
        TimeSteps: Total number of discrete time steps
        TaskRequirements: List of required robots for each task
        
    Returns:
        float: Minimized sum of Euclidean distances traveled by all robots.
               Returns infinity if no feasible solution exists.
    """
    import math
    from gurobipy import Model, GRB, quicksum

    # Input validation
    if (len(RobotPositions) != NumRobots or any(len(pos) != 2 for pos in RobotPositions) or
        len(TaskPositions) != NumTasks or any(len(pos) != 2 for pos in TaskPositions) or
        len(EarliestStep) != NumTasks or len(LatestStep) != NumTasks or 
        len(TaskRequirements) != NumTasks or TimeSteps <= 0 or 
        any(es < 0 or es > LatestStep[j] for j, es in enumerate(EarliestStep))):
        return float('inf')

    model = Model("RobotTaskAssignment")
    model.Params.LogToConsole = 0
    model.Params.NonConvex = 2

    # Create assignment variables only for valid time windows
    x = {}
    for r in range(NumRobots):
        for k in range(NumTasks):
            for t in range(TimeSteps):
                if EarliestStep[k] <= t <= LatestStep[k]:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, name=f'x_{r}_{k}_{t}')
                else:
                    x[r, k, t] = model.addVar(vtype=GRB.BINARY, ub=0, name=f'x_{r}_{k}_{t}')

    # Position variables
    pos_x = {}
    pos_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps + 1):
            pos_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_x_{r}_{t}')
            pos_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'pos_y_{r}_{t}')

    # Set initial positions
    for r in range(NumRobots):
        model.addConstr(pos_x[r, 0] == RobotPositions[r][0], name=f'init_pos_x_{r}')
        model.addConstr(pos_y[r, 0] == RobotPositions[r][1], name=f'init_pos_y_{r}')

    # Position updates using indicator constraints
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

    # Task execution variables and constraints
    y = {}
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            y[k, t] = model.addVar(vtype=GRB.BINARY, name=f'y_{k}_{t}')

    # Each task must be executed exactly once within its window
    for k in range(NumTasks):
        model.addConstr(
            quicksum(y[k, t] for t in range(EarliestStep[k], LatestStep[k] + 1)) == 1,
            name=f'task_{k}_exact_time'
        )

    # Task requirements constraints
    for k in range(NumTasks):
        for t in range(EarliestStep[k], LatestStep[k] + 1):
            model.addGenConstrIndicator(
                y[k, t],
                True,
                quicksum(x[r, k, t] for r in range(NumRobots)) == TaskRequirements[k],
                name=f'task_{k}_t_{t}_req'
            )
            model.addGenConstrIndicator(
                y[k, t],
                False,
                quicksum(x[r, k, t] for r in range(NumRobots)) == 0,
                name=f'task_{k}_t_{t}_no_req'
            )

    # Robot capacity constraints
    for r in range(NumRobots):
        for t in range(TimeSteps):
            model.addConstr(
                quicksum(x[r, k, t] for k in range(NumTasks)) <= 1,
                name=f'robot_{r}_time_{t}_max_one'
            )

    # Distance variables and constraints
    delta_x = {}
    delta_y = {}
    for r in range(NumRobots):
        for t in range(TimeSteps):
            delta_x[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_x_{r}_{t}')
            delta_y[r, t] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f'delta_y_{r}_{t}')
            model.addConstr(delta_x[r, t] == pos_x[r, t+1] - pos_x[r, t], name=f'delta_x_constr_{r}_{t}')
            model.addConstr(delta_y[r, t] == pos_y[r, t+1] - pos_y[r, t], name=f'delta_y_constr_{r}_{t}')

    # Calculate total distance using Euclidean norm
    total_distance = 0
    for r in range(NumRobots):
        for t in range(TimeSteps):
            dist = model.addVar(name=f'dist_{r}_{t}')
            model.addGenConstrNorm(dist, [delta_x[r, t], delta_y[r, t]], 2, name=f'dist_norm_{r}_{t}')
            total_distance += dist

    model.setObjective(total_distance, GRB.MINIMIZE)
    model.optimize()

    for i in range(NumRobots):
        for j in range(NumTasks):
            for t in range(TimeSteps):
                if (x[i, j, t].X > 0.5):
                    print(f"Robot {i} assigned to Task {j} at Time {t}")
                    

    return model.objVal if model.status == GRB.OPTIMAL else float('inf')

# 机器人初始位置
RobotPositions = [
    [1.0, 1.0],
    [2.0, 2.0],
    [4.0, 1.0]
]

# 任务位置
TaskPositions = [
    [1.0, 2.0],
    [5.0, 1.0]
]

# 任务最早开始时间步
EarliestStep = [0, 1]

# 任务最晚开始时间步
LatestStep = [1, 2]

# 每个任务所需的机器人数量
TaskRequirements = [2, 1]

# 机器人数量
NumRobots = 3

# 任务数量
NumTasks = 2

# 总时间步数
TimeSteps = 3

# 输出结果（最小总距离）
output = [3.0]

# 计算最小总欧几里得距离
min_distance = prob_5(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements)
print(f"Minimum Total Euclidean Distance: {min_distance}")