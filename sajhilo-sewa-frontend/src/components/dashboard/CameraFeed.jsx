import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './CameraFeed.module.css';
import gestureWebSocket from '../../services/gestureWebSocket';
import { getToken } from '../../utils/auth';

const CameraFeed = ({ onRecognition, mode = "recognition" }) => {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [stream, setStream] = useState(null);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
          video: true 
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setIsActive(true);

      // --- ML Integration ---
      const clientId = `client_${Math.random().toString(36).substr(2, 9)}`;
      gestureWebSocket.connect(clientId, mode);
      
      // --- Authentication Sync ---
      const token = getToken();
      if (token) {
        // Wait for WebSocket to open before sending auth
        setTimeout(() => {
          if (gestureWebSocket.ws && gestureWebSocket.ws.readyState === WebSocket.OPEN) {
            gestureWebSocket.ws.send(JSON.stringify({
              type: "auth",
              token: token
            }));
            console.log("🔐 CameraFeed: Sent auth token to backend");
          }
        }, 1000);
      }
      
      gestureWebSocket.onResult = (result) => {
        if (onRecognition) {
          onRecognition({
            gesture: result.gesture,
            nepali: result.nepali,
            confidence: result.confidence,
            sentence: result.sentence,
            nepaliSentence: result.nepaliSentence,
            is_final: result.is_final
          });
        }
      };

      gestureWebSocket.startCapture({ current: videoRef.current }, 20);

    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Could not access camera. Please ensure you have given permission.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setIsActive(false);
    gestureWebSocket.disconnect();
  };

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Camera Feed</h2>
        <div className={`${styles.status} ${isActive ? styles.active : ''}`}>
          <span className={styles.statusDot}></span>
          {isActive ? 'Live' : 'Ready'}
        </div>
      </div>

      <div className={styles.videoWrapper}>
        {!isActive && (
          <div className={styles.placeholder}>
            <div className={styles.placeholderIcon}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                <circle cx="12" cy="13" r="4" />
              </svg>
            </div>
            <p className={styles.placeholderText}>Click "Start Session" to begin recognition</p>
          </div>
        )}
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline 
          className={`${styles.video} ${isActive ? styles.visible : ''}`}
        />
      </div>

      <div className={styles.controls}>
        {!isActive ? (
          <button className={styles.startButton} onClick={startCamera}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <polygon points="10 8 16 12 10 16 10 8" />
            </svg>
            Start Session
          </button>
        ) : (
          <button className={styles.stopButton} onClick={stopCamera}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="6" y="6" width="12" height="12" />
            </svg>
            Stop Session
          </button>
        )}
        <button 
          className={styles.demoButton}
          onClick={() => navigate('/practice')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          Demo Mode
        </button>
      </div>
    </div>
  );
};

export default CameraFeed;
