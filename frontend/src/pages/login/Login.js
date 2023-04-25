import React, { useState } from 'react';
import Cookies from 'js-cookie';

function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState('');

  // everything inside of the LoginForm() and outside of the handleSubmit will run whenever a user refreshes or uses the url. This means we can implement authorization here.

  function handleSubmit(event) {
    event.preventDefault();

    fetch('http://localhost:8000/v1/api/frontend/login', {
        method: 'POST',
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: username, 
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            console.log(data)
            setToken(data.access_token);
            Cookies.set('access_token', data.access_token)
        } else {
            alert('Invalid credentials');
        }
    })
    .catch(error => {
        if (error.message === 'Failed to fetch') {
            alert('API is offline')
        } else {
            alert('An error occured')
        }
    })
  }
  if (token) {
    // Redirect to the protected route
    window.location.href = '/'
  }

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Username:
        <input type="text" value={username} onChange={event => setUsername(event.target.value)} />
      </label>
      <label>
        Password:
        <input type="password" value={password} onChange={event => setPassword(event.target.value)} />
      </label>
      <button type="submit">Login</button>
    </form>
  );
}

export default LoginForm;
