import matplotlib.pyplot as plt
import numpy as np

def plot_grid_partition(n, P, partition_type="stripe", save_as=None):
    """
    Plot a grid with stripe-wise or block-wise partitioning, including process numbers
    and uniform triangulation of grid points.
    
    Parameters:
        n (int): Number of grid points per dimension (n x n grid).
        P (int): Number of processes.
        partition_type (str): "stripe" or "block".
        save_as (str): File path to save the figure (optional).
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    x, y = np.meshgrid(range(n + 1), range(n + 1))
    
    # Draw grid lines
    ax.plot(x, y, color='lightgray', linestyle='--', linewidth=0.5)
    ax.plot(x.T, y.T, color='lightgray', linestyle='--', linewidth=0.5)

    if partition_type == "stripe":
        # Stripe-wise partitioning (horizontal stripes)
        rows_per_process = n // P
        for p in range(P):
            start_row = p * rows_per_process
            end_row = (p + 1) * rows_per_process if p != P - 1 else n
            rect = plt.Rectangle(
                (0, start_row),
                n,
                end_row - start_row,
                linewidth=2,
                edgecolor="black",
                facecolor="none"
            )
            ax.add_patch(rect)
            # Add process number
            ax.text(
                n / 2, (start_row + end_row) / 2, str(p + 1),
                ha='center', va='center', fontsize=20, fontweight='bold'
            )
    
    elif partition_type == "block":
        # Block-wise partitioning
        blocks_per_side = int(np.sqrt(P))
        block_size = n // blocks_per_side
        for i in range(blocks_per_side):
            for j in range(blocks_per_side):
                start_x = j * block_size
                start_y = i * block_size
                rect = plt.Rectangle(
                    (start_x, start_y),
                    block_size,
                    block_size,
                    linewidth=2,
                    edgecolor="black",
                    facecolor="none"
                )
                ax.add_patch(rect)
                # Add process number
                ax.text(
                    start_x + block_size / 2, start_y + block_size / 2,
                    str(i * blocks_per_side + j + 1),
                    ha='center', va='center', fontsize=20, fontweight='bold'
                )
    
    else:
        raise ValueError("Invalid partition_type. Use 'stripe' or 'block'.")

    # Draw triangulation
    for i in range(n):
        for j in range(n):
            # Draw triangles for each grid square
            ax.plot(
                [j, j + 1, j], [i, i, i + 1], color='blue', linewidth=0.5  # Triangle 1
            )
            ax.plot(
                [j + 1, j + 1, j], [i, i + 1, i + 1], color='blue', linewidth=0.5  # Triangle 2
            )

    # Axis settings
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_title(f"{partition_type.capitalize()} Partitioning with Triangulation ({n}x{n} Grid, {P} Processes)")
    ax.set_xlabel("X-axis (Columns)")
    ax.set_ylabel("Y-axis (Rows)")
    ax.grid(False)

    # Prevent duplicate labels in legend
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')
    
    plt.savefig(save_as, bbox_inches="tight")


import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Example usage
n = 13  # Grid size (n x n)
P = 4   # Number of processes

# Stripe-wise partition
plot_grid_partition(n, P, partition_type="stripe", save_as="../lab2/stripe_partition.png")

# Block-wise partition
plot_grid_partition(n, P, partition_type="block", save_as="../lab2/block_partition.png")
