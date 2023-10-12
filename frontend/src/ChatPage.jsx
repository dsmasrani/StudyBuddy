import React from 'react';
import './styles.css'

class ChatPage extends React.Component {
    render() {
        return (
            <div className="app-container">
            <header className="app-header">
                <h1>STUDY BUDDY</h1>
                <button className="logout-button">LOG OUT</button>
            </header>
            <section className="content-section">
                <div className="api-keys">
                <h2>API KEYS</h2>
                <input type="password" placeholder="enter password to view" />
                </div>
                <div className="setup-section">
                <h2>SETUP</h2>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit...</p>
                <div className="pagination-controls">
                    <button className="pagination-button">&lt;</button>
                    <span>1</span>
                    <button className="pagination-button">&gt;</button>
                </div>
                </div>
            </section>
            <div className="chatbox"></div>
            </div>
        );
    };
};

export default ChatPage;
