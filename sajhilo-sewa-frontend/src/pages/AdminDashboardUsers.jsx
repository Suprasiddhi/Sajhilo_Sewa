import React from 'react';
import styles from './AdminDashboard.module.css';

const AdminDashboardUsers = ({ allUsers, loading, handleDeleteUser }) => {
  return (
    <div className={styles.sectionContent}>
      <header className={styles.header}>
        <h1 className={styles.title}>User Management</h1>
      </header>

      <div className={styles.usersList}>
        {loading ? (
          <div className={styles.loading}>Loading users...</div>
        ) : allUsers.length > 0 ? (
          <div className={styles.tableContainer}>
            <table className={styles.userTable}>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Joined</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {allUsers.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className={styles.userInfoCell}>
                        <div className={styles.userAvatar}>{user.username[0].toUpperCase()}</div>
                        <span className={styles.userNameText}>{user.username}</span>
                      </div>
                    </td>
                    <td>{user.email}</td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`${styles.statusBadge} ${user.is_active ? styles.active : styles.inactive}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      <button 
                        className={styles.deleteUserBtn}
                        onClick={() => handleDeleteUser(user.id)}
                        title="Delete User"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className={styles.emptyState}>
            <p>No users found in the system.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboardUsers;
