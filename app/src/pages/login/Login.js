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
        if (data.error != undefined){
            console.log(data.error)
            return
        }
        // store the token in a cookie named "auth_token". It should also expire in 1 hour.
        const now = new Date();
        const time = now.getTime();
        const expirationTime = time + 60 * 60 * 1000; // 1 hour from now
        now.setTime(expirationTime);
        document.cookie = `auth_token=${data.token};expires=${now.toUTCString()};path=/`;
        

        console.log(document.cookie)
        console.log("Successfully logged in")
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
