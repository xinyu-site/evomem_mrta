def prob_20(RobotPositions, TaskPositions, NumRobots, NumTasks):
    """ 
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
    Returns:
        total_distance: a float, the minimized sum of Euclidean distances between assigned robots and tasks
    """
    import gurobipy as gp
    from gurobipy import GRB
    import math
    # Input validation
    if not RobotPositions or not TaskPositions:
        raise ValueError("RobotPositions and TaskPositions must not be empty.")
    if len(RobotPositions) != NumRobots or len(TaskPositions) != NumTasks:
        raise ValueError("Mismatch between positions list lengths and NumRobots/NumTasks.")

    # Create model
    model = gp.Model("RobotTaskAssignment")
    
    try:
        # Create binary decision variables
        x = model.addVars(NumRobots, NumTasks, vtype=GRB.BINARY, name="assign")
        
        # Calculate Euclidean distances using hypot
        distances = {}
        for i in range(NumRobots):
            for j in range(NumTasks):
                dx = RobotPositions[i][0] - TaskPositions[j][0]
                dy = RobotPositions[i][1] - TaskPositions[j][1]
                distances[i, j] = math.hypot(dx, dy)
        
        # Set objective: minimize total distance
        model.setObjective(
            gp.quicksum(x[i, j] * distances[i, j] 
                       for i in range(NumRobots) 
                       for j in range(NumTasks)), 
            GRB.MINIMIZE
        )
        
        # Add constraints (handles unbalanced cases)
        if NumRobots > NumTasks:
            model.addConstrs((x.sum('*', j) <= 1 for j in range(NumTasks)), name="task_assignment")
            model.addConstrs((x.sum(i, '*') == 1 for i in range(NumRobots)), name="robot_assignment")
        elif NumRobots < NumTasks:
            model.addConstrs((x.sum(i, '*') <= 1 for i in range(NumRobots)), name="robot_assignment")
            model.addConstrs((x.sum('*', j) == 1 for j in range(NumTasks)), name="task_assignment")
        else:
            model.addConstrs((x.sum(i, '*') == 1 for i in range(NumRobots)), name="robot_assignment")
            model.addConstrs((x.sum('*', j) == 1 for j in range(NumTasks)), name="task_assignment")
        
        # Optimize model
        model.optimize()
        
        # Check solution status
        if model.status == GRB.OPTIMAL:
            total_distance = model.ObjVal
        else:
            raise RuntimeError(f"Model failed to solve. Status: {model.status}")
        
        return total_distance
    
    finally:
        model.dispose()