import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Seasonal bark backgrounds
const getSeasonalBark = () => {
  // Dev preview mode - check URL for ?bark=season
  const urlParams = new URLSearchParams(window.location.search);
  const previewSeason = urlParams.get('bark');
  if (previewSeason) {
    const seasonMap = {
      'spring': 'bark-spring.jpg',
      'summer': 'bark-summer.jpg', 
      'fall': 'bark-fall.jpg',
      'winter': 'bark-winter.jpg'
    };
    if (seasonMap[previewSeason]) return seasonMap[previewSeason];
  }
  
  // Normal seasonal logic
  const month = new Date().getMonth(); // 0-11
  
  // Spring: March(2), April(3), May(4)
  if (month >= 2 && month <= 4) return 'bark-spring.jpg';
  
  // Summer: June(5), July(6), August(7)  
  if (month >= 5 && month <= 7) return 'bark-summer.jpg';
  
  // Fall: September(8), October(9), November(10)
  if (month >= 8 && month <= 10) return 'bark-fall.jpg';
  
  // Winter: December(11), January(0), February(1)
  return 'bark-winter.jpg';
};

function Modal({ open, onClose, children }) {
  const [showSquirrel, setShowSquirrel] = useState(false);
  const [modalFade, setModalFade] = useState(false);

  const handleClose = () => {
    setShowSquirrel(true);
    setTimeout(() => {
      setModalFade(true);
    }, 350); // Squirrel starts, then modal fades
    setTimeout(() => {
      setShowSquirrel(false);
      setModalFade(false);
      onClose();
    }, 900); // Squirrel animation duration
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.22 }}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(20,30,40,0.85)',
            zIndex: 2000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden', // Prevent scrollbars
          }}
        >
          <motion.div
            initial={{ scale: 0.85, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.85, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28, duration: 0.32 }}
            style={{
              background: `
                linear-gradient(rgba(25, 15, 10, 0.35), rgba(35, 20, 15, 0.35)),
                url('/app/images/${getSeasonalBark()}?v=2') center/cover
              `,
              borderRadius: '12px',
              boxShadow: '0 12px 40px rgba(0,0,0,0.6), inset 0 2px 0 rgba(139, 90, 43, 0.3), inset 0 -1px 0 rgba(35, 25, 18, 0.6)',
              border: '2px solid rgba(139, 90, 43, 0.6)',
              minWidth: '320px',
              width: 'auto',
              maxWidth: '520px',
              maxHeight: '85vh',
              padding: '1.5rem',
              color: '#f5e6d3',
              position: 'relative',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              opacity: modalFade ? 0.2 : 1,
              transition: 'opacity 0.4s',
              textShadow: '0 2px 4px rgba(0,0,0,0.8)'
            }}
          >
            {children}
            {/* Squirrel animation overlays modal, centered vertically */}
            <AnimatePresence>
              {showSquirrel && (
                <motion.span
                  initial={{ x: -120, scale: 0.7, opacity: 0 }}
                  animate={{ x: '60vw', scale: 1.2, opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 180, damping: 18, duration: 0.9 }}
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: '7rem',
                    color: '#f39c12',
                    textShadow: '0 4px 24px #223a2c',
                    userSelect: 'none',
                    zIndex: 10,
                    pointerEvents: 'none',
                  }}
                >
                  🐿️
                </motion.span>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default Modal;
