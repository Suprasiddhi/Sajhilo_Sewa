import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styles from './AdminDashboard.module.css';

// Sub-components
import AdminDashboardUsers from './AdminDashboardUsers';
import AdminDashboardGesture from './AdminDashboardGesture';
import AdminDashboardHistory from './AdminDashboardHistory';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('overview');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [stats, setStats] = useState({
    total_users: 0,
    all_usernames: [],
    total_gestures: 0,
    latest_gestures: []
  });
  const [allGestures, setAllGestures] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [currentEditId, setCurrentEditId] = useState(null);
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
    if (activeSection === 'gestures') {
      fetchAllGestures(selectedCategory);
    } else if (activeSection === 'users') {
      fetchAllUsers();
    }
  }, [selectedCategory, activeSection]);

  const fetchAllGestures = async (category = 'all') => {
    try {
      setLoading(true);
      const categoryParam = category === 'all' ? 'all' : category.toLowerCase();
      const res = await fetch(`http://localhost:8000/gestures/?category=${categoryParam}`);
      if (res.ok) {
        const data = await res.json();
        setAllGestures(data);
      }
    } catch (err) {
      console.error("Error fetching gestures:", err);
    } finally {
      setLoading(false);
    }
  };

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

  const fetchAllUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/admin/users/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAllUsers(data);
      }
    } catch (err) {
      console.error("Error fetching users:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm("Are you sure you want to delete this user? This action cannot be undone.")) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/admin/users/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        fetchAllUsers();
        fetchStats();
      }
    } catch (err) {
      console.error("Error deleting user:", err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  const handleProcessVideos = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/api/ml/process-videos', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      alert(data.message || "Video processing started in background.");
    } catch (err) {
      alert("Failed to start processing: " + err.message);
    }
  };

  const handleRetrain = async () => {
    if (!window.confirm("Full training takes 10-30 min. Continue?")) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/api/ml/train', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      alert(data.message || "Training started in background.");
    } catch (err) {
      alert("Failed to start training: " + err.message);
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

  const handleEditClick = (gesture) => {
    setGestureData({
      name: gesture.name,
      category: gesture.category,
      sections: gesture.sections.map(s => ({
        ...s,
        id: s.id,
        media: s.media.map(m => ({ ...m, file: null }))
      }))
    });
    setIsEditing(true);
    setCurrentEditId(gesture.id);
    setIsModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this gesture?")) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/gestures/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        fetchStats();
        fetchAllGestures(selectedCategory);
      }
    } catch (err) {
      console.error("Error deleting gesture:", err);
    }
  };

  const handleSubmit = async () => {
    try {
      const updatedSections = await Promise.all(gestureData.sections.map(async (section) => {
        const updatedMedia = await Promise.all(section.media.map(async (mediaItem) => {
          if (mediaItem.file) {
            const formData = new FormData();
            formData.append('file', mediaItem.file);
            const res = await fetch('http://localhost:8000/gestures/upload', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              },
              body: formData
            });
            const data = await res.json();
            return { ...mediaItem, url: data.url };
          }
          return mediaItem;
        }));
        return { ...section, media: updatedMedia };
      }));

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

      const url = isEditing 
        ? `http://localhost:8000/gestures/${currentEditId}`
        : 'http://localhost:8000/gestures/';
      
      const res = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(finalGesture)
      });

      if (res.status === 401) {
        alert("Session expired or unauthorized. Please log out and back in.");
        return;
      }

      if (res.ok) {
        setIsModalOpen(false);
        fetchStats();
        fetchAllGestures(selectedCategory);
      } else {
        alert("Failed to add gesture");
      }
    } catch (err) {
      console.error("Error submitting gesture:", err);
      alert("Error submitting gesture");
    }
  };

  const navigationItems = [
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
      id: 'users', 
      label: 'Users',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
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
        <div className={styles.topBarRight}>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      <div className={styles.container}>
        <aside className={styles.subSidebar}>
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`${styles.navButton} ${activeSection === item.id ? styles.active : ''}`}
              onClick={() => setActiveSection(item.id)}
            >
              {item.icon}
              <span>{item.label}</span>
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

              <div className={styles.systemGrid}>
                <div className={styles.systemCard}>
                  <div className={styles.cardHeaderSmall}>
                    <h3 className={styles.cardTitle}>ML System Management</h3>
                    <div className={styles.systemBadge}>Ready</div>
                  </div>
                  <div className={styles.systemButtons}>
                    <button onClick={handleProcessVideos} className={styles.processBtn}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                      <span>Process Videos</span>
                    </button>
                    <button onClick={handleRetrain} className={styles.retrainBtn}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21.5 2v6h-6M2.5 22v-6h6M2 12c0-4.4 3.6-8 8-8 3.3 0 6.2 2 7.4 5M22 12c0 4.4-3.6 8-8 8-3.3 0-6.2-2-7.4-5" />
                      </svg>
                      <span>Retrain Model</span>
                    </button>
                  </div>
                  <p className={styles.systemNote}>
                    * Run "Process Videos" first if you have uploaded new gestures.
                  </p>
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

          {activeSection === 'users' && (
            <AdminDashboardUsers 
              allUsers={allUsers} 
              loading={loading} 
              handleDeleteUser={handleDeleteUser} 
            />
          )}

          {activeSection === 'gestures' && (
            <AdminDashboardGesture 
              allGestures={allGestures}
              loading={loading}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              handleEditClick={handleEditClick}
              handleDelete={handleDelete}
              setIsModalOpen={setIsModalOpen}
              setGestureData={setGestureData}
              setIsEditing={setIsEditing}
              setCurrentEditId={setCurrentEditId}
              isModalOpen={isModalOpen}
              isEditing={isEditing}
              gestureData={gestureData}
              handleRemoveSection={handleRemoveSection}
              handleSectionChange={handleSectionChange}
              handleRemoveMedia={handleRemoveMedia}
              handleMediaChange={handleMediaChange}
              handleAddMedia={handleAddMedia}
              handleAddMoreSection={handleAddMoreSection}
              handleSubmit={handleSubmit}
            />
          )}

          {activeSection === 'history' && <AdminDashboardHistory />}
        </main>
      </div>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <header className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>{isEditing ? 'Edit Gesture' : 'Add New Gesture'}</h2>
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
                {isEditing ? 'Save Changes' : 'Add Gesture'}
              </button>
            </footer>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
