import withAuthorization from "../../authzVerify";
import Cookies from 'js-cookie';
import './Root.css';

function RootForm({ authorizationStatus }) {
  const getAllRelayboxes = () => {
    return fetch('http://127.0.0.1:8000/v1/api/frontend/relayboxes/all', {
    method: 'GET',
    headers: {
      'Authorization': `${Cookies.get('access_token')}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => {
    if (error.message === 'Failed to fetch') {
      alert('API is offline')
    } else {
      alert(error)
    }
    return false;
  });
  }
  const handleLogout = () => {
    window.location.href = '/logout';
  };
  if (authorizationStatus === "Authorized") {
    getAllRelayboxes()
    return (
      <>
        <h1>Authorized</h1>
        <button onClick={handleLogout}>
        Logout
        </button>
      </>
    );
  }
}


const AuthorizedRootForm = withAuthorization(RootForm, "/login");
function RenderAuthorizedContent() {
  return (
    <>
      <AuthorizedRootForm />
    </>
  );
}

export default RenderAuthorizedContent;