import React from 'react';
import styles from "./Header.module.css";

function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.breadcrumb}>
        {/* Placeholder for breadcrumbs or page title */}
      </div>

      <div className={styles.userSection}>
        <div className={styles.userBadge}>
          <div className={styles.avatar}>U</div>
          <span className={styles.userName}>User</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
