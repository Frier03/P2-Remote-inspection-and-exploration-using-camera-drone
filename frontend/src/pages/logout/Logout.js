import React, { useEffect } from 'react';
import Cookies from 'js-cookie';
import withAuthorization from "../../authzVerify";
import config from "../../config.json"

function LogoutForm({ authorizationStatus }) {
  useEffect(() => {
    Cookies.remove('relayName')
    Cookies.remove('droneName')
    handleLogout();
  }, []);
  if(authorizationStatus === "Authorized"){
    return (
      <h1>Logging out...</h1>
    );
  }

  function handleLogout() {
  return fetch(`http://${config.BASE_URL}/v1/api/frontend/logout`, {
    method: 'GET',
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
