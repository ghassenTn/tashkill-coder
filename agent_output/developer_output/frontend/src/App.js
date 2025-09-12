import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Advanced To-Do App</h1>
        </header>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          {/* A temporary home page or redirect for now */}
          <Route path="/" element={<h2>Welcome! Please Login or Register</h2>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
