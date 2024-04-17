// import React, { useState } from 'react';
// import './App.css';

// function App() {
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');
//   const [role, setRole] = useState('student');
//   const [message, setMessage] = useState('');
//   const [error, setError] = useState('');
//   const [showLogin, setShowLogin] = useState(true);
//   const [courseName, setCourseName] = useState('');
//   const [courses, setCourses] = useState([]);

//   // Dummy session data
//   const session = {
//     role: 'student', // Replace with your actual session data
//   };

//   const handleLogin = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await fetch('http://localhost:5000/login', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ username, password }),
//       });

//       const data = await response.json();

//       if (data.success) {
//         setMessage(`You have logged in as ${data.role}.`);
//         if (data.role === 'student') {
//           window.location.href = '/student-dashboard';
//         } else if (data.role === 'teacher') {
//           window.location.href = '/teacher-dashboard';
//         }
//       } else {
//         setError(data.message);
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       setError('An error occurred while logging in.');
//     }
//   };

//   const handleSignup = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await fetch('http://localhost:5000/signup', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ username, password, role }),
//       });

//       const data = await response.json();

//       if (data.success) {
//         setMessage('Signup successful. Please login.');
//         setShowLogin(true);
//       } else {
//         setError(data.message);
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       setError('An error occurred while signing up.');
//     }
//   };

//   const handleCreateCourse = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await fetch('http://localhost:5000/create-course', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ course_name: courseName }),
//       });

//       const data = await response.json();

//       if (data.success) {
//         setMessage(data.message);
//       } else {
//         setError(data.message);
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       setError('An error occurred while creating the course.');
//     }
//   };

//   const handleEnrollCourse = async () => {
//     // Fetch courseId from somewhere or pass it as an argument
//     const courseId = 1; // Replace with the actual courseId

//     try {
//       const response = await fetch('http://localhost:5000/enroll-course', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ course_id: courseId }),
//       });

//       const data = await response.json();

//       if (data.success) {
//         setMessage(data.message);
//       } else {
//         setError(data.message);
//       }
//     } catch (error) {
//       console.error('Error:', error);
//       setError('An error occurred while enrolling in the course.');
//     }
//   };

//   return (
//     <div className="App">
//       <div className="form-container">
//         <div className="form">
//           <h2>{showLogin ? 'Login' : 'Signup'}</h2>
//           {message && <p className="message">{message}</p>}
//           {error && <p className="error">{error}</p>}
//             {showLogin ? (
//               <form onSubmit={handleLogin}>
//                 <div className="input-group">
//                   <label>Username:</label>
//                   <input
//                     type="text"
//                     value={username}
//                     onChange={(e) => setUsername(e.target.value)}
//                     required
//                   />
//                 </div>
//                 <div className="input-group">
//                   <label>Password:</label>
//                   <input
//                     type="password"
//                     value={password}
//                     onChange={(e) => setPassword(e.target.value)}
//                     required
//                   />
//                 </div>
//                 <button type="submit">Login</button>
//                 <button type="button" onClick={() => setShowLogin(false)}>
//                   Register
//                 </button>
//               </form>
//             ) : (
//               <form onSubmit={handleSignup}>
//                 <div className="input-group">
//                   <label>Username:</label>
//                   <input
//                     type="text"
//                     value={username}
//                     onChange={(e) => setUsername(e.target.value)}
//                     required
//                   />
//                 </div>
//                 <div className="input-group">
//                   <label>Password:</label>
//                   <input
//                     type="password"
//                     value={password}
//                     onChange={(e) => setPassword(e.target.value)}
//                     required
//                   />
//                 </div>
//                 <div className="input-group">
//                   <label>Role:</label>
//                   <select onChange={(e) => setRole(e.target.value)}>
//                     <option value="student">Student</option>
//                     <option value="teacher">Teacher</option>
//                   </select>
//                 </div>
//                 <button type="submit">Signup</button>
//                 <button type="button" onClick={() => setShowLogin(true)}>
//                   Back to Login
//                 </button>
//               </form>
//             )}

//             {session.role === 'teacher' && (
//               <div>
//                 <input
//                   type="text"
//                   placeholder="Enter course name"
//                   value={courseName}
//                   onChange={(e) => setCourseName(e.target.value)}
//                 />
//                 <button onClick={handleCreateCourse}>Create Course</button>
//               </div>
//             )}
//             {session.role === 'student' && (
//               <button onClick={handleEnrollCourse}>Enroll in Course</button>
//             )}
//           </div>
//       </div>
//     </div>
//   );
// }

// export default App;
import React, { useState, useEffect } from 'react';
import './App.css'
import {
  BrowserRouter as Router,
  Route,
  Routes, // Replace Switch with Routes
  Navigate, // Replace Redirect with Navigate
} from 'react-router-dom';





function LoginForm({ handleLogin, setShowLogin, setUsername, setPassword }) {
  return (
    <form onSubmit={handleLogin}>
      <div className="input-group">
        <label>Username:</label>
        <input
          type="text"
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div className="input-group">
        <label>Password:</label>
        <input
          type="password"
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Login</button>
      <button type="button" onClick={() => setShowLogin(false)}>
        Register
      </button>
    </form>
  );
}

function SignupForm({ handleSignup, setShowLogin, setUsername, setPassword }) {
  return (
    <form onSubmit={handleSignup}>
      <div className="input-group">
        <label>Username:</label>
        <input
          type="text"
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      <div className="input-group">
        <label>Password:</label>
        <input
          type="password"
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Signup</button>
      <button type="button" onClick={() => setShowLogin(true)}>
        Back to Login
      </button>
    </form>
  );
}

function TeacherDashboard({ handleCreateCourse, setCourseName, setCourseDescription }) {
  return (
    <div>
      <h2>Create Course</h2>
      <form onSubmit={handleCreateCourse}>
        <div className="input-group">
          <label>Course Name:</label>
          <input
            type="text"
            onChange={(e) => setCourseName(e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label>Course Description:</label>
          <textarea
            onChange={(e) => setCourseDescription(e.target.value)}
            required
          ></textarea>
        </div>
        <button type="submit">Create Course</button>
      </form>
    </div>
  );
}

function StudentDashboard({ courses, handleEnrollCourse }) {
  return (
    <div>
      <h2>Available Courses</h2>
      <ul>
        {courses.map((course) => (
          <li key={course.id}>
            <strong>{course.course_name}</strong>: {course.course_description}
            <button onClick={() => handleEnrollCourse(course.id)}>Enroll</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('student');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showLogin, setShowLogin] = useState(true);
  const [courseName, setCourseName] = useState('');
  const [courseDescription, setCourseDescription] = useState('');
  const [courses, setCourses] = useState([]);

  const session = {
    role: 'student', // Placeholder for session data
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/login', {
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
      const response = await fetch('http://localhost:5000/signup', {
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

  const handleCreateCourse = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch('http://localhost:5000/create-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ course_name: courseName, course_description: courseDescription }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage(data.message);
        setCourseName('');
        setCourseDescription('');
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while creating the course.');
    }
  };

  const handleEnrollCourse = async (courseId) => {
    try {
      const response = await fetch('http://localhost:5000/enroll-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ course_id: courseId }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage(data.message);
      } else {
        setError(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('An error occurred while enrolling in the course.');
    }
  };

  useEffect(() => {
    async function fetchCourses() {
      try {
        const response = await fetch('http://localhost:5000/courses');
        const data = await response.json();
        setCourses(data);
      } catch (error) {
        console.error('Error:', error);
      }
    }
    fetchCourses();
  }, []);

  return (
    <Router>
      <div className="App">
        <div className="form-container">
          <Routes>
            <Route path="/login" element={
              <LoginForm
                handleLogin={handleLogin}
                setShowLogin={setShowLogin}
                setUsername={setUsername}
                setPassword={setPassword}
              />
            } />
            <Route path="/signup" element={
              <SignupForm
                handleSignup={handleSignup}
                setShowLogin={setShowLogin}
                setUsername={setUsername}
                setPassword={setPassword}
              />
            } />
            <Route path="/teacher-dashboard" element={
              <TeacherDashboard
                handleCreateCourse={handleCreateCourse}
                setCourseName={setCourseName}
                setCourseDescription={setCourseDescription}
              />
            } />
            <Route path="/student-dashboard" element={
              <StudentDashboard courses={courses} handleEnrollCourse={handleEnrollCourse} />
            } />
            <Route path="/" element={<Navigate to="/login" />} /> {/* Default redirect */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}


export default App;
