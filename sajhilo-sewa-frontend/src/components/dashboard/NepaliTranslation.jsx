import React from 'react';
import styles from './NepaliTranslation.module.css';

const NepaliTranslation = ({ text, confidence }) => {
  const displayConfidence = Math.round((confidence || 0) * 100);
  
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.iconWrapper}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </div>
        <h2 className={styles.title}>नेपाली अनुवाद</h2>
      </div>

      <div className={styles.translationBox}>
        {text ? (
          <p className={styles.translationText}>{text}</p>
        ) : (
          <p className={styles.placeholderText}>तपाईंको अनुवाद यहाँ देखा पर्नेछ...</p>
        )}
      </div>

      <div className={styles.footer}>
        <div className={styles.confidenceHeader}>
          <span>Confidence Score</span>
          <span className={styles.percentage}>{displayConfidence}%</span>
        </div>
        <div className={styles.progressTrack}>
          <div className={styles.progressBar} style={{ width: `${displayConfidence}%` }}></div>
        </div>
      </div>
    </div>
  );
};

export default NepaliTranslation;
