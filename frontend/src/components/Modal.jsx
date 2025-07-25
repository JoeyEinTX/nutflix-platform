import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

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
              background: 'linear-gradient(135deg, #1a2332 0%, #223a2c 100%)',
              borderRadius: '16px',
              boxShadow: '0 8px 32px rgba(46,204,113,0.15)',
              border: '1px solid rgba(76,175,80,0.25)',
              minWidth: '320px',
              width: '70vw',
              maxWidth: '900px',
              maxHeight: '80vh',
              padding: '2.5rem',
              color: '#e0e0e0',
              position: 'relative',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              opacity: modalFade ? 0.2 : 1,
              transition: 'opacity 0.4s',
            }}
          >
            <button
              onClick={handleClose}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'rgba(46,204,113,0.15)',
                color: '#76b900',
                border: 'none',
                borderRadius: '6px',
                padding: '0.5rem 1rem',
                cursor: 'pointer',
                fontWeight: '700',
                fontSize: '1rem',
                boxShadow: '0 2px 8px rgba(76,175,80,0.08)'
              }}
            >
              × Close
            </button>
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
