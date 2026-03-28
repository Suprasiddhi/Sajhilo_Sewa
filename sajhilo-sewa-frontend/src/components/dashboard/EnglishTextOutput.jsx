import React from 'react';
import styles from './EnglishTextOutput.module.css';

const EnglishTextOutput = ({ text }) => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.iconWrapper}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <h2 className={styles.title}>English Recognition</h2>
      </div>

      <div className={styles.recognitionBox}>
        {text ? (
          <span className={styles.text}>{text}</span>
        ) : (
          <p className={styles.placeholderText}>Recognized gesture will appear here...</p>
        )}
      </div>

      <div className={styles.footer}>
        <span className={styles.statusLabel}>Real-time Feedback</span>
        <div className={styles.liveBadge}>Live</div>
      </div>
    </div>
  );
};

export default EnglishTextOutput;
