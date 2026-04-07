import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../utils/auth';
import styles from "./Header.module.css";

function Header() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (err) {
        console.error("Failed to parse user from localStorage", err);
      }
    }
  }, []);

  const handleLogout = () => {
    logout();
  };

  return (
    <header className={styles.header}>
      <div className={styles.breadcrumb}>
        {/* Placeholder for breadcrumbs or page title */}
      </div>

      <div className={styles.userSection}>
        {user ? (
          <div className={styles.userBadge}>
            <div className={styles.avatar}>
              {user.username ? user.username[0].toUpperCase() : 'U'}
            </div>
            <span className={styles.userName}>
              {user.username}
            </span>
            <button className={styles.logoutButton} onClick={handleLogout} title="Logout">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </button>
          </div>
        ) : (
          <button className={styles.loginButton} onClick={() => navigate('/login')}>
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}

export default Header;
