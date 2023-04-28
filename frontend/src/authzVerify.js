import React, { useEffect, useState } from 'react';
import Cookies from 'js-cookie';
import config from "./config.json"

async function validateToken() {
  return fetch(`http://${config.BASE_URL}/v1/api/frontend/protected`, {
    method: 'GET',
    headers: {
      'Authorization': `${Cookies.get('access_token')}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log(response)
    if(response.ok) {
      return true;
    } else {
      return false;
    }
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
    }, []); // <-- added empty dependency array here

    return <WrappedComponent authorizationStatus={authorizationStatus} {...props} />;
  };
}


export default withAuthorization;