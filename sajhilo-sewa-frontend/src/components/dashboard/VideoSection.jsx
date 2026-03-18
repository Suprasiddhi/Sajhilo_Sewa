import styles from "./VideoSection.module.css";

function VideoSection() {
  return (
    <div className={styles.videoCard}>
      <div className={styles.cardHeader}>
        <h2>Camera Feed</h2>
      </div>
    </div>
  );
}

export default VideoSection;
