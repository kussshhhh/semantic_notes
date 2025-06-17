from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add src directory to Python path to allow sibling imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Attempt to import core modules - this assumes they are compatible
try:
    from core.data_manager import DataManager
    from core.note import Note
    from processing.semantic_analyzer import SemanticAnalyzer
    from processing.position_calculator import PositionCalculator
    print("Successfully imported core modules.")
except ImportError as e:
    print(f"Error importing core modules: {e}")
    # Define dummy classes if imports fail, so app can still run for basic checks
    class DataManager:
        def __init__(self, db_path='notes.json'): self.db_path = db_path; print("Dummy DataManager initialized.")
        def add_note(self, note): print(f"Dummy add_note called with: {note.content if hasattr(note, 'content') else note}")
        def get_all_notes(self): print("Dummy get_all_notes called."); return []
        def save_notes(self): print("Dummy save_notes called.")

    class Note:
        def __init__(self, content, position=None, embedding=None): self.content = content; self.position = position or [0,0,0]; self.embedding = embedding; print(f"Dummy Note created with content: {content}")

    class SemanticAnalyzer:
        def __init__(self, model_name='all-MiniLM-L6-v2'): self.model_name = model_name; print("Dummy SemanticAnalyzer initialized.")
        def get_embedding(self, text): print(f"Dummy get_embedding for: {text}"); return [0.1] * 384 # Ensure correct dimensionality

    class PositionCalculator:
        def __init__(self, n_dimensions=3): self.n_dimensions = n_dimensions; print("Dummy PositionCalculator initialized.")
        def calculate_positions(self, embeddings): print(f"Dummy calculate_positions for embeddings count: {len(embeddings)}"); return [[i*0.1, i*0.2, i*0.3] for i in range(len(embeddings))]


app = Flask(__name__)
CORS(app) # Enable CORS for all routes, allowing requests from the frontend

# Initialize components (using real or dummy classes)
# Adjust db_path as necessary, perhaps make it configurable
notes_db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'notes_db.json') # Store DB in project root
data_manager = DataManager(db_path=notes_db_path)
semantic_analyzer = SemanticAnalyzer()
position_calculator = PositionCalculator(n_dimensions=3)

@app.route('/')
def home():
    return "Backend API for NoteSphere is running!"

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content in request'}), 400

    content = data['content']

    # 1. Get embedding
    embedding = semantic_analyzer.get_embedding(content)

    # 2. Create Note object (without position initially)
    # Assuming Note class can be instantiated like this and handles its own ID generation or DataManager does.
    new_note = Note(content=content, embedding=embedding)

    # 3. Add note to DataManager (which might save it and assign an ID)
    data_manager.add_note(new_note) # Let's assume add_note also handles embedding storage with the note.

    # 4. Recalculate positions for all notes (or update incrementally if possible)
    all_notes = data_manager.get_all_notes() # Get all notes, including the new one
    all_embeddings = [note.embedding for note in all_notes if hasattr(note, 'embedding') and note.embedding is not None]

    if not all_embeddings:
         # Handle case where no notes have embeddings (e.g., first note)
        new_note.position = [0.0, 0.0, 0.0] # Default position
    else:
        # This part needs careful review based on how PositionCalculator and DataManager work.
        # The current PositionCalculator seems to expect a list of embeddings and returns a list of positions.
        # We need to map these positions back to the correct notes.
        # For simplicity, let's assume it recalculates for all and DataManager updates them.

        positions = position_calculator.calculate_positions(all_embeddings)

        # Assign positions back to notes
        # This assumes the order of notes from get_all_notes and embeddings fed to calculate_positions is consistent.
        notes_with_embeddings_idx = 0
        for note in all_notes:
            if hasattr(note, 'embedding') and note.embedding is not None:
                if notes_with_embeddings_idx < len(positions):
                    note.position = positions[notes_with_embeddings_idx]
                    notes_with_embeddings_idx += 1
                else:
                    # Should not happen if logic is correct
                    note.position = [0,0,0] # Default fallback

    data_manager.save_notes() # Save all notes with updated positions

    # Find the newly added note (it might have an ID now) to return its details
    # This is a simplification; DataManager should ideally return the created/updated note.
    # For now, we'll just return the input content and its new position.
    # A more robust way would be for add_note or get_all_notes to make the specific new_note object available.
    created_note_data = {
        'id': getattr(new_note, 'id', 'unknown'), # Assuming Note has an ID
        'content': new_note.content,
        'position': new_note.position,
        'embedding': new_note.embedding # Optional: might not need to send full embedding to frontend
    }
    return jsonify(created_note_data), 201

@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = data_manager.get_all_notes()
    # Ensure notes are serializable (e.g. convert Note objects to dicts)
    notes_data = []
    for note in notes:
        notes_data.append({
            'id': getattr(note, 'id', None), # Assuming Note objects have an 'id' attribute
            'content': note.content,
            'position': getattr(note, 'position', [0,0,0]), # Ensure position exists
            # 'embedding': note.embedding # Usually not needed for GET all, unless frontend uses it
        })
    return jsonify(notes_data)

if __name__ == '__main__':
    # Make sure to run this from the project root directory for imports to work correctly if not installed as a package
    # e.g., python src/api/main.py
    app.run(debug=True, port=5001) # Using port 5001 to avoid conflict with React dev server
