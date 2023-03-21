
function handleLogout(){
    // retrieve the JWT token from the cookie
    const access_token = document.cookie;

    // send a POST request to backend
    fetch('http://127.0.0.1:8000/api/auth/logout', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            access_token: access_token
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
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
