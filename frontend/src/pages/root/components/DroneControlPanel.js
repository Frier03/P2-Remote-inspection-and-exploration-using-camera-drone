import { useEffect, useState, useRef } from "react";
import "./Navbar.css";
import droneTakeoff from "../utilities/keyboardlistener";
import "./DroneControlPanel.css";
import config from "../../../config.json";

function DroneControlPanel(props) {
  const [relay, drone] = props.connectDrone.split("-");
  const [showTakeoffBtn, setTakeoffBtn] = useState(true);
  const [showLandBtn, setLandBtn] = useState(false);
  const [frame, setFrame] = useState('');
  const socket = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      if (relay && drone && props.relayData[relay][drone] !== undefined) {
        if (props.relayData[relay][drone]["airborn"] === true) {
          setTakeoffBtn(false);
          setLandBtn(true);
        } else {
          setTakeoffBtn(true);
          setLandBtn(false);
        }
      }
    }, 100);

    socket.current = new WebSocket(`ws://${config.BASE_URL}/`);
    socket.current.onmessage = (event) => {
      setFrame(event.data);
    };

    return () => {
      clearInterval(interval);
      socket.current.close();
    }
  }, [relay, drone, props.relayData, setTakeoffBtn]);

  return (
    <>
      <div className="control-panel">
        <div className="video-feed-container">
          <video className="video-feed">
            <img src={`data:image/jpeg;base64,${frame}`} alt="Video Frame" />
          </video>
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
