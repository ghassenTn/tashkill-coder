import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'; // For making API requests

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const { email, password } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/auth/login', formData); // Adjust API endpoint as needed
      console.log(res.data); // Should log the token
      // TODO: Store token in localStorage and redirect user
      alert('Login Successful! Token in console.');
    } catch (err) {
      console.error(err.response.data);
      alert('Login Failed: ' + (err.response.data.msg || 'Server Error'));
    }
  };

  return (
    <div className="auth-container">
      <h1>Sign In</h1>
      <p>Sign Into Your Account</p>
      <form onSubmit={onSubmit}>
        <div>
          <input
            type="email"
            placeholder="Email Address"
            name="email"
            value={email}
            onChange={onChange}
            required
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            name="password"
            value={password}
            onChange={onChange}
            minLength="6"
            required
          />
        </div>
        <input type="submit" value="Login" />
      </form>
      <p>
        Don't have an account? <Link to="/register">Sign Up</Link>
      </p>
      <p>
        <Link to="/forgot-password">Forgot Password?</Link>
      </p>
    </div>
  );
};

export default Login;
