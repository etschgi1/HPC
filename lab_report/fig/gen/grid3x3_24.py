import matplotlib.pyplot as plt
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def plot_uniform_grid_partition_3x3(n=5):
    """
    Plots a uniform grid with 3x3 rectangular partitions.
    
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

    # Add 3x3 partitions
    orig_x = 0.2
    orig_y = 0
    n *= 0.87
    partition_size = n / 3
    for i in range(3):
        for j in range(3):
            rect = plt.Rectangle(
                (orig_x + j * partition_size, orig_y + i * partition_size),
                partition_size,
                partition_size,
                linewidth=2,
                edgecolor='r',
                facecolor='none'
            )
            ax.add_patch(rect)

    # Highlight specific points and markers
    ax.plot(2, 4 * h, 'bo', markersize=10)
    ax.plot(1.5, 3 * h, 'bo', markersize=10)
    ax.plot(0.5, 3 * h, 'bo', markersize=10)

    ax.plot(4, 2 * h, 'ro', markersize=10)
    ax.plot(3, 2 * h, 'ro', markersize=10)
    ax.plot(2.5, 1 * h, 'ro', markersize=10)

    ax.plot(1.5, 3 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(2, 4 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(3, 4 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(3.5, 3 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(1.5, 1 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(2.5, 1 * h, 'orange', marker="$\\circ$", markersize=20)
    ax.plot(3.5, 1 * h, 'orange', marker="$\\circ$", markersize=20)

    # Add numbers to the partitions
    ax.plot(1, 4.5 * h, 'blue', marker="$0$", markersize=20)
    ax.plot(2.5, 4.5 * h, 'black', marker="$1$", markersize=20)
    ax.plot(4, 4.5 * h, 'black', marker="$2$", markersize=20)
    ax.plot(1, 2.6* h, 'black', marker="$3$", markersize=20)
    ax.plot(2.5, 2.6* h, 'orange', marker="$4$", markersize=20)
    ax.plot(4, 2.6* h, 'black', marker="$5$", markersize=20)
    ax.plot(1, 0.6* h, 'black', marker="$6$", markersize=20)
    ax.plot(2.5, 0.6* h, 'black', marker="$7$", markersize=20)
    ax.plot(4, 0.6* h, 'red', marker="$8$", markersize=20)
    plt.tight_layout()

    # Save the figure
    plt.savefig("../lab2/grid_3x3_partition.png")
# Example usage
plot_uniform_grid_partition_3x3()

