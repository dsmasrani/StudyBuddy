import React from 'react';


const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#f2f2f2',
    boxSizing: 'border-box'
  },
  title: {
    fontSize: '32px',
    marginBottom: '20px',
    paddingBottom: '40%'
  },
  card: {
    width: '100%',  
    maxWidth: '300px',
    padding: '20px',
    margin: '10px 0', 
    backgroundColor: '#b8e994',
    borderRadius: '8px',
    boxShadow: '0px 4px 8px rgba(0,0,0,0.2)',
    boxSizing: 'border-box'
  },
  input: {
    width: '100%',
    padding: '10px',
    margin: '5px 0',
    borderRadius: '8px',
    border: '1px solid #ccc',
    boxSizing: 'border-box' 
  }
};

class StudyBuddy extends React.Component {
  render() {
    return (
      <div>
        <h1 style={styles.title}>STUDY BUDDY</h1>
        
        <div style={styles.card}>
          <h2>SIGN IN</h2>
          <input type="email" placeholder="email" style={styles.input} />
          <input type="password" placeholder="password" style={styles.input} />
        </div>
        
        <div style={styles.card}>
          <h2>SIGN UP</h2>
          <input type="email" placeholder="email" style={styles.input} />
          <input type="password" placeholder="password" style={styles.input} />
        </div>
      </div>
    );
  }
}

export default StudyBuddy;
