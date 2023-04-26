import { useEffect } from 'react';
import Cookies from 'js-cookie';

function WorkerExample() {
  useEffect(() => {
    // Send a message to the worker every 5 seconds
    const intervalId = setInterval(() => {
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
      console.log(data)
    })
    .catch((error) => {
      if (error.message === "Failed to fetch") {
        alert("bruh");
      } else {
        alert("An error occured", error);
      }
    });
    }, 10000);

    // Clean up the worker and interval when the component unmounts
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div>
      <input type="text" placeholder="Search for a relaybox" />
      <ul>
        {console.log(relayboxData)}
        {relayboxData && Object.keys(relayboxData).map(relayboxName => (
          <li key={relayboxName}>
            <h3>{relayboxName}</h3>
            <ul>
              {Object.keys(relayboxData[relayboxName]).map(droneName => (
                <li key={droneName}>{droneName}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default WorkerExample;
