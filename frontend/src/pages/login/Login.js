import React, { useState } from "react";
import Cookies from "js-cookie";
import "./Login.css";

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    fetch("http://localhost:8000/v1/api/frontend/login", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: username,
        password: password,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.access_token) {
          setToken(data.access_token);
          Cookies.set("access_token", data.access_token);
        } else {
          var msg = document.getElementById("msg");
          msg.innerHTML = "Invalid Username or Password";
          msg.style.display = "block";
        }
      })
      .catch((error) => {
        if (error.message === "Failed to fetch") {
          var msg = document.getElementById("msg");
          msg.innerHTML = "Server is offline";
          msg.style.display = "block";
        } else {
          alert("An error occured", error);
        }
      });
  }

  if (token) {
    window.location.href = "/";
  }

  return (
    <div className="animated bounceInDown">
      <div className="container">
        <span className="error animated tada" id="msg"></span>
        <form onSubmit={handleSubmit} className="box">
          <h4>
            Drone Pilot <span>Dashboard</span>
          </h4>
          <h5>Sign in to your account.</h5>
          <label>
            <input
              type="text"
              name="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Username"
              autoComplete="off"
            />
          </label>
          <i className="typcn typcn-eye" id="eye"></i>
          <label>
            <input
              type="password"
              name="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Password"
              id="pwd"
              autoComplete="off"
            />
          </label>
          <button type="submit" className="btn1">
            Sign in
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
