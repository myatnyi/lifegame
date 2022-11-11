import numpy as np


def algorithm(width, height, grid, heatAlive):
    grid_copy = np.zeros((height, width), dtype=np.ushort)
    for j, i in np.ndindex(grid.shape):
        total = sum([1 for x in [grid[(j - 1) % height][(i - 1) % width],
                                 grid[(j - 1) % height][i % width],
                                 grid[(j - 1) % height][(i + 1) % width],
                                 grid[j % height][(i - 1) % width],
                                 grid[j % height][(i + 1) % width],
                                 grid[(j + 1) % height][(i - 1) % width],
                                 grid[(j + 1) % height][i % width],
                                 grid[(j + 1) % height][(i + 1) % width]] if int(x) == heatAlive])
        if grid[j][i] == heatAlive and total in [2, 3]:
            grid_copy[j][i] = heatAlive
        elif total == 3:
            grid_copy[j][i] = heatAlive
        elif 0 < grid[j][i] <= heatAlive:
            grid_copy[j][i] = grid[j][i] - 1
    return grid_copy
