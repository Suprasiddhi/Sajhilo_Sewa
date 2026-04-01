import React from 'react';
import styles from './AdminDashboard.module.css';

const AdminDashboardHistory = () => {
  return (
    <div className={styles.sectionContent}>
      <header className={styles.header}>
        <h1 className={styles.title}>History</h1>
      </header>
      
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 8v4l3 3" />
            <circle cx="12" cy="12" r="9" />
          </svg>
        </div>
        <h3>No history logs found</h3>
        <p>System activity and recognition history will appear here.</p>
      </div>
    </div>
  );
};

export default AdminDashboardHistory;
