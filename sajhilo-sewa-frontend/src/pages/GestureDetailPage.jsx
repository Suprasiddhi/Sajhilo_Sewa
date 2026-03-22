import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styles from './GestureDetailPage.module.css';

const MediaCarousel = ({ media }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [touchStart, setTouchStart] = useState(null);
  const [touchEnd, setTouchEnd] = useState(null);

  // Minimum swipe distance in pixels
  const minSwipeDistance = 50;

  if (!media || media.length === 0) return null;

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % media.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + media.length) % media.length);
  };

  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e) => setTouchEnd(e.targetTouches[0].clientX);

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    if (isLeftSwipe) nextSlide();
    if (isRightSwipe) prevSlide();
  };

  return (
    <div className={styles.carouselContainer}>
      <div 
        className={styles.carouselWindow}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        <div 
          className={styles.carouselTrack} 
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {media.map((m, i) => (
            <div key={m.id || i} className={styles.carouselSlide}>
              {m.media_type === 'video' ? (
                <video src={m.url} className={styles.video} controls muted loop />
              ) : (
                <img src={m.url} alt="gesture media" className={styles.image} />
              )}
            </div>
          ))}
        </div>
      </div>

      {media.length > 1 && (
        <>
          <button className={`${styles.navBtn} ${styles.prev}`} onClick={prevSlide}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <button className={`${styles.navBtn} ${styles.next}`} onClick={nextSlide}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
          <div className={styles.dots}>
            {media.map((_, i) => (
              <span 
                key={i} 
                className={`${styles.dot} ${currentIndex === i ? styles.activeDot : ''}`}
                onClick={() => setCurrentIndex(i)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

const GestureDetailPage = () => {
  const { id } = useParams();
  const [gesture, setGesture] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Suppress ResizeObserver loop limit exceeded error
    const handleError = (e) => {
      if (e.message === 'ResizeObserver loop completed with undelivered notifications.' || 
          e.message === 'ResizeObserver loop limit exceeded') {
        const resizeObserverErrDiv = document.getElementById('webpack-dev-server-client-overlay-div');
        const resizeObserverErr = document.getElementById('webpack-dev-server-client-overlay');
        if (resizeObserverErr) resizeObserverErr.style.display = 'none';
        if (resizeObserverErrDiv) resizeObserverErrDiv.style.display = 'none';
        e.stopImmediatePropagation();
      }
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  useEffect(() => {
    fetchGesture();
  }, [id]);

  const fetchGesture = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/gestures/${id}`);
      if (res.ok) {
        const data = await res.json();
        setGesture(data);
      }
    } catch (err) {
      console.error("Error fetching gesture:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className={styles.loading}>Loading gesture details...</div>;
  if (!gesture) return <div className={styles.error}>Gesture not found.</div>;

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <Link to="/practice" className={styles.backBtn}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          Back to Practice
        </Link>
        <div className={styles.titleInfo}>
          <h1 className={styles.title}>{gesture.name}</h1>
          <span className={styles.categoryBadge}>{gesture.category}</span>
        </div>
      </header>

      <main className={styles.mainContent}>
        <div className={styles.sectionsGrid}>
          {gesture.sections.map((section, index) => (
            <section key={section.id} className={styles.sectionCard}>
              <div className={styles.sectionHeader}>
                <span className={styles.sectionNumber}>0{index + 1}</span>
                <h2 className={styles.sectionTitle}>{section.title}</h2>
              </div>
              
              <MediaCarousel media={section.media} />

              {section.description && (
                <div className={styles.descriptionBox}>
                  <p className={styles.description}>{section.description}</p>
                </div>
              )}
            </section>
          ))}
        </div>
      </main>
    </div>
  );
};

export default GestureDetailPage;
