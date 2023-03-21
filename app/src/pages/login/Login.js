import Cookies from 'js-cookie'; //npm install js-cookie --save

function handleLogin(){
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const token = document.cookie;

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
    .then(response => response.json())
    .then(data => {
        if(data['detail'] === 'Incorrect username or password'){
            console.log(data['detail'])
            return
        }
        const access_token = data['access_token'];

        console.log('Successfully logged in! Here is your token "' + access_token + '"');
        console.log('Storing your token...');
        document.cookie = 'access_token='+access_token;
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
