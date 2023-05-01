import { useEffect } from "react";
import Cookies from "js-cookie";
import "./Sidenav.css";
import "../utilities/keyboardlistener";
import config from "../../../config.json"

function Sidenav(props) {

  useEffect(() => {
    fetchRelayData();
    const intervalId = setInterval(() => {
      fetchRelayData();
    }, 1000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  function fetchRelayData() {
    console.log("fetching relay data");
    fetch(`http://${config.BASE_URL}/v1/api/frontend/relayboxes/all`, {
      method: "GET",
      headers: {
        Authorization: `${Cookies.get("access_token")}`,
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        props.setRelayData(data);
      });
  }

  function onClickConnectedbtn(key) {
    const [relay, drone] = key.split("-")

    if(Cookies.get("relayName") === undefined && Cookies.get("droneName") === undefined){
      Cookies.set("relayName", relay);
      Cookies.set("droneName", drone);
      props.setConnectDrone(key);
    } else {
      Cookies.remove("relayName")
      Cookies.remove("droneName")
      props.setConnectDrone('');
    }

  }

  return (
    <>
      <div id="sidenav" className="sidenav">
        <ul>
          {props.relayData && Object.keys(props.relayData).map((relayName) => (
              <li key={relayName}>
                <h3>{relayName}</h3>
                <ul>
                  {Object.keys(props.relayData[relayName]).map((droneName) => (
                    <li key={`${relayName}-${droneName}`}>
                      {droneName}
                      <button className="connect-btn" onClick={() => {onClickConnectedbtn(`${relayName}-${droneName}`)}}>
                      {props.connectDrone === `${relayName}-${droneName}` ? "Selected" : "Select"}</button>
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

export default Sidenav;