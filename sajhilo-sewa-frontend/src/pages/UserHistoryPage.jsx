import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import styles from './UserHistoryPage.module.css';

const UserHistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await apiRequest('/api/history/');
      if (response && response.ok) {
        const data = await response.json();
        setHistory(data);
      } else {
        setError('Failed to load history');
      }
    } catch (err) {
      setError('An error occurred while fetching history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Practice History</h1>
        <p className={styles.subtitle}>
          Track your sign language recognition journey. Every gesture saved helps you grow.
        </p>
      </header>

      {loading ? (
        <div className={styles.loadingState}>
          <div className={styles.loader}></div>
          <p>Analyzing your records...</p>
        </div>
      ) : error ? (
        <div className={styles.errorState}>
          <h3>Oops!</h3>
          <p>{error}</p>
          <button onClick={fetchHistory} className={styles.retryBtn}>Retry</button>
        </div>
      ) : history.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 8v4l3 3" />
              <circle cx="12" cy="12" r="9" />
              <path d="M16 12h2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2h-2" />
              <path d="M8 12H6a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2" />
            </svg>
          </div>
          <h3>No History Yet</h3>
          <p>Start practicing to see your translated gestures appear here.</p>
        </div>
      ) : (
        <div className={styles.historyList}>
          {history.map((record, index) => (
            <div 
              key={record.id} 
              className={styles.historyCard}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className={styles.cardHeader}>
                <span className={`${styles.modeBadge} ${styles[record.mode]}`}>
                  {record.mode === 'alphabet' ? 'Letter' : 'Gesture'}
                </span>
                <span className={styles.timestamp}>{formatDate(record.created_at)}</span>
              </div>
              
              <div className={styles.cardBody}>
                <div className={styles.translationGroup}>
                  <label>English</label>
                  <p className={styles.englishText}>{record.english_text}</p>
                </div>
                
                <div className={styles.divider}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="13 17 18 12 13 7" />
                    <polyline points="6 17 11 12 6 7" />
                  </svg>
                </div>

                <div className={styles.translationGroup}>
                  <label>Nepali</label>
                  <p className={styles.nepaliText}>{record.nepali_text}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UserHistoryPage;
