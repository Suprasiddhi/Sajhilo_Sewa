import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './PracticePage.module.css';

const PracticePage = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [gestures, setGestures] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  const categories = ['All', 'Alphabets', 'Numbers', 'Common Words'];
  
  useEffect(() => {
    fetchGestures();
  }, [selectedCategory]);

  const fetchGestures = async () => {
    setLoading(true);
    try {
      let categoryParam = selectedCategory === 'All' ? 'all' : selectedCategory.toLowerCase();
      if (categoryParam === 'common words') categoryParam = 'common';
      const response = await fetch(`http://localhost:8000/gestures/?category=${categoryParam}`);
      if (response.ok) {
        const data = await response.json();
        setGestures(data);
      }
    } catch (error) {
      console.error("Failed to fetch gestures:", error);
    } finally {
      setLoading(false);
    }
  };

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
        {loading ? (
          <div className={styles.loading}>Loading gestures...</div>
        ) : gestures.length > 0 ? (
          gestures.map(gesture => (
            <div 
              key={gesture.id} 
              className={styles.videoCard} 
              onClick={() => {
                const titleSlug = gesture.name.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]+/g, '');
                navigate(`/work/${gesture.id}/${titleSlug}`);
              }}
              style={{ cursor: 'pointer' }}
            >
              <div className={styles.thumbnail}>
                {gesture.sections && gesture.sections[0] && gesture.sections[0].media && (
                  (() => {
                    const videoMedia = gesture.sections[0].media.find(m => m.media_type === 'video') || gesture.sections[0].media[0];
                    return videoMedia ? (
                      <div className={styles.videoPreviewContainer}>
                        <video 
                          src={videoMedia.url} 
                          className={styles.previewVideo} 
                          muted 
                          preload="metadata"
                          playsInline
                        />
                      </div>
                    ) : null;
                  })()
                )}
                <div className={styles.playIcon}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                </div>
              </div>
              <div className={styles.cardContent}>
                <div className={styles.cardHeader}>
                  <h3 className={styles.gestureTitle}>{gesture.name}</h3>
                </div>
                <p className={styles.category}>{gesture.category}</p>
                <div className={styles.sectionCount}>
                  {gesture.sections?.length || 0} Sections
                </div>
                <button className={styles.practiceBtn}>Start Practice</button>
              </div>
            </div>
          ))
        ) : (
          <div className={styles.empty}>No gestures found in this category.</div>
        )}
      </div>
    </div>
  );
};

export default PracticePage;
