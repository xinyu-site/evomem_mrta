def prob_13(RobotPositions, TaskPositions, TaskRequirements, NumRobots, NumTasks):
    """ 
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        TaskRequirements: a list, the number of robots required per task
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
    Returns:
        assignment: a list of lists, each task assigned robots (robot index starts from 0)
    """
    import numpy as np
    from gurobipy import Model, GRB, quicksum

    def euclidean_distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # Create the Gurobi model
    model = Model("robot_task_assignment")

    # Decision variables: x_{ij} = 1 if robot i is assigned to task j, 0 otherwise
    x = {}
    for i in range(NumRobots):
        for j in range(NumTasks):
            x[i, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}")

    # Objective: minimize the total Euclidean distance
    model.setObjective(
        quicksum(
            euclidean_distance(RobotPositions[i], TaskPositions[j]) * x[i, j]
            for i in range(NumRobots)
            for j in range(NumTasks)
        ),
        GRB.MINIMIZE
    )

    # Constraints:
    # 1. Each task must be assigned the required number of robots
    for j in range(NumTasks):
        model.addConstr(quicksum(x[i, j] for i in range(NumRobots)) == TaskRequirements[j])

    # Optimize the model
    model.optimize()

    # Initialize a list to track the assignment of tasks to robots
    assignment = [[] for _ in range(NumTasks)]

    # Extract the assignment from the solution
    if model.status == GRB.OPTIMAL:
        for i in range(NumRobots):
            for j in range(NumTasks):
                if x[i, j].X > 0.5:  # If the variable is 1 (or close to 1)
                    assignment[j].append(i)
    else:
        raise Exception("No optimal solution found.")

    return assignment
