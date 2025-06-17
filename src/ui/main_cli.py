import sys
from src.core.data_manager import DataManager
from src.core.note import Note # Still useful for type hinting or direct use if needed
from src.visualization.renderer import plot_notes_3d # Added import

def list_all_notes(data_manager: DataManager):
    """Lists all notes with their details."""
    notes = data_manager.get_all_notes()
    if not notes:
        print("No notes found.")
        return
    print("\n--- All Notes ---")
    for i, note in enumerate(notes):
        print(f"Note {i+1}:")
        print(f"  ID: {note.id}")
        print(f"  Timestamp: {note.timestamp}")
        print(f"  Content: {note.content[:100]}{'...' if len(note.content) > 100 else ''}")

        vec_preview = "N/A"
        if note.semantic_vector:
            vec_preview = f"[{', '.join(map(lambda x: f'{x:.4f}', note.semantic_vector[:3]))} ...]"
        print(f"  Semantic Vector (first 3 dims): {vec_preview}")

        coords_preview = "N/A"
        if note.coordinates:
            coords_preview = f"[{', '.join(map(lambda x: f'{x:.4f}', note.coordinates))}]"
        print(f"  Coordinates: {coords_preview}")
        print("-" * 20)

def create_new_note_cli(data_manager: DataManager):
    """Prompts user for note content, then uses DataManager to add it."""
    print("\n--- Create New Note ---")
    try:
        content = input("Enter your note content (or type 'exitnotes' to cancel): ")
        if content.lower() == 'exitnotes':
            print("Note creation cancelled.")
            return
        if not content.strip():
            print("Note content cannot be empty.")
            return
    except EOFError: # Happens if input is piped and ends
        print("\nNo input received for note content. Skipping creation.")
        return

    new_note = data_manager.add_new_note(content)
    if new_note:
        print(f"Note saved successfully!")
        print(f"  ID: {new_note.id}")
        print(f"  Content: {new_note.content[:100]}{'...' if len(new_note.content) > 100 else ''}")
        if new_note.semantic_vector:
            print(f"  Semantic vector generated (length {len(new_note.semantic_vector)}).")
        else:
            print("  Semantic vector NOT generated (check logs for errors).")
        if new_note.coordinates:
            print(f"  Coordinates calculated: {new_note.coordinates}")
        else:
            print("  Coordinates NOT calculated (possibly no vector or not enough notes).")
    else:
        print("Failed to save the note. Check logs for details.")

def main_cli():
    """Main CLI loop for interacting with the note system."""
    print("Initializing DataManager...")
    # Check if SemanticAnalyzer or PositionCalculator failed to initialize
    # by checking if they are None after DataManager instantiation.
    # The DataManager constructor already prints critical errors.
    data_manager = DataManager()
    if data_manager.semantic_analyzer is None:
        print("WARNING: SemanticAnalyzer could not be initialized. Embedding generation will be skipped.")
    if data_manager.position_calculator is None:
        print("WARNING: PositionCalculator could not be initialized. Position calculation will be skipped.")

    while True:
        print("\nWhat would you like to do?")
        print("1. Create a new note")
        print("2. List all notes")
        print("3. Regenerate all embeddings and update positions")
        print("4. Refresh all positions (using existing embeddings)")
        print("5. Plot 3D Notes (saves to 'notes_visualization.png')")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            create_new_note_cli(data_manager)
        elif choice == '2':
            list_all_notes(data_manager)
        elif choice == '3':
            print("Regenerating all embeddings and updating positions...")
            if data_manager.regenerate_all_embeddings(force_recalculation=True):
                print("Embeddings and positions updated.")
            else:
                print("Failed to regenerate embeddings. Check logs.")
        elif choice == '4':
            print("Refreshing all positions...")
            if data_manager.refresh_all_positions():
                print("Positions updated.")
            else:
                print("Failed to refresh positions. Check logs.")
        elif choice == '5':
            print("Generating 3D plot of notes...")
            all_notes = data_manager.get_all_notes()
            if not all_notes:
                print("No notes available to plot.")
            else:
                try:
                    if plot_notes_3d(all_notes):
                        print("Plot generation request completed.") # Message from plot_notes_3d is more specific
                    else:
                        print("Plot generation failed or no plottable notes. Check console for details.")
                except ImportError:
                    print("Matplotlib might not be installed. Plotting is unavailable.")
                except Exception as e:
                    print(f"An unexpected error occurred during plotting: {e}")
        elif choice == '6':
            print("Exiting Note Manager CLI.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    # Check if running in a non-interactive environment (e.g. during tests or automated execution)
    # `isatty()` checks if the standard input is connected to a terminal.
    # This helps prevent `input()` from causing errors if there's no TTY.
    if not sys.stdin.isatty():
        print("Non-interactive mode detected. CLI will not run main_cli loop.")
        # Optionally, run a specific function here for testing if needed, e.g.:
        # dm = DataManager()
        # list_all_notes(dm)
    else:
        main_cli()
