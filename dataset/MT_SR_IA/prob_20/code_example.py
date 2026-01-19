def prob_20(RobotPositions, TaskPositions, NumRobots, NumTasks):
    """ 
    Args:
        RobotPositions: a list of lists, positions of robots in Cartesian coordinates
        TaskPositions: a list of lists, positions of tasks in Cartesian coordinates
        NumRobots: an integer, number of robots
        NumTasks: an integer, number of tasks
    Returns:
        assignment: a list of integers, each task assigned to a robot (robot index starts from 0)
    """
    import numpy as np

    def euclidean_distance(p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    # Initialize a list to track the assignment of tasks to robots
    assignment = []

    return assignment
