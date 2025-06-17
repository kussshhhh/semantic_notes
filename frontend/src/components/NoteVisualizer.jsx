import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Box } from '@react-three/drei';

function NoteVisualizer({ notes }) {
  return (
    <div style={{ width: '100%', height: '100%', minHeight: '400px' }}>
      <Canvas camera={{ position: [0, 5, 10], fov: 75 }}> {/* Adjusted camera for better view */}
        <ambientLight intensity={0.8} /> {/* Slightly increased ambient light */}
        <pointLight position={[10, 10, 10]} intensity={1} /> {/* Ensured point light has intensity */}

        {notes && notes.map((note) => (
          <Box
            key={note.id} // Use note.id as key
            position={note.position || [0, 0, 0]} // Use note.position array
            args={[0.5, 0.5, 0.5]} // Standard size for notes
          >
            <meshStandardMaterial color={'#6A8D92'} /> {/* Using a pleasant fixed color */}
          </Box>
        ))}

        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default NoteVisualizer;
