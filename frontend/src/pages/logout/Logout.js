import React from 'react';
import Cookies from 'js-cookie';
import withAuthorization from "../../HOC";

function LogoutForm({ authorizationStatus }) {
  if (authorizationStatus === "Authorized") {
    return (
      <form onSubmit={handleLogout}>
        <h1>Authorized</h1>
        <button type="submit">Logout</button>
      </form>
    );
  }

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

            window.location.href = "/login" // redirect to "/login"
        }
    })
    .catch(error => {
        if (error.message === 'Failed to fetch') {
            alert('Failed to fetch API')
        } else {
            alert('An error occured')
        }
    })
  }
}

const AuthorizedLogoutForm = withAuthorization(LogoutForm, "/login");

function RenderAuthorizedContent() {
  return (
    <>
      <AuthorizedLogoutForm />
    </>
  );
}

export default RenderAuthorizedContent;
