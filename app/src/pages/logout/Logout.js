import React, { useState } from 'react';
import Cookies from 'js-cookie';

function LogoutForm( {token} ) {

  function handleLogout(event) {
    event.preventDefault();

    fetch('http://127.0.0.1:8000/v1/auth/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${Cookies.get('access_token')}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.message === "OK"){
            //Cookies.set('access_token', 'NULL') # Since backend adds token to a blacklist, we do not need this
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

  return (
    <form onSubmit={handleLogout}>
      <label>
        Logout
        <button type="submit">Logout</button>
      </label>
    </form>
  );
}
export default LogoutForm;
