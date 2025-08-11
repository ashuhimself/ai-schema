import React from 'react';

// Simple toaster component - in a full implementation, you'd use a proper toast library
export const Toaster: React.FC = () => {
  return (
    <div id="toast-container" className="fixed top-4 right-4 z-50">
      {/* Toast messages will be dynamically inserted here */}
    </div>
  );
};