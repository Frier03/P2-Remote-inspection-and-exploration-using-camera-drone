import React, { useEffect, useState } from 'react';
import Cookies from 'js-cookie';

function validateToken() {
  return fetch('http://127.0.0.1:8000/v1/auth/protected', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${Cookies.get('access_token')}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.message === "OK") {
      return true;
    } else {
      return false;
    }
  })
  .catch(error => {
    if (error.message === 'Failed to fetch') {
      alert('API is offline')
    } else {
      alert('An error occured')
    }
    return false;
  });
}

function withAuthorization(WrappedComponent, unauthorizedRedirect) {
  return function(props) {
    const [authorizationStatus, setAuthorizationStatus] = useState("Not Authorized");

    useEffect(() => {
      const token = Cookies.get('access_token');
      if (token) {
        validateToken()
          .then(isAuthorized => {
            if (isAuthorized) {
              setAuthorizationStatus("Authorized");
            } else {
              window.location.href = unauthorizedRedirect;
            }
          })
          .catch(error => console.error(error));
      } else {
        window.location.href = unauthorizedRedirect;
      }
    });

    return <WrappedComponent authorizationStatus={authorizationStatus} {...props} />;
  };
}

export default withAuthorization;