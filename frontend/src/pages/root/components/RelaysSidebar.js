import { useEffect, useState } from 'react';
import Cookies from 'js-cookie';

function RelaysSidebar() {
  const [relayData, setRelayData] = useState("");
  useEffect(() => {
    fetchRelayData()
    const intervalId = setInterval(() => {
      fetchRelayData()
    }, 1000);

    // Clean up the worker and interval when the component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  function fetchRelayData(){
    console.log("fetching")
    fetch("http://localhost:8000/v1/api/frontend/relayboxes/all", {
    method: "GET",
    headers: {
      'Authorization': `${Cookies.get('access_token')}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
    .then((response) => response.json())
    .then((data) => {
      setRelayData(data)
    })
  }

  return (
    <div>
      <input type="text" placeholder="Search for a relaybox" />
      <ul>
        {console.log(relayData)}
        {relayData && Object.keys(relayData).map(relayName => (
          <li key={relayName}>
            <h3>{relayName}</h3>
            <ul>
              {Object.keys(relayData[relayName]).map(droneName => (
                <li key={droneName}>{droneName}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default RelaysSidebar;
