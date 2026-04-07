import React, { useState } from "react";
import styles from "./HomePage.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import RecognitionHistory from "../components/dashboard/RecognitionHistory";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";
import EnglishTextOutput from "../components/dashboard/EnglishTextOutput";
import gestureWebSocket from "../services/gestureWebSocket";

function HomePage() {
  const [recognitionResult, setRecognitionResult] = useState({
    sentence: "",
    nepaliSentence: "",
    nepali: "",
    confidence: 0
  });

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
        <div className={styles.mainColumn}>
          <CameraFeed onRecognition={handleRecognition} />
        </div>
        
        <div className={styles.sideColumn}>
          <RecognitionHistory />
        </div>

        <div className={styles.fullWidthRow}>
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
        </div>
        <div className={styles.fullWidthRow}>
          <NepaliTranslation 
            text={recognitionResult.nepaliSentence || recognitionResult.nepali || "None"} 
            confidence={recognitionResult.confidence} 
          />
        </div>

      </div>
    </div>
  );
}

export default HomePage;
