import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './AdminDashboard.module.css';

const AdminDashboard = () => {
  const [activeSection, setActiveSection] = useState('overview');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [stats, setStats] = useState({
    total_users: 0,
    all_usernames: [],
    total_gestures: 0,
    latest_gestures: []
  });
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [gestureData, setGestureData] = useState({
    name: '',
    category: 'alphabets',
    sections: [{ 
      id: Date.now(), 
      title: '', 
      description: '', 
      media: [{ id: Date.now(), media_type: 'video', url: '', file: null }] 
    }]
  });

  React.useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/admin/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Error fetching stats:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddMoreSection = () => {
    setGestureData(prev => ({
      ...prev,
      sections: [...prev.sections, { 
        id: Date.now(), 
        title: '', 
        description: '', 
        media: [{ id: Date.now() + 1, media_type: 'video', url: '', file: null }] 
      }]
    }));
  };

  const handleAddMedia = (sectionId) => {
    setGestureData(prev => ({
      ...prev,
      sections: prev.sections.map(s => s.id === sectionId ? {
        ...s,
        media: [...s.media, { id: Date.now(), media_type: 'video', url: '', file: null }]
      } : s)
    }));
  };

  const handleMediaChange = (sectionId, mediaId, field, value) => {
    setGestureData(prev => ({
      ...prev,
      sections: prev.sections.map(s => s.id === sectionId ? {
        ...s,
        media: s.media.map(m => m.id === mediaId ? { ...m, [field]: value } : m)
      } : s)
    }));
  };

  const handleRemoveMedia = (sectionId, mediaId) => {
    setGestureData(prev => ({
      ...prev,
      sections: prev.sections.map(s => s.id === sectionId ? {
        ...s,
        media: s.media.filter(m => m.id !== mediaId)
      } : s)
    }));
  };

  const handleSectionChange = (id, field, value) => {
    setGestureData(prev => ({
      ...prev,
      sections: prev.sections.map(s => s.id === id ? { ...s, [field]: value } : s)
    }));
  };

  const handleRemoveSection = (id) => {
    setGestureData(prev => ({
      ...prev,
      sections: prev.sections.filter(s => s.id !== id)
    }));
  };

  const handleSubmit = async () => {
    try {
      // 1. Upload all files first to get URLs
      const updatedSections = await Promise.all(gestureData.sections.map(async (section) => {
        const updatedMedia = await Promise.all(section.media.map(async (mediaItem) => {
          if (mediaItem.file) {
            const formData = new FormData();
            formData.append('file', mediaItem.file);
            const res = await fetch('http://localhost:8000/gestures/upload', {
              method: 'POST',
              body: formData
            });
            const data = await res.json();
            return { ...mediaItem, url: data.url };
          }
          return mediaItem;
        }));
        return { ...section, media: updatedMedia };
      }));

      // 2. Submit the full gesture data
      const finalGesture = {
        name: gestureData.name,
        category: gestureData.category,
        sections: updatedSections.map(s => ({
          title: s.title,
          description: s.description,
          media: s.media.map(m => ({
            media_type: m.media_type,
            url: m.url
          }))
        }))
      };

      const res = await fetch('http://localhost:8000/gestures/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(finalGesture)
      });

      if (res.ok) {
        setIsModalOpen(false);
        // Refresh gestures or show success
      } else {
        alert("Failed to add gesture");
      }
    } catch (err) {
      console.error("Error submitting gesture:", err);
      alert("Error submitting gesture");
    }
  };

  const sections = [
    { 
      id: 'overview', 
      label: 'Overview',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </svg>
      )
    },
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
          {activeSection === 'overview' && (
            <div className={styles.sectionContent}>
              <header className={styles.header}>
                <h1 className={styles.title}>Dashboard Overview</h1>
              </header>

              <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                  <div className={styles.statIcon} style={{ background: '#e0f2fe', color: '#0ea5e9' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                  </div>
                  <div className={styles.statInfo}>
                    <span className={styles.statLabel}>Total Users</span>
                    <h2 className={styles.statValue}>{stats.total_users}</h2>
                  </div>
                </div>

                <div className={styles.statCard}>
                  <div className={styles.statIcon} style={{ background: '#f0fdf4', color: '#22c55e' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 11V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                      <path d="M14 10V4a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                      <path d="M10 10.5V6a2 2 0 0 0-2-2v0a2 2 0 0 0-2 2v0" />
                      <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15" />
                    </svg>
                  </div>
                  <div className={styles.statInfo}>
                    <span className={styles.statLabel}>Total Gestures</span>
                    <h2 className={styles.statValue}>{stats.total_gestures}</h2>
                  </div>
                </div>
              </div>

              <div className={styles.analysisGrid}>
                <div className={styles.analysisCard}>
                  <h3 className={styles.cardTitle}>Usernames</h3>
                  <div className={styles.scrollList}>
                    {stats.all_usernames.length > 0 ? (
                      stats.all_usernames.map((un, i) => (
                        <div key={i} className={styles.listItem}>
                          <div className={styles.userAvatar}>{un[0].toUpperCase()}</div>
                          <span className={styles.userName}>{un}</span>
                        </div>
                      ))
                    ) : (
                      <p className={styles.emptyText}>No users found</p>
                    )}
                  </div>
                </div>

                <div className={styles.analysisCard}>
                  <h3 className={styles.cardTitle}>Latest Practice Videos</h3>
                  <div className={styles.scrollList}>
                    {stats.latest_gestures.length > 0 ? (
                      stats.latest_gestures.map((gesture) => (
                        <div key={gesture.id} className={styles.gestureItem}>
                          <div className={styles.gesturePreview}>
                            {gesture.sections?.[0]?.media?.[0]?.url && (
                              <video src={gesture.sections[0].media[0].url} muted />
                            )}
                            {!gesture.sections?.[0]?.media?.[0]?.url && (
                              <div className={styles.noVideo}>No Video</div>
                            )}
                          </div>
                          <div className={styles.gestureInfo}>
                            <span className={styles.gestureName}>{gesture.name}</span>
                            <span className={styles.gestureCat}>{gesture.category}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className={styles.emptyText}>No gestures added yet</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

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
                <label className={styles.formLabel}>Main Gesture Name</label>
                <input 
                  type="text" 
                  className={styles.formInput} 
                  placeholder="e.g. Namaste"
                  value={gestureData.name}
                  onChange={(e) => setGestureData({...gestureData, name: e.target.value})}
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

              <div className={styles.sectionDivider}>
                <span>Gesture Sections / Contexts</span>
              </div>
              
              {gestureData.sections.map((section, index) => (
                <div key={section.id} className={styles.gestureSectionCard}>
                  <header className={styles.sectionCardHeader}>
                    <h4>Section {index + 1}</h4>
                    {gestureData.sections.length > 1 && (
                      <button 
                        className={styles.removeSectionBtn}
                        onClick={() => handleRemoveSection(section.id)}
                      >
                        Remove
                      </button>
                    )}
                  </header>

                  <div className={styles.formGroup}>
                    <label className={styles.formLabel}>Section Title</label>
                    <input 
                      type="text" 
                      className={styles.formInput} 
                      placeholder="e.g. Front View"
                      value={section.title}
                      onChange={(e) => handleSectionChange(section.id, 'title', e.target.value)}
                    />
                  </div>

                  <div className={styles.mediaList}>
                    <label className={styles.formLabel}>Media (Videos / Images)</label>
                    {section.media.map((mediaItem, mIndex) => (
                      <div key={mediaItem.id} className={styles.mediaItemCard}>
                        <div className={styles.mediaItemHeader}>
                          <span>Media {mIndex + 1}</span>
                          {section.media.length > 1 && (
                            <button 
                              className={styles.removeMediaBtn}
                              onClick={() => handleRemoveMedia(section.id, mediaItem.id)}
                            >
                              &times;
                            </button>
                          )}
                        </div>
                        
                        <div className={styles.formRow}>
                          <div className={styles.formGroup}>
                            <select 
                              className={styles.formSelect}
                              value={mediaItem.media_type}
                              onChange={(e) => handleMediaChange(section.id, mediaItem.id, 'media_type', e.target.value)}
                            >
                              <option value="video">Video</option>
                              <option value="image">Image</option>
                            </select>
                          </div>
                          <div className={styles.formGroup} style={{ flex: 2 }}>
                            <input 
                              type="text" 
                              className={styles.formInput} 
                              placeholder="URL (Optional)..."
                              value={mediaItem.url}
                              onChange={(e) => handleMediaChange(section.id, mediaItem.id, 'url', e.target.value)}
                            />
                          </div>
                        </div>

                        <div 
                          className={styles.dropzoneSmall}
                          onClick={() => document.getElementById(`file-${section.id}-${mediaItem.id}`).click()}
                        >
                          {mediaItem.file ? (
                            <div className={styles.fileSelected}>
                              <span>{mediaItem.file.name}</span>
                            </div>
                          ) : (
                            <p>Upload File</p>
                          )}
                          <input 
                            type="file" 
                            id={`file-${section.id}-${mediaItem.id}`}
                            style={{ display: 'none' }} 
                            accept={mediaItem.media_type === 'video' ? 'video/*' : 'image/*'}
                            onChange={(e) => handleMediaChange(section.id, mediaItem.id, 'file', e.target.files[0])}
                          />
                        </div>
                      </div>
                    ))}
                    
                    <button 
                      className={styles.addMediaBtn}
                      onClick={() => handleAddMedia(section.id)}
                    >
                      + Add More Media
                    </button>
                  </div>

                  <div className={styles.formGroup}>
                    <label className={styles.formLabel}>Description</label>
                    <textarea 
                      className={styles.formTextarea} 
                      placeholder="Context for this specific video..."
                      value={section.description}
                      onChange={(e) => handleSectionChange(section.id, 'description', e.target.value)}
                    ></textarea>
                  </div>
                </div>
              ))}

              <button 
                className={styles.addSectionBtn}
                onClick={handleAddMoreSection}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                <span>Add Section</span>
              </button>
            </div>

            <footer className={styles.modalFooter}>
              <button 
                className={styles.cancelBtn}
                onClick={() => setIsModalOpen(false)}
              >
                Cancel
              </button>
              <button className={styles.submitBtn} onClick={handleSubmit}>
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
