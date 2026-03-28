import React, { useState } from "react";
import styles from "./HomePage.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import RecognitionHistory from "../components/dashboard/RecognitionHistory";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";
import EnglishTextOutput from "../components/dashboard/EnglishTextOutput";

function HomePage() {
  const [recognitionResult, setRecognitionResult] = useState({
    english: "",
    nepali: "",
    confidence: 0
  });

  const handleRecognition = (result) => {
    setRecognitionResult(result);
  };

  return (
    <div className={styles.homePage}>
      <header className={styles.header}>
        <div className={styles.welcomeCard}>
          <h1 className={styles.title}>Welcome to Sajhilo Sewa</h1>
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
          <EnglishTextOutput text={recognitionResult.english} />
        </div>
        <div className={styles.fullWidthRow}>
          <NepaliTranslation 
            text={recognitionResult.nepali} 
            confidence={recognitionResult.confidence} 
          />
        </div>

      </div>
    </div>
  );
}

export default HomePage;
