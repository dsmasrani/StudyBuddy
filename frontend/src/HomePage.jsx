import React from 'react';
import auth from './auth.js';
import UserContext from './UserContext';


const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '50vh',
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
    padding: '10px',
    margin: '10px 0', 
    backgroundColor: '#b8e994',
    borderRadius: '8px',
    boxShadow: '0px 4px 8px rgba(0,0,0,0.2)',
    boxSizing: 'border-box'
  },
};

class StudyBuddy extends React.Component {
  static contextType = UserContext;
  handleGoogleSignIn = async () => {
    const { user, error } = await auth.signInWithGoogle();
    if (error) {
      console.error('Error signing in:', error);
    } else {
      console.log('Signed in as:', user.email);
    }
    if (!error && user) {
      this.context.setUser(user); 
      this.props.history.push('/chat'); 
    }
  };

  render() {
    return (
      <div style={styles.container}>
        <img src='/src/assets/StuddyBuddyLogo.png'/>

        <div style={styles.card}>
          <button style={styles.button} onClick={this.handleGoogleSignIn}>
            Sign in with Google
          </button>
        </div>  

      </div>
    );
  }
}

export default StudyBuddy;
