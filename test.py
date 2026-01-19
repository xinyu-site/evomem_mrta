def prob_4(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements):
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

    # Create model
    model = Model("RobotTaskAssignment")
    
    # Create variables
    x = {}  # Assignment variables
    pos_x = {}  # Robot x positions
    pos_y = {}  # Robot y positions
    d = {}  # Distance variables
    
    for r in range(NumRobots):
        for s in range(TimeSteps):
            pos_x[r,s] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f"pos_x_{r}_{s}")
            pos_y[r,s] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f"pos_y_{r}_{s}")
            for t in range(NumTasks):
                x[r,t,s] = model.addVar(vtype=GRB.BINARY, name=f"x_{r}_{t}_{s}")
                d[r,t,s] = model.addVar(lb=0, ub=GRB.INFINITY, name=f"d_{r}_{t}_{s}")
    
    # Set initial positions
    for r in range(NumRobots):
        model.addConstr(pos_x[r,0] == RobotPositions[r][0], name=f"init_pos_x_{r}")
        model.addConstr(pos_y[r,0] == RobotPositions[r][1], name=f"init_pos_y_{r}")
    
    # Task assignment requirements
    for t in range(NumTasks):
        for s in range(TimeSteps):
            if s >= EarliestStep[t] and s <= LatestStep[t]:
                model.addConstr(
                    quicksum(x[r,t,s] for r in range(NumRobots)) == TaskRequirements[t],
                    name=f"task_req_{t}_{s}"
                )
            else:
                for r in range(NumRobots):
                    model.addConstr(x[r,t,s] == 0, name=f"time_window_{r}_{t}_{s}")
    
    # Robot task capacity (one task per robot per time step)
    for r in range(NumRobots):
        for s in range(TimeSteps):
            model.addConstr(
                quicksum(x[r,t,s] for t in range(NumTasks)) <= 1,
                name=f"robot_capacity_{r}_{s}"
            )
    
    # Position update constraints
    M = 1000  # Large constant for big-M formulation
    for r in range(NumRobots):
        for s in range(1, TimeSteps):
            # Calculate possible new positions
            new_x = quicksum(TaskPositions[t][0] * x[r,t,s] for t in range(NumTasks))
            new_y = quicksum(TaskPositions[t][1] * x[r,t,s] for t in range(NumTasks))
            
            # If assigned to any task, move to that task's position
            model.addConstr(pos_x[r,s] == new_x + pos_x[r,s-1] * (1 - quicksum(x[r,t,s] for t in range(NumTasks))))
            model.addConstr(pos_y[r,s] == new_y + pos_y[r,s-1] * (1 - quicksum(x[r,t,s] for t in range(NumTasks))))
    
    # Distance calculation (linearized Euclidean distance)
    for r in range(NumRobots):
        for t in range(NumTasks):
            for s in range(1, TimeSteps):
                dx = TaskPositions[t][0] - pos_x[r,s-1]
                dy = TaskPositions[t][1] - pos_y[r,s-1]
                distance = math.sqrt(dx**2 + dy**2)
                model.addConstr(d[r,t,s] >= distance * x[r,t,s] - M * (1 - x[r,t,s]))
            # Distance at time 0 is 0
            model.addConstr(d[r,t,0] == 0)
    
    # Set objective
    model.setObjective(quicksum(d[r,t,s] for r in range(NumRobots) 
                               for t in range(NumTasks) 
                               for s in range(TimeSteps)), GRB.MINIMIZE)
    
    # Solve the model
    model.optimize()
    
    # Return total distance
    total_distance = model.objVal
    return total_distance

if __name__=="__main__":
    RobotPositions = [
    [0.0, 4.0],
    [1.0, 3.0],
    [2.0, 0.0]
]

    TaskPositions = [
    [0.0, 3.0],
    [2.0, 1.0],
    [2.0, 2.0]
]

    EarliestStep = [0, 0, 1]
    LatestStep = [1, 2, 2]
    NumRobots = 3
    NumTasks = 3
    TimeSteps = 3
    TaskRequirements = [2, 1, 1]

    r=prob_4(RobotPositions, TaskPositions, EarliestStep, LatestStep, NumRobots, NumTasks, TimeSteps, TaskRequirements)
    print(r)