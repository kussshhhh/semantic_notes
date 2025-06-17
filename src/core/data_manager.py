import json
import os
from src.core.note import Note
from src.processing.semantic_analyzer import SemanticAnalyzer
from src.processing.position_calculator import PositionCalculator

class DataManager:
    def __init__(self, notes_dir="notes_data/"):
        self.notes_dir = notes_dir
        # Initialize processing tools
        # These might fail if dependencies are not installed or models can't be downloaded
        try:
            self.semantic_analyzer = SemanticAnalyzer()
        except Exception as e:
            print(f"Critical: Failed to initialize SemanticAnalyzer: {e}")
            self.semantic_analyzer = None # Allow DataManager to operate without it

        try:
            self.position_calculator = PositionCalculator()
        except Exception as e:
            print(f"Critical: Failed to initialize PositionCalculator: {e}")
            self.position_calculator = None # Allow DataManager to operate without it

        self.notes: list[Note] = []
        os.makedirs(self.notes_dir, exist_ok=True)
        self._load_all_notes_from_disk()

    def _save_note_to_disk(self, note: Note):
        """Saves a single Note object to a JSON file in the notes_dir."""
        if not isinstance(note, Note):
            print("Error: Attempted to save an invalid object type. Expected Note.")
            return
        filepath = os.path.join(self.notes_dir, f"{note.id}.json")
        try:
            with open(filepath, "w") as f:
                json.dump(note.to_dict(), f, indent=4)
        except IOError as e:
            print(f"Error saving note {note.id} to disk: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving note {note.id}: {e}")

    def _load_note_from_disk(self, note_id: str) -> Note | None:
        """Loads a single Note object from a JSON file by its ID."""
        filepath = os.path.join(self.notes_dir, f"{note_id}.json")
        if not os.path.exists(filepath):
            # print(f"Note file {note_id}.json not found.")
            return None
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            return Note.from_dict(data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {filepath}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading note {note_id}: {e}")
            return None

    def _load_all_notes_from_disk(self):
        """Loads all notes from JSON files in the notes_dir into self.notes."""
        self.notes.clear()
        if not os.path.exists(self.notes_dir):
            print(f"Notes directory {self.notes_dir} not found.")
            return

        for filename in os.listdir(self.notes_dir):
            if filename.endswith(".json"):
                note_id = filename[:-5] # Remove .json extension
                note = self._load_note_from_disk(note_id)
                if note:
                    self.notes.append(note)
        # print(f"Loaded {len(self.notes)} notes from disk.")

    def add_new_note(self, content: str) -> Note | None:
        """
        Creates a new note, generates its semantic vector, updates positions for all notes,
        saves the new note and updates other notes with new positions to disk.
        """
        if self.semantic_analyzer is None or self.position_calculator is None:
            print("Error: DataManager is not fully initialized (missing SemanticAnalyzer or PositionCalculator). Cannot add new note.")
            # Optionally, allow adding note without semantic processing
            # new_note_basic = Note(content=content)
            # self.notes.append(new_note_basic)
            # self._save_note_to_disk(new_note_basic)
            # print("Warning: Note added without semantic vector or position due to initialization errors.")
            # return new_note_basic
            return None

        new_note = Note(content=content)

        # 1. Generate semantic vector for the new note
        print(f"Generating semantic vector for new note {new_note.id}...")
        vector = self.semantic_analyzer.generate_embedding(new_note.content)
        if vector is not None:
            new_note.semantic_vector = vector
            print(f"Semantic vector generated for {new_note.id}.")
        else:
            print(f"Warning: Could not generate semantic vector for note {new_note.id}. Note will be added without it.")

        self.notes.append(new_note) # Add to internal list

        # 2. Trigger position recalculation for all notes
        print("Recalculating positions for all notes...")
        all_valid_vectors = []
        notes_with_vectors_indices = [] # Keep track of original indices of notes that have vectors

        for i, note in enumerate(self.notes):
            if note.semantic_vector is not None:
                all_valid_vectors.append(note.semantic_vector)
                notes_with_vectors_indices.append(i)
            else:
                # Ensure notes without vectors have their coordinates as None
                if note.coordinates is not None:
                    note.coordinates = None
                    # If coordinates were previously set and now vector is gone, this note needs re-saving
                    # self._save_note_to_disk(note) # This will be handled by the loop below

        updated_notes_ids = set() # To track which notes get new positions

        if not all_valid_vectors:
            print("No valid semantic vectors found to calculate positions.")
        else:
            positions = self.position_calculator.calculate_positions(all_valid_vectors)
            if positions is not None and len(positions) == len(all_valid_vectors):
                print(f"Positions calculated for {len(positions)} notes.")
                for i, pos_index in enumerate(notes_with_vectors_indices):
                    original_note_index = pos_index
                    # Check if the position actually changed to avoid unnecessary saves
                    if self.notes[original_note_index].coordinates != positions[i]:
                        self.notes[original_note_index].coordinates = positions[i]
                        updated_notes_ids.add(self.notes[original_note_index].id)
                        # print(f"Updated position for note {self.notes[original_note_index].id}")
            else:
                print("Warning: Could not calculate positions or mismatch in position count.")

        # 3. Save the new note to disk (it's already in self.notes)
        print(f"Saving new note {new_note.id} to disk...")
        self._save_note_to_disk(new_note)

        # 4. Re-save all other notes that had their positions updated or cleared
        print("Re-saving notes with updated positions...")
        for i, note in enumerate(self.notes):
            # Save if it's the new note (already done but good to be explicit if logic changes)
            # or if its ID is in updated_notes_ids
            # or if its vector is None and its coordinates were just cleared
            if note.id == new_note.id:
                continue # Already saved new_note explicitly

            needs_resave = False
            if note.id in updated_notes_ids:
                needs_resave = True

            # If a note lost its vector, its coordinates should be None.
            # If they were just set to None, it needs resaving.
            if note.semantic_vector is None and note.coordinates is not None: # Should have been cleared above
                note.coordinates = None
                needs_resave = True # Implicitly, its old coordinates are now invalid

            if needs_resave:
                print(f"Re-saving note {note.id} due to position update or clearing.")
                self._save_note_to_disk(note)

        print(f"Note {new_note.id} added and positions updated.")
        return new_note

    def get_all_notes(self) -> list[Note]:
        """Returns a copy of the current list of notes."""
        return list(self.notes)

    def get_note_by_id(self, note_id: str) -> Note | None:
        """Retrieves a note from the internal list by its ID."""
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def refresh_all_positions(self) -> bool:
        """
        Recalculates positions for all notes that have semantic vectors.
        Saves notes whose positions have changed.
        """
        if self.position_calculator is None:
            print("Error: PositionCalculator not initialized. Cannot refresh positions.")
            return False

        print("Refreshing all note positions...")
        all_valid_vectors = []
        notes_with_vectors_indices = []

        for i, note in enumerate(self.notes):
            if note.semantic_vector is not None:
                all_valid_vectors.append(note.semantic_vector)
                notes_with_vectors_indices.append(i)

        if not all_valid_vectors:
            print("No valid semantic vectors found to calculate positions.")
            return False

        positions = self.position_calculator.calculate_positions(all_valid_vectors)
        updated_count = 0
        if positions is not None and len(positions) == len(all_valid_vectors):
            print(f"New positions calculated for {len(positions)} notes.")
            for i, pos_index in enumerate(notes_with_vectors_indices):
                original_note_index = pos_index
                if self.notes[original_note_index].coordinates != positions[i]:
                    self.notes[original_note_index].coordinates = positions[i]
                    self._save_note_to_disk(self.notes[original_note_index])
                    updated_count +=1
            print(f"{updated_count} notes had their positions updated and saved.")
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
        vectors_changed = False
        for note in self.notes:
            old_vector = note.semantic_vector
            new_vector = self.semantic_analyzer.generate_embedding(note.content)
            if new_vector is not None:
                if new_vector != old_vector:
                    note.semantic_vector = new_vector
                    self._save_note_to_disk(note) # Save note if embedding changed
                    updated_count += 1
                    vectors_changed = True
            else:
                print(f"Warning: Failed to generate new embedding for note {note.id}")

        print(f"{updated_count} notes had their embeddings updated and saved.")

        if vectors_changed or force_recalculation:
            print("Embeddings changed or recalculation forced, now refreshing all positions.")
            self.refresh_all_positions()

        return True

```
