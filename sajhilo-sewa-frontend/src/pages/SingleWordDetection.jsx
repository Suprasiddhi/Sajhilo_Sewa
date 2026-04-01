import React, { useState } from "react";
import styles from "./SingleWordDetection.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import RecognitionHistory from "../components/dashboard/RecognitionHistory";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";
import EnglishTextOutput from "../components/dashboard/EnglishTextOutput";
import gestureWebSocket from "../services/gestureWebSocket";

function SingleWordDetection() {
  const [recognitionResult, setRecognitionResult] = useState({
    english: "",
    nepali: "",
    confidence: 0
  });

  const handleRecognition = (result) => {
    setRecognitionResult({
      english: result.sentence, // The whole word built so far
      nepali: result.gesture,    // The current letter detected
      confidence: result.confidence
    });
  };

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.welcomeCard}>
          <h1 className={styles.title}>Single Word Detection</h1>
          <p className={styles.subtitle}>
            Focus on individual letters and words. Perfect for finger spelling or discrete gestures.
          </p>
        </div>
      </header>

      <div className={styles.dashboardGrid}>
        <div className={styles.mainColumn}>
          <CameraFeed onRecognition={handleRecognition} mode="alphabet" />
        </div>
        
        <div className={styles.sideColumn}>
          <RecognitionHistory />
        </div>

        <div className={styles.fullWidthRow}>
          <div className={styles.outputControls}>
            <EnglishTextOutput text={recognitionResult.english || "..."} />
            <button 
              className={styles.clearButton} 
              onClick={() => {
                if (gestureWebSocket.ws?.readyState === WebSocket.OPEN) {
                  gestureWebSocket.ws.send(JSON.stringify({ type: "clear_sentence" }));
                }
                setRecognitionResult({ english: "", nepali: "", confidence: 0 });
              }}
            >
              Clear Text
            </button>
          </div>
        </div>
        <div className={styles.fullWidthRow}>
          <NepaliTranslation 
            text={recognitionResult.nepali || "None"} 
            confidence={recognitionResult.confidence} 
          />
        </div>
      </div>
    </div>
  );
}

export default SingleWordDetection;
