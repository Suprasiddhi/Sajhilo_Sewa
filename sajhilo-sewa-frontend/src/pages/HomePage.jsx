import React from "react";
import styles from "./HomePage.module.css";
import CameraFeed from "../components/dashboard/CameraFeed";
import RecognitionHistory from "../components/dashboard/RecognitionHistory";
import NepaliTranslation from "../components/dashboard/NepaliTranslation";

function HomePage() {
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

export default HomePage;
