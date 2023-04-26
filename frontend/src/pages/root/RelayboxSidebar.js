import { useState, useEffect } from 'react';

function RelayboxSidebar() {
  const [relayboxData, setRelayboxData] = useState('');
  const [worker, setWorker] = useState('');

  useEffect(() => {
    // Create a new worker and store it in the state variable
    const newWorker = new Worker('workerThread.js');
    setWorker(newWorker);

    // Send a message to the worker to start getting relaybox data
    newWorker.postMessage('start');

    // Receive messages from the worker and update the state variable
    newWorker.onmessage = function (event) {
      setRelayboxData(event.data);
    }

    // Clean up the worker when the component unmounts
    return () => {
      newWorker.terminate();
      setWorker(null);
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
  );
}

export default RelayboxSidebar;
