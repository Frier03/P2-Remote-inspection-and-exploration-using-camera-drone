import { useEffect, useState } from "react";
import "./Navbar.css";
import droneTakeoff from "../utilities/keyboardlistener";
import "./DroneControlPanel.css";

function DroneControlPanel(props) {
  const [relay, drone] = props.connectDrone.split("-");
  const [showTakeoffBtn, setTakeoffBtn] = useState(true);
  const [showLandBtn, setLandBtn] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      if (relay && drone) {
        if (props.relayData[relay][drone]["airborn"] === true) {
          setTakeoffBtn(false);
          setLandBtn(true);
        } else {
          setTakeoffBtn(true);
          setLandBtn(false);
        }
      }
    }, 100);

    return () => clearInterval(interval);
  }, [relay, drone, props.relayData, setTakeoffBtn]);

  return (
    <>
      <div className="control-panel">
        <div className="video-feed-container">
          <video className="video-feed"></video>
        </div>
        <div className="controls-container">
          <div className="btn-container">
            {showTakeoffBtn && (
              <>
                <button className="takeoff-btn" onClick={() => droneTakeoff()}>
                  Take Off
                </button>
                <p className="takeoff"></p>
              </>
            )}
          </div>
          <div className="btn-container">
            {showLandBtn && (
              <>
                <button className="land-btn">Land</button>
                <p className="land"></p>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default DroneControlPanel;
