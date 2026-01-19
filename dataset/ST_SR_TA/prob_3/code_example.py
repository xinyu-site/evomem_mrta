def prob_3(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps):
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

    # 预处理阶段
    dist_matrix = np.zeros((NumRobots, NumTasks))
    for i in range(NumRobots):
        for j in range(NumTasks):
            dist_matrix[i][j] = euclidean_distance(RobotPositions[i], TaskPositions[j])

    adj_earliest = []
    adj_latest = []
    for j in range(NumTasks):
        latest = min(LatestStep[j], TimeSteps-1)
        earliest = max(EarliestStep[j], 0)
        if earliest > latest:
            earliest = latest
        adj_earliest.append(earliest)
        adj_latest.append(latest)

    # 建模阶段
    model = Model("ST_SR_TA")
    x = {}
    for j in range(NumTasks):
        for i in range(NumRobots):
            for t in range(adj_earliest[j], adj_latest[j]+1):
                x[i,t,j] = model.addVar(
                    vtype=GRB.BINARY,
                    name=f"x_{i}_{t}_{j}",
                    obj=dist_matrix[i][j]
                )

    # 约束条件
    for j in range(NumTasks):
        model.addConstr(
            quicksum(x[i,t,j] for i in range(NumRobots) for t in range(adj_earliest[j], adj_latest[j]+1)) == 1,
            f"Task_{j}_assign"
        )
        
    for i in range(NumRobots):
        for t in range(TimeSteps):
            valid_tasks = [j for j in range(NumTasks) if adj_earliest[j] <= t <= adj_latest[j]]
            model.addConstr(
                quicksum(x[i,t,j] for j in valid_tasks) <= 1,
                f"Robot_{i}_time_{t}"
            )

    # 求解与结果处理
    model.setParam('OutputFlag', 0)
    model.optimize()

    assignments = {}
    if model.status == GRB.OPTIMAL:
        # 解析分配方案
        for var in model.getVars():
            if var.X > 0.5:
                _, i_str, t_str, j_str = var.VarName.split('_')
                assignments[int(j_str)] = (int(i_str), int(t_str))
        total_distance = model.objVal
        return total_distance
    else:
        return float('inf'), {}
