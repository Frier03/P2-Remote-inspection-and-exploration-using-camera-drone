import { useState } from "react";
import withAuthorization from "../../authzVerify";
import Sidenav from "./components/Sidenav";
import Navbar from "./components/Navbar";
import DroneControlPanel from "./components/DroneControlPanel"
import "./Root.css";

function RootForm({ authorizationStatus }) {
  const [relayData, setRelayData] = useState('');
  const [username, setUsername] = useState('');
  const [connectDrone, setConnectDrone] = useState('');
  if (authorizationStatus === "Authorized") {
    return (
      <>
        <Navbar username={username} setUsername={setUsername} />
        <Sidenav connectDrone={connectDrone} setConnectDrone={setConnectDrone} relayData={relayData} setRelayData={setRelayData} />
        <DroneControlPanel relayData={relayData} connectDrone={connectDrone} />
      </>
    );
  }
}

const AuthorizedRootForm = withAuthorization(RootForm, "/login");
function RenderAuthorizedContent() {
  return (
    <>
      <AuthorizedRootForm />
    </>
  );
}

export default RenderAuthorizedContent;
