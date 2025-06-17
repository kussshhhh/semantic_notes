import json
import os
from src.core.note import Note
from src.processing.semantic_analyzer import SemanticAnalyzer
from src.processing.position_calculator import PositionCalculator

class DataManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default path: project_root/notes_db.json
            # Assuming this file (data_manager.py) is in src/core/
            self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'notes_db.json')
        else:
            self.db_path = db_path

        # Ensure the directory for the db_path exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize processing tools
        try:
            self.semantic_analyzer = SemanticAnalyzer()
        except Exception as e:
            print(f"Warning: Failed to initialize SemanticAnalyzer: {e}. Some functionalities might be limited.")
            self.semantic_analyzer = None

        try:
            self.position_calculator = PositionCalculator()
        except Exception as e:
            print(f"Warning: Failed to initialize PositionCalculator: {e}. Some functionalities might be limited.")
            self.position_calculator = None

        self.notes: list[Note] = []
        self._load_db()

    def _save_db(self):
        """Saves all notes to a single JSON file."""
        try:
            # Create a list of dictionaries from the note objects
            notes_data = [note.to_dict() for note in self.notes]
            with open(self.db_path, "w") as f:
                json.dump(notes_data, f, indent=4)
        except IOError as e:
            print(f"Error saving notes to {self.db_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving notes: {e}")

    def _load_db(self):
        """Loads all notes from a single JSON file into self.notes."""
        self.notes.clear()
        if not os.path.exists(self.db_path):
            print(f"Database file {self.db_path} not found. Initializing with empty notes list.")
            return

        try:
            with open(self.db_path, "r") as f:
                notes_data = json.load(f)
                if not isinstance(notes_data, list):
                    print(f"Error: Expected a list from {self.db_path}, got {type(notes_data)}. Initializing empty.")
                    self.notes = []
                    return
                for note_dict in notes_data:
                    # Ensure note_dict is a dictionary
                    if isinstance(note_dict, dict):
                        self.notes.append(Note.from_dict(note_dict))
                    else:
                        print(f"Warning: Skipping non-dictionary item in notes data: {note_dict}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {self.db_path}: {e}. Initializing with empty notes list.")
            self.notes = [] # Initialize empty if file is corrupt
        except Exception as e:
            print(f"An unexpected error occurred while loading notes from {self.db_path}: {e}")
            self.notes = []

    def add_note(self, new_note: Note) -> Note | None:
        """
        Adds a pre-created note (with content and embedding) to the list,
        updates positions for all notes, and saves all notes.
        """
        if not isinstance(new_note, Note):
            print("Error: Attempted to add an invalid object type. Expected Note.")
            return None

        if self.position_calculator is None:
            print("Error: DataManager is not fully initialized (missing PositionCalculator). Cannot process note positions.")
            # Add note without position calculation and save
            self.notes.append(new_note)
            self._save_db()
            print(f"Warning: Note {new_note.id} added without position calculation due to initialization errors.")
            return new_note

        # Add the new note to the internal list
        # Ensure no duplicate IDs if that's a concern (current Note class generates unique IDs)
        # For simplicity, we assume IDs are unique or handled by Note class creation
        self.notes.append(new_note)

        # Recalculate positions for all notes
        print("Recalculating positions for all notes...")
        all_embeddings = []
        notes_with_embeddings_indices = []

        for i, note in enumerate(self.notes):
            if hasattr(note, 'embedding') and note.embedding is not None:
                all_embeddings.append(note.embedding)
                notes_with_embeddings_indices.append(i)
            else:
                if hasattr(note, 'position') and note.position is not None:
                    note.position = None # Clear position if no embedding

        if not all_embeddings:
            print("No valid embeddings found to calculate positions.")
            # If the new_note was the first one and has an embedding, its position might be [0,0,0] or similar
            # This case is handled by the API layer setting a default position if all_embeddings is empty.
            # For now, if new_note has an embedding but is the only one, it won't get a position from calculator.
            # The API layer's logic for this will be important.
        else:
            positions = self.position_calculator.calculate_positions(all_embeddings)
            if positions is not None and len(positions) == len(all_embeddings):
                print(f"Positions calculated for {len(positions)} notes.")
                for i, original_note_idx in enumerate(notes_with_embeddings_indices):
                    self.notes[original_note_idx].position = positions[i]
            else:
                print("Warning: Could not calculate positions or mismatch in position count.")

        self._save_db() # Save all notes (including new one and those with updated positions)
        print(f"Note {new_note.id} processed and all notes saved.")
        return new_note

    def get_all_notes(self) -> list[Note]:
        """Returns the current list of notes."""
        # Consider returning a copy if direct modification of the list is a concern:
        # return list(self.notes)
        return self.notes

    def get_note_by_id(self, note_id: str) -> Note | None:
        """Retrieves a note from the internal list by its ID."""
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def save_notes(self):
        """Explicitly saves the current state of all notes to the database file."""
        print("DataManager: Explicitly saving all notes...")
        self._save_db()


    def refresh_all_positions(self) -> bool:
        """
        Recalculates positions for all notes that have embeddings.
        Saves notes if positions have changed.
        """
        if self.position_calculator is None:
            print("Error: PositionCalculator not initialized. Cannot refresh positions.")
            return False

        print("Refreshing all note positions...")
        all_embeddings = []
        notes_with_embeddings_indices = []

        for i, note in enumerate(self.notes):
            if hasattr(note, 'embedding') and note.embedding is not None:
                all_embeddings.append(note.embedding)
                notes_with_embeddings_indices.append(i)

        if not all_embeddings:
            print("No valid embeddings found to calculate positions.")
            return False

        positions = self.position_calculator.calculate_positions(all_embeddings)
        updated_count = 0
        if positions is not None and len(positions) == len(all_embeddings):
            print(f"New positions calculated for {len(positions)} notes.")
            needs_save = False
            for i, original_note_idx in enumerate(notes_with_embeddings_indices):
                if self.notes[original_note_idx].position != positions[i]:
                    self.notes[original_note_idx].position = positions[i]
                    updated_count += 1
                    needs_save = True

            if needs_save:
                self._save_db()
                print(f"{updated_count} notes had their positions updated and saved.")
            else:
                print("No positions needed updating.")
            return True
        else:
            print("Warning: Could not calculate positions or mismatch in position count during refresh.")
            return False

    def regenerate_all_embeddings(self, force_recalculation: bool = False) -> bool:
        """
        Regenerates embeddings for all notes.
        If force_recalculation is True, it will also trigger a position update.
        Saves notes whose embeddings have changed.
        """
        if self.semantic_analyzer is None:
            print("Error: SemanticAnalyzer not initialized. Cannot regenerate embeddings.")
            return False

        print("Regenerating all embeddings...")
        updated_count = 0
        embeddings_changed = False
        for note in self.notes:
            old_embedding = note.embedding
            # Assuming generate_embedding exists in SemanticAnalyzer and takes text
            new_embedding = self.semantic_analyzer.generate_embedding(note.content)
            if new_embedding is not None:
                if new_embedding != old_embedding:
                    note.embedding = new_embedding
                    updated_count += 1
                    embeddings_changed = True
            else:
                print(f"Warning: Failed to generate new embedding for note {note.id}")

        if embeddings_changed:
            self._save_db() # Save all notes if any embedding changed
            print(f"{updated_count} notes had their embeddings updated and saved.")

        if embeddings_changed or force_recalculation:
            print("Embeddings changed or recalculation forced, now refreshing all positions.")
            self.refresh_all_positions()

        return True

```
