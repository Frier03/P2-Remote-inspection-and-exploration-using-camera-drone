import { useEffect, useState } from "react";
import "./Navbar.css";
import Cookies from "js-cookie";

function Navbar() {
  const [username, setUsername] = useState("");

  useEffect(() => {
    fetchUsername();
  }, []);

  function fetchUsername() {
    console.log("fetching username");
    fetch("http://localhost:8000/v1/api/frontend/users/me", {
      method: "GET",
      headers: {
        Authorization: `${Cookies.get("access_token")}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setUsername(data.message);
        console.log(data);
      });
  }

  return (
    <>
      <div className="navbar-top">
        <div className="flexsdisplay-top">
          <div className="navbar-username">
            <h3>Hello {username}!</h3>
          </div>
          <div className="search-box">search test</div>
          <div className="navbar-logout">
            <a href="/logout">Log out</a>
          </div>
        </div>
      </div>
    </>
  );
}

export default Navbar;
