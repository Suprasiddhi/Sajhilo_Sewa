import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import styles from "./HomePage.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";
import EnglishTextOutput from "../components/dashboard/EnglishTextOutput";
import gestureWebSocket from "../services/gestureWebSocket";

function HomePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [recognitionResult, setRecognitionResult] = useState({
    sentence: "",
    nepaliSentence: "",
    nepali: "",
    confidence: 0
  });

  const showAccessDenied = location.state?.error === 'access_denied';

  React.useEffect(() => {
    if (showAccessDenied) {
      window.history.replaceState({}, document.title);
    }
  }, [showAccessDenied]);
  const handleRecognition = (result) => {
    setRecognitionResult({
      sentence: result.sentence,
      nepaliSentence: result.nepaliSentence,
      nepali: result.nepali,
      confidence: result.confidence
    });
  };

  return (
    <div className={styles.homePage}>
      {showAccessDenied && (
        <div className={styles.accessDeniedWarning}>
          <div className={styles.warningContent}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>Access Denied: Administrative privileges required.</span>
          </div>
          <button 
            className={styles.closeWarning} 
            onClick={() => navigate(location.pathname, { replace: true, state: {} })}
          >
            ×
          </button>
        </div>
      )}
      <header className={styles.header}>
        <div className={styles.welcomeCard}>
          <h1 className={styles.title}>Word & Sentence Detection</h1>
          <p className={styles.subtitle}>
            Start your sign language recognition session. Your gestures will
            be translated in real-time.
          </p>
        </div>
      </header>

      <div className={styles.dashboardGrid}>
        <div className={styles.sideColumn}>
          <div className={styles.outputControls}>
            <EnglishTextOutput text={recognitionResult.sentence || "..."} />
            <button 
              className={styles.clearButton} 
              onClick={() => {
                gestureWebSocket.clearSentence();
                setRecognitionResult({ sentence: "", nepali: "", confidence: 0 });
              }}
            >
              Clear Text
            </button>
          </div>
          <NepaliTranslation 
            text={recognitionResult.nepaliSentence || recognitionResult.nepali || "None"} 
            confidence={recognitionResult.confidence} 
          />
        </div>

        <div className={styles.mainColumn}>
          <CameraFeed onRecognition={handleRecognition} />
        </div>
      </div>
    </div>
  );
}

export default HomePage;
