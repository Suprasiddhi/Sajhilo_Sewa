import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './AdminDashboard.module.css';

const AdminDashboard = () => {
  const [activeSection, setActiveSection] = useState('gestures');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gestureData, setGestureData] = useState({
    title: '',
    category: 'alphabets',
    description: '',
    videos: [{ id: Date.now(), file: null }]
  });

  const handleAddMoreVideo = () => {
    setGestureData(prev => ({
      ...prev,
      videos: [...prev.videos, { id: Date.now(), file: null }]
    }));
  };

  const handleFileChange = (id, file) => {
    setGestureData(prev => ({
      ...prev,
      videos: prev.videos.map(v => v.id === id ? { ...v, file } : v)
    }));
  };

  const handleRemoveVideo = (id) => {
    setGestureData(prev => ({
      ...prev,
      videos: prev.videos.filter(v => v.id !== id)
    }));
  };

  const sections = [
    { 
      id: 'gestures', 
      label: 'Gestures',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
          <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
          <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
          <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
        </svg>
      )
    },
    { 
      id: 'history', 
      label: 'History',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 8v4l3 3" />
          <circle cx="12" cy="12" r="9" />
        </svg>
      )
    },
  ];

  return (
    <div className={styles.wrapper}>
      <header className={styles.topBar}>
        <div className={styles.topBarLeft}>
          <Link to="/" className={styles.viewSite}>
            &lt; View Site
          </Link>
        </div>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
          <span className={styles.logoText}>Sajhilo Sewa Admin</span>
        </div>
      </header>

      <div className={styles.container}>
        <aside className={styles.subSidebar}>
          {sections.map((section) => (
            <button
              key={section.id}
              className={`${styles.navButton} ${activeSection === section.id ? styles.active : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              {section.icon}
              <span>{section.label}</span>
            </button>
          ))}
        </aside>

        <main className={styles.content}>
          {activeSection === 'gestures' && (
            <div className={styles.sectionContent}>
              <header className={styles.header}>
                <h1 className={styles.title}>Gestures</h1>
                <button 
                  className={styles.addButton}
                  onClick={() => setIsModalOpen(true)}
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
            </div>
          )}

          {activeSection === 'history' && (
            <div className={styles.sectionContent}>
              <header className={styles.header}>
                <h1 className={styles.title}>History</h1>
              </header>
              
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 8v4l3 3" />
                    <circle cx="12" cy="12" r="9" />
                  </svg>
                </div>
                <h3>No history logs found</h3>
                <p>System activity and recognition history will appear here.</p>
              </div>
            </div>
          )}
        </main>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <header className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Add New Gesture</h2>
              <button 
                className={styles.closeButton}
                onClick={() => setIsModalOpen(false)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </header>

            <div className={styles.modalBody}>
              <div className={styles.formGroup}>
                <label className={styles.formLabel}>Gesture Name (Title)</label>
                <input 
                  type="text" 
                  className={styles.formInput} 
                  placeholder="e.g. Namaste"
                  value={gestureData.title}
                  onChange={(e) => setGestureData({...gestureData, title: e.target.value})}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>Category</label>
                <select 
                  className={styles.formSelect}
                  value={gestureData.category}
                  onChange={(e) => setGestureData({...gestureData, category: e.target.value})}
                >
                  <option value="alphabets">Alphabets</option>
                  <option value="numbers">Numbers</option>
                  <option value="words">Words</option>
                  <option value="common">Common Gestures</option>
                </select>
              </div>

              <div className={styles.formGroup}>
                <label className={styles.formLabel}>Description</label>
                <textarea 
                  className={styles.formTextarea} 
                  placeholder="Describe the gesture movements..."
                  value={gestureData.description}
                  onChange={(e) => setGestureData({...gestureData, description: e.target.value})}
                ></textarea>
              </div>

              <div className={styles.videoSection}>
                <div className={styles.videoHeader}>
                  <label className={styles.formLabel}>Video Collections</label>
                </div>
                
                {gestureData.videos.map((v, index) => (
                  <div key={v.id} className={styles.videoSlot}>
                    <div 
                      className={styles.dropzone}
                      onClick={() => document.getElementById(`file-${v.id}`).click()}
                      onDragOver={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                      onDrop={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                          handleFileChange(v.id, e.dataTransfer.files[0]);
                        }
                      }}
                    >
                      <svg className={styles.uploadIcon} width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                      {v.file ? (
                        <div className={styles.fileSelected}>
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                          <span>{v.file.name}</span>
                        </div>
                      ) : (
                        <>
                          <p>Drag & Drop or Click to upload Video {index + 1}</p>
                          <span style={{ fontSize: '0.8rem' }}>MP4, WebM up to 50MB</span>
                        </>
                      )}
                      <input 
                        type="file" 
                        id={`file-${v.id}`}
                        style={{ display: 'none' }} 
                        accept="video/*"
                        onChange={(e) => handleFileChange(v.id, e.target.files[0])}
                      />
                    </div>
                    {gestureData.videos.length > 1 && (
                      <button 
                        className={styles.removeVideoBtn}
                        onClick={() => handleRemoveVideo(v.id)}
                        title="Remove video"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="18" y1="6" x2="6" y2="18" />
                          <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                      </button>
                    )}
                  </div>
                ))}

                <button 
                  className={styles.addMoreBtn}
                  onClick={handleAddMoreVideo}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  <span>Add More Video</span>
                </button>
              </div>
            </div>

            <footer className={styles.modalFooter}>
              <button 
                className={styles.cancelBtn}
                onClick={() => setIsModalOpen(false)}
              >
                Cancel
              </button>
              <button className={styles.submitBtn}>
                Add Gesture
              </button>
            </footer>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
