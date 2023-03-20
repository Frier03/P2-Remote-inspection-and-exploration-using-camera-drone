function handleLogin(){
    const username = document.getElementById("username").value
    const password = document.getElementById("password").value

    // send a POST request to backend
    fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username, 
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        
        if(data['detail'] === 'Incorrect username or password'){
            console.log(data['detail'])
            return
        }

        const access_token = data['access_token']
        const token_type = data['token_type']

        // Store access token in cookies
        document.cookie = 'access_token={0}'.format(access_token)
        console.log('Successfully logged in! Here is your token "' + access_token + '"')

    })
    .catch(error => {
        // handle any errors here
        console.error(error);
    })
}

const Login = () => {
    return (
    <>
    <label>Username </label>
    <input type="text" id="username"/>
    <label>Password </label>
    <input type="text" id="password"/>
    <button onClick={handleLogin}>Login here</button>
    </>
    );
  }
export default Login;
