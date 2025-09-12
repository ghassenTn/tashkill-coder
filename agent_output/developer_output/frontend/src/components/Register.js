import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'; // For making API requests

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    password2: '',
  });

  const { name, email, password, password2 } = formData;

  const onChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    if (password !== password2) {
      alert('Passwords do not match');
    } else {
      try {
        const res = await axios.post('/api/auth/register', {
          name,
          email,
          password,
        }); // Adjust API endpoint as needed
        console.log(res.data); // Should log the token
        // TODO: Store token in localStorage and redirect user
        alert('Registration Successful! Token in console.');
      } catch (err) {
        console.error(err.response.data);
        alert('Registration Failed: ' + (err.response.data.msg || 'Server Error'));
      }
    }
  };

  return (
    <div className="auth-container">
      <h1>Sign Up</h1>
      <p>Create Your Account</p>
      <form onSubmit={onSubmit}>
        <div>
          <input
            type="text"
            placeholder="Name"
            name="name"
            value={name}
            onChange={onChange}
            required
          />
        </div>
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
        <div>
          <input
            type="password"
            placeholder="Confirm Password"
            name="password2"
            value={password2}
            onChange={onChange}
            minLength="6"
            required
          />
        </div>
        <input type="submit" value="Register" />
      </form>
      <p>
        Already have an account? <Link to="/login">Sign In</Link>
      </p>
    </div>
  );
};

export default Register;
