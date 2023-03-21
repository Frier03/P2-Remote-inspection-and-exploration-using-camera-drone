import trimAccessToken from '../../helperFunctions'

function handleLogin(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    let token = document.cookie;
    token = trimAccessToken(token);

    // send a POST request to backend
    fetch('http://127.0.0.1:8000/v1/auth/login', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username, 
            password: password,
            access_token: token
        })
    })
    .then(res => Promise.all([res.status, res.json()]))
    .then(([status, data]) => {
        // Make proper logic here
        console.log(status, data)
        const access_token = data['access_token'];
        document.cookie = 'access_token='+access_token+";";
    })
    .catch(error => {
        // handle any errors here
        console.error(error);
    })
}

const Login = () => {
    return (
    <>
    <h1>Login</h1>
    <label>Username </label>
    <input type="text" id="username"/>
    <label>Password </label>
    <input type="text" id="password"/>
    <button onClick={handleLogin}>Login here</button>
    </>
    );
  }
export default Login;
