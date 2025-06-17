import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Import axios
import './App.css';
import NoteEditor from './components/NoteEditor';
import NoteVisualizer from './components/NoteVisualizer';

const API_URL = 'http://localhost:5001/api'; // Backend API URL

function App() {
  const [notes, setNotes] = useState([]);

  // Function to fetch notes from backend
  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_URL}/notes`);
      setNotes(response.data || []); // Assuming response.data is an array of notes
    } catch (error) {
      console.error('Error fetching notes:', error);
      // Optionally, set notes to an empty array or handle error in UI
      setNotes([]);
    }
  };

  // useEffect to fetch notes when component mounts
  useEffect(() => {
    fetchNotes();
  }, []); // Empty dependency array means this runs once on mount

  const handleSaveNote = async (content) => {
    if (!content.trim()) {
      alert('Note content cannot be empty.'); // Basic validation
      return;
    }
    try {
      const response = await axios.post(`${API_URL}/notes`, { content });
      // Add the new note to the existing notes state
      // Assuming backend returns the newly created note object with id, content, position
      setNotes(prevNotes => [...prevNotes, response.data]);
      // Or, for simplicity, just refetch all notes (less optimal but ensures consistency)
      // await fetchNotes();
    } catch (error) {
      console.error('Error saving note:', error);
      // Optionally, display an error message to the user
      alert(`Failed to save note: ${error.response?.data?.error || error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>NoteSphere</h1>
      </header>
      <div className="main-content">
        <div className="note-editor-container">
          <NoteEditor onSave={handleSaveNote} />
        </div>
        <div className="note-visualizer-container">
          <NoteVisualizer notes={notes} />
        </div>
      </div>
    </div>
  );
}

export default App;
