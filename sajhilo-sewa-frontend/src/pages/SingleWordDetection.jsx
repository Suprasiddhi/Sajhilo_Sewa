import React from "react";
import styles from "./SingleWordDetection.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import RecognitionHistory from "../components/dashboard/RecognitionHistory";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";

function SingleWordDetection() {
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
          <CameraFeed />
        </div>
        
        <div className={styles.sideColumn}>
          <RecognitionHistory />
        </div>

        <div className={styles.fullWidthRow}>
          <NepaliTranslation />
        </div>
      </div>
    </div>
  );
}

export default SingleWordDetection;
