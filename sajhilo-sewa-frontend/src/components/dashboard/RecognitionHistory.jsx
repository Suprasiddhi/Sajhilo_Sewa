import React from 'react';
import styles from './RecognitionHistory.module.css';

const RecognitionHistory = () => {
  const history = [
    { id: 1, time: '2 minutes ago', english: 'Hello, how are you?', nepali: 'नमस्ते, तपाईं कस्तो हुनुहुन्छ?' },
    { id: 2, time: '5 minutes ago', english: 'I would like water please', nepali: 'मलाई पानी चाहिन्छ कृपया' },
    { id: 3, time: '8 minutes ago', english: 'Thank you very much', nepali: 'धेरै धेरै धन्यवाद' }
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Recognition History</h2>
        <button className={styles.clearAll}>Clear All</button>
      </div>

      <div className={styles.list}>
        {history.map((item) => (
          <div key={item.id} className={styles.card}>
            <div className={styles.timestamp}>{item.time}</div>
            <div className={styles.english}>{item.english}</div>
            <div className={styles.nepali}>{item.nepali}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecognitionHistory;
