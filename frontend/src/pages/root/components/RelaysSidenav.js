import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import "./RelaysSidenav.css";
import "../utilities/keyboardlistener"

function RelaysSidenav() {
  const [relayData, setRelayData] = useState("");
  const [connectDrone, setConnectDrone] = useState("");
  
  useEffect(() => {
    fetchRelayData();
    const intervalId = setInterval(() => {
      fetchRelayData();
    }, 1000);

    // Clean up the worker and interval when the component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  function fetchRelayData() {
    console.log("fetching relay data");
    fetch("http://localhost:8000/v1/api/frontend/relayboxes/all", {
      method: "GET",
      headers: {
        Authorization: `${Cookies.get("access_token")}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setRelayData(data);
      });
  }

  function onClickConnectedbtn(key) {
    let relay = key.split('-')[0];
    let drone = key.split('-')[1];

    if(Cookies.get("relayName") == undefined && Cookies.get("droneName") == undefined){
      Cookies.set("relayName", relay);
      Cookies.set("droneName", drone);
      setConnectDrone(key);
    } else {
      Cookies.remove("relayName")
      Cookies.remove("droneName")
      setConnectDrone('');
    }

  }

  return (
    <>
      <div id="sidenav" className="sidenav">
        <ul>
          {console.log(relayData)}
          {relayData &&
            Object.keys(relayData).map((relayName) => (
              <li key={relayName}>
                <h3>{relayName}</h3>
                <ul>
                  {Object.keys(relayData[relayName]).map((droneName) => (
                    <li key={`${relayName}-${droneName}`}>
                      {droneName}
                      <button className="connect-btn" onClick={() => {onClickConnectedbtn(`${relayName}-${droneName}`)}}>
                      {connectDrone === `${relayName}-${droneName}` ? "Selected" : "Select"}</button>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
        </ul>
      </div>
    </>
  );
}

export default RelaysSidenav;
