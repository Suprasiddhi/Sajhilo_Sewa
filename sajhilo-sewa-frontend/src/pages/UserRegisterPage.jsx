import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './UserRegisterPage.module.css';

const UserRegisterPage = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Register attempt:', formData);
    // Functionality not integrated as per request
  };

  return (
    <div className={styles.container}>
      <div className={styles.registerCard}>
        <div className={styles.header}>
          <div className={styles.logoIcon}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className={styles.title}>Create Account</h1>
          <p className={styles.subtitle}>Join us and start your learning journey</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formRow}>
            <div className={styles.inputGroup}>
              <label className={styles.label}>First Name *</label>
              <input
                type="text"
                name="firstName"
                className={styles.input}
                placeholder="Sajhilo"
                value={formData.firstName}
                onChange={handleChange}
                required
              />
            </div>
            <div className={styles.inputGroup}>
              <label className={styles.label}>Last Name *</label>
              <input
                type="text"
                name="lastName"
                className={styles.input}
                placeholder="Sewa"
                value={formData.lastName}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className={styles.inputGroup}>
            <label className={styles.label}>Email Address *</label>
            <input
              type="email"
              name="email"
              className={styles.input}
              placeholder="sajhilosewa@gmail.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

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
            <label className={styles.label}>Password *</label>
            <input
              type="password"
              name="password"
              className={styles.input}
              placeholder="••••••••"
              value={formData.password}
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
            Get Started
          </button>
        </form>

        <p className={styles.terms}>
          By creating an account, you agree to our
          <Link to="/terms">Terms of Service</Link> and
          <Link to="/privacy">Privacy Policy</Link>
        </p>

        <div className={styles.footer}>
          Already have an account?
          <Link to="/login" className={styles.signInLink}>Sign In</Link>
        </div>
      </div>
    </div>
  );
};

export default UserRegisterPage;
