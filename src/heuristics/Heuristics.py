def null_heuristic(node, start, goal, content, neighbors):
    return 0


def bfs_heuristic(node, start, goal, content, neighbors):
    return 1


def shortcut_bfs_heuristic(node, start, goal, content, neighbors):
    return -float("inf") if node == goal else 1


def dfs_heuristic(node, start, goal, content, neighbors):
    return -1


def shortcut_dfs_heuristic(node, start, goal, content, neighbors):
    return -float("inf") if node == goal else -1
