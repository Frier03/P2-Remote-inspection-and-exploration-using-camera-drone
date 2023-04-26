import React, { useEffect } from 'react';
import Cookies from 'js-cookie';
import withAuthorization from "../../HOC";

function LogoutForm({ authorizationStatus }) {
  useEffect(() => {
    handleLogout();
  }, []);
  if(authorizationStatus === "Authorized"){
    return (
      <h1>Logging out...</h1>
    );
  }

  function handleLogout() {
  return fetch('http://127.0.0.1:8000/v1/api/frontend/protected', {
    method: 'POST',
    headers: {
      'Authorization': `${Cookies.get('access_token')}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log(response)
    window.location.href = '/login'
    })
  .catch(error => {
    if (error.message === 'Failed to fetch') {
      alert('API is offline')
    } else {
      alert(error)
    }
    return false;
  });
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
