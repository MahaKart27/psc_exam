import React, { useState } from 'react';
import './App.css';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showLogin, setShowLogin] = useState(true);

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/login', { // Updated URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage(`You have logged in as ${data.role}.`);
        if (data.role === 'student') {
          window.location.href = '/student-dashboard';
        } else if (data.role === 'teacher') {
          window.location.href = '/teacher-dashboard';
        }
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while logging in.');
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/signup', { // Updated URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password, role }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage('Signup successful. Please login.');
        setShowLogin(true);
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while signing up.');
    }
  };

  return (
    <div className="App">
      <div className="form-container">
        <div className="form">
          <h2>{showLogin ? 'Login' : 'Signup'}</h2>
          {message && <p className="message">{message}</p>}
          {error && <p className="error">{error}</p>}
          {showLogin ? (
            <form onSubmit={handleLogin}>
              <div className="input-group">
                <label>Username:</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label>Password:</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit">Login</button>
              <button type="button" onClick={() => setShowLogin(false)}>
                Register
              </button>
            </form>
          ) : (
            <form onSubmit={handleSignup}>
              <div className="input-group">
                <label>Username:</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label>Password:</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className="input-group">
                <label>Role:</label>
                <select onChange={(e) => setRole(e.target.value)}>
                  <option value="student">Student</option>
                  <option value="teacher">Teacher</option>
                </select>
              </div>
              <button type="submit">Signup</button>
              <button type="button" onClick={() => setShowLogin(true)}>
                Back to Login
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
