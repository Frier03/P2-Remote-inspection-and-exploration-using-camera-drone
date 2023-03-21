import trimAccessToken from '../../helperFunctions'

function handleLogout(){
    // retrieve the JWT token from the cookie
    let token = document.cookie;
    token = trimAccessToken(token)
 
    // send a POST request to backend
    fetch('http://127.0.0.1:8000/v1/auth/logout', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then(res => Promise.all([res.status, res.json()]))
    .then(([status, data]) => {
        // Make proper logic here
        console.log(status, data)
    })
    .catch(error => {
        // handle any errors here
        console.error(error);
    })
}

const Logout = () => {
    return (
    <>
    <h1>Logout</h1>
    <button onClick={handleLogout}>Logout</button>
    </>
    );
  }
export default Logout;
