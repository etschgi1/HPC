import matplotlib.pyplot as plt
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def plot_uniform_grid_simple(n=5):
    """
    Plots a simple uniform grid of size n x n without text, axes, or title.
    
    Parameters:
        n (int): Number of grid points in each dimension.
    """
        # Calculate height of an equilateral triangle
    h = np.sqrt(3) / 2 * 1

    fig, ax = plt.subplots(figsize=(8, 8))

    # Generate equilateral triangle grid points
    for i in range(n + 1):
        for j in range(n + 1):
            # Calculate x, y positions
            x = j * 1 + (i % 2) * (1 / 2)
            y = i * h
            # Draw two triangles for each point
            if i < n and j < n:
                # Triangle 1
                ax.plot(
                    [x, x + 1 / 2, x - 1 / 2, x],
                    [y, y + h, y + h, y],
                    color="black",
                    linewidth=0.5,
                )
                # Triangle 2
                ax.plot(
                    [x, x + 1 / 2, x + 1, x],
                    [y, y + h, y, y],
                    color="black",
                    linewidth=0.5,
                )
            # Add point
            ax.scatter(x, y, color="black", s=10)

    # Formatting
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')  # Remove axes
    orig_x = 0.2
    orig_y = 0
    n *= 0.87
    rect0 = plt.Rectangle((orig_x, orig_y), n/2, n/2, linewidth=2, edgecolor='r', facecolor='none')
    rect1 = plt.Rectangle((orig_x+n/2, orig_y+n/2), n/2, n/2, linewidth=2, edgecolor='r', facecolor='none')
    rect2 = plt.Rectangle((orig_x, orig_y+n/2), n/2, n/2, linewidth=2, edgecolor='r', facecolor='none')
    rect3 = plt.Rectangle((orig_x+n/2, orig_y), n/2, n/2, linewidth=2, edgecolor='r', facecolor='none')
    ax.add_patch(rect0)
    ax.add_patch(rect1)
    ax.add_patch(rect2)
    ax.add_patch(rect3)
    ax.plot(2.5, 3*h, 'bo', markersize=10)
    ax.plot(1.5, 3*h, 'bo')
    ax.plot(3, 2*h, 'bo')
    ax.plot(2, 2*h, 'bo')

    ax.plot(1.5, 3*h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(2.5, 3*h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(2, 2*h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(2, 2*h, 'orange', marker="$\\circ$", markersize=15)

    ax.plot(1.5, 3.6*h, 'black', marker="$0$", markersize=20)
    ax.plot(3.5, 3.6*h, 'black', marker="$1$", markersize=20)
    ax.plot(1.5, 1.6*h, 'black', marker="$2$", markersize=20)
    ax.plot(3.5, 1.6*h, 'black', marker="$3$", markersize=20)
    plt.tight_layout()
    plt.savefig("../lab2/grid24.png")

# Example usage
plot_uniform_grid_simple()

