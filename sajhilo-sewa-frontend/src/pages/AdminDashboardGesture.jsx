import React from 'react';
import styles from './AdminDashboard.module.css';

const AdminDashboardGesture = ({ 
  allGestures, 
  loading, 
  selectedCategory, 
  setSelectedCategory, 
  handleEditClick, 
  handleDelete, 
  setIsModalOpen, 
  setGestureData, 
  setIsEditing, 
  setCurrentEditId,
  isModalOpen,
  isEditing,
  gestureData,
  handleRemoveSection,
  handleSectionChange,
  handleRemoveMedia,
  handleMediaChange,
  handleAddMedia,
  handleAddMoreSection,
  handleSubmit
}) => {
  return (
    <div className={styles.sectionContent}>
      <header className={styles.header}>
        <h1 className={styles.title}>Gestures</h1>
        <button 
          className={styles.addButton}
          onClick={() => {
            setGestureData({
              name: '',
              category: 'alphabets',
              sections: [{ 
                id: Date.now(), 
                title: '', 
                description: '', 
                media: [{ id: Date.now(), media_type: 'video', url: '', file: null }] 
              }]
            });
            setIsEditing(false);
            setCurrentEditId(null);
            setIsModalOpen(true);
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>Add Gesture</span>
        </button>
      </header>

      <div className={styles.filterBar}>
        {['all', 'alphabets', 'numbers', 'common'].map((cat) => (
          <button
            key={cat}
            className={`${styles.filterButton} ${selectedCategory === cat ? styles.activeFilter : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1).replace('_', ' ')}
          </button>
        ))}
      </div>
      
      <div className={styles.gesturesGrid}>
        {loading ? (
          <div className={styles.loading}>Loading gestures...</div>
        ) : allGestures.length > 0 ? (
          allGestures.map(gesture => (
            <div key={gesture.id} className={styles.videoCard}>
              <div className={styles.thumbnail}>
                {gesture.sections && gesture.sections[0] && gesture.sections[0].media && (
                  (() => {
                    const videoMedia = gesture.sections[0].media.find(m => m.media_type === 'video') || gesture.sections[0].media[0];
                    return videoMedia ? <video src={videoMedia.url} className={styles.previewVideo} muted /> : null;
                  })()
                )}
                <div className={styles.cardActions}>
                  <button 
                    className={styles.actionBtn} 
                    onClick={(e) => { e.stopPropagation(); handleEditClick(gesture); }}
                    title="Edit Gesture"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                  </button>
                  <button 
                    className={`${styles.actionBtn} ${styles.deleteBtn}`} 
                    onClick={(e) => { e.stopPropagation(); handleDelete(gesture.id); }}
                    title="Delete Gesture"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
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
              </div>
            </div>
          ))
        ) : (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
              </svg>
            </div>
            <h3>No dynamic gestures added yet</h3>
            <p>Start by clicking the "Add Gesture" button to expand the system library.</p>
          </div>
        )}
      </div>

    </div>
  );
};

export default AdminDashboardGesture;
