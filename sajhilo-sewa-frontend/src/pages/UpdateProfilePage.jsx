import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './UpdateProfilePage.module.css';

const UpdateProfilePage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    newPassword: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Update profile attempt:', formData);
    // Functionality not integrated as per request
  };

  return (
    <div className={styles.container}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <div className={styles.logoIcon}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className={styles.title}>Update Profile</h1>
          <p className={styles.subtitle}>Enter your details to reset your password</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label className={styles.label}>Username *</label>
            <input
              type="text"
              name="username"
              className={styles.input}
              placeholder="sajhilo_sewa"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>Email Address *</label>
            <input
              type="email"
              name="email"
              className={styles.input}
              placeholder="name@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>New Password *</label>
            <input
              type="password"
              name="newPassword"
              className={styles.input}
              placeholder="••••••••"
              value={formData.newPassword}
              onChange={handleChange}
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>Confirm Password *</label>
            <input
              type="password"
              name="confirmPassword"
              className={styles.input}
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>

          <button type="submit" className={styles.submitButton}>
            Update Password
          </button>
        </form>

        <div className={styles.footer}>
          Remembered your password? 
          <Link to="/login" className={styles.signUpLink}>Sign In</Link>
        </div>
      </div>
    </div>
  );
};

export default UpdateProfilePage;
