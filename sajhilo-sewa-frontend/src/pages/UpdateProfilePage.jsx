import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './UpdateProfilePage.module.css';

const UpdateProfilePage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // 1. Password validation
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          new_password: formData.newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update password');
      }

      // 4. Success navigation
      navigate('/login', { state: { message: 'password changed' } });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.loginCard}>
        <div className={styles.header}>
          <div className={styles.logoImage}>
            <img src="/logo.png" alt="Sajhilo Sewa Logo" />
          </div>
          <h1 className={styles.title}>Update Profile</h1>
          <p className={styles.subtitle}>Enter your details to reset your password</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          {error && <div className={styles.errorMessage}>{error}</div>}
          
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

          <button type="submit" className={styles.submitButton} disabled={isLoading}>
            {isLoading ? 'Updating...' : 'Update Password'}
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
