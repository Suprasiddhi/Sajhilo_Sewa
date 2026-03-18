import React, { useState } from 'react';
import styles from './PracticePage.module.css';

const PracticePage = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  const categories = ['All', 'Alphabet', 'Numbers', 'Common Phrases', 'Greetings'];
  
  const gestures = [
    { id: 1, title: 'Alphabet A', category: 'Alphabet', difficulty: 'Easy', duration: '0:15' },
    { id: 2, title: 'Number 1-10', category: 'Numbers', difficulty: 'Easy', duration: '0:45' },
    { id: 3, title: 'Thank You', category: 'Greetings', difficulty: 'Medium', duration: '0:20' },
    { id: 4, title: 'How are you?', category: 'Greetings', difficulty: 'Medium', duration: '0:30' },
    { id: 5, title: 'I need help', category: 'Common Phrases', difficulty: 'Hard', duration: '0:40' },
    { id: 6, title: 'Alphabet B', category: 'Alphabet', difficulty: 'Easy', duration: '0:15' },
  ];

  const filteredGestures = selectedCategory === 'All' 
    ? gestures 
    : gestures.filter(g => g.category === selectedCategory);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Practice Ground</h1>
        <p className={styles.subtitle}>Watch and learn ASL gestures. Practice them yourself to improve recognition accuracy.</p>
      </header>

      <div className={styles.filters}>
        {categories.map(cat => (
          <button 
            key={cat} 
            className={`${styles.filterBtn} ${selectedCategory === cat ? styles.active : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className={styles.videoGrid}>
        {filteredGestures.map(gesture => (
          <div key={gesture.id} className={styles.videoCard}>
            <div className={styles.thumbnail}>
              <div className={styles.playIcon}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
              </div>
              <span className={styles.duration}>{gesture.duration}</span>
            </div>
            <div className={styles.cardContent}>
              <div className={styles.cardHeader}>
                <h3 className={styles.gestureTitle}>{gesture.title}</h3>
                <span className={`${styles.badge} ${styles[gesture.difficulty.toLowerCase()]}`}>
                  {gesture.difficulty}
                </span>
              </div>
              <p className={styles.category}>{gesture.category}</p>
              <button className={styles.practiceBtn}>Start Practice</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PracticePage;
