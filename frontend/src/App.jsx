import { useState } from 'react'
import reactLogo from './assets/react.svg'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import viteLogo from '/vite.svg'
import './App.css'
import StudyBuddy from './HomePage'
import Layout from './Layout';
import ChatPage from './ChatPage'

export default function App() {
    return (
        <BrowserRouter>
        <Routes>
            <Route path="/" element={<Layout />}>
            <Route index element={<StudyBuddy />} />
            <Route path="chat" element={<ChatPage />} />
            </Route>
        </Routes>
        </BrowserRouter>
        
    )
}


