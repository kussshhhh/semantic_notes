import matplotlib
matplotlib.use('Agg') # Use non-interactive backend for saving to file

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D # Required for projection='3d'
from typing import List
from src.core.note import Note

def plot_notes_3d(notes: List[Note], output_path: str = "notes_visualization.png") -> bool:
    """
    Generates a 3D scatter plot of notes with valid 3D coordinates and saves it to a file.

    Args:
        notes (List[Note]): A list of Note objects.
        output_path (str): The path to save the generated plot image.

    Returns:
        bool: True if the plot was successfully generated and saved, False otherwise.
    """
    if not notes:
        print("No notes provided to plot.")
        return False

    plottable_notes = [
        note for note in notes
        if note.coordinates is not None and isinstance(note.coordinates, list) and len(note.coordinates) == 3
    ]

    if not plottable_notes:
        print("No notes with valid 3D coordinates to plot.")
        # Check if there are notes at all, and if any have coordinates but not 3D
        has_any_coords = any(note.coordinates is not None for note in notes)
        if has_any_coords:
            print("Some notes have coordinates, but they are not valid 3D lists (e.g., None, wrong length, or not a list).")
        return False

    try:
        x_coords = [note.coordinates[0] for note in plottable_notes]
        y_coords = [note.coordinates[1] for note in plottable_notes]
        z_coords = [note.coordinates[2] for note in plottable_notes]

        fig = plt.figure(figsize=(10, 8)) # Adjust figure size for better readability
        ax = fig.add_subplot(111, projection='3d')

        scatter = ax.scatter(x_coords, y_coords, z_coords, c=z_coords, cmap='viridis', marker='o', s=50) # s for size

        # Add a color bar
        fig.colorbar(scatter, ax=ax, label='Z Coordinate Value (Color Coded)')

        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_zlabel('Z Coordinate')
        ax.set_title('3D Note Landscape')

        # Optionally, add labels to points (can be crowded if many points)
        # for i, note in enumerate(plottable_notes):
        #     ax.text(note.coordinates[0], note.coordinates[1], note.coordinates[2],
        #             f"ID: {note.id[:4]}", size=7, zorder=1, color='k')

        plt.savefig(output_path, dpi=150) # Save with higher DPI
        plt.close(fig)  # Close the figure to free memory

        print(f"Plot saved to {output_path}")
        return True
    except Exception as e:
        print(f"Error during 3D plot generation: {e}")
        # Attempt to close figure if it exists, in case of error after fig creation
        if 'fig' in locals() and plt.fignum_exists(fig.number):
             plt.close(fig)
        return False

if __name__ == '__main__':
    # Example Usage (for testing this module directly)
    print("Running example for plot_notes_3d...")

    # Create some dummy Note objects for testing
    class DummyNote(Note): # Inherit to use existing structure, override for simplicity
        def __init__(self, id_val, content, coordinates=None):
            super().__init__(content) # Call parent init for timestamp, etc.
            self.id = id_val # Override generated UUID for predictability
            self.coordinates = coordinates

    test_notes = [
        DummyNote("note1", "Content 1", [1.0, 2.0, 3.0]),
        DummyNote("note2", "Content 2", [4.0, 5.0, 6.0]),
        DummyNote("note3", "Content 3", [2.5, 3.5, 4.5]),
        DummyNote("note4", "Content 4", None), # No coordinates
        DummyNote("note5", "Content 5", [1.5, 2.5]), # Invalid 2D coordinates
        DummyNote("note6", "Content 6", [7.0, 8.0, 9.0]),
    ]

    # Test 1: Plotting valid notes
    print("\nTest 1: Plotting valid notes...")
    success = plot_notes_3d(test_notes, "test_plot_valid.png")
    print(f"Plotting successful: {success}")

    # Test 2: No valid notes
    print("\nTest 2: No valid notes...")
    success_invalid = plot_notes_3d([test_notes[3], test_notes[4]], "test_plot_invalid.png")
    print(f"Plotting successful (should be False): {not success_invalid}")

    # Test 3: Empty list of notes
    print("\nTest 3: Empty list of notes...")
    success_empty = plot_notes_3d([], "test_plot_empty.png")
    print(f"Plotting successful (should be False): {not success_empty}")

    print("\nExample run finished. Check for 'test_plot_valid.png' if successful.")
