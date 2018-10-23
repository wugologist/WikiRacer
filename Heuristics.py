def null_heuristic(node, start, goal, content, neighbors):
    return 0


def bfs_heuristic(node, start, goal, content, neighbors):
    return 1


def shortcut_null_heuristic(node, start, goal, content, neighbors):
    return 0 if node == goal else 1
