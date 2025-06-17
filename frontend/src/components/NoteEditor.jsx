import React, { useState, useEffect, useRef } from 'react';

function NoteEditor({ onSave }) { // Added onSave prop
  const [noteContent, setNoteContent] = useState('');
  const textAreaRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.ctrlKey && event.key === 'n') {
        event.preventDefault();
        textAreaRef.current.focus();
        // Optionally, clear the textarea for a new note or handle as new note creation
        // setNoteContent('');
        console.log('Ctrl+N pressed - focusing editor');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const handleSave = () => {
    if (onSave) {
      onSave(noteContent);
    } else {
      console.log('Save clicked, no onSave handler provided yet:', noteContent);
    }
    // Optionally clear content after save:
    // setNoteContent('');
  };

  return (
    <div className="note-editor">
      <h3>Create / Edit Note</h3>
      <textarea
        ref={textAreaRef}
        value={noteContent}
        onChange={(e) => setNoteContent(e.target.value)}
        placeholder="Start writing your note here... (Ctrl+N to focus/new)"
        rows="10"
        style={{ width: '100%', padding: '10px', boxSizing: 'border-box' }}
      />
      <button onClick={handleSave} style={{ marginTop: '10px', padding: '10px 15px' }}>
        Save Note
      </button>
    </div>
  );
}

export default NoteEditor;
