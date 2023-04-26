import withAuthorization from "../../authzVerify";
import WorkerExample from "./WorkerExample";
import "./Root.css";


function RootForm({ authorizationStatus }) {
  // create a new worker and pass the worker script file as an argument
  var worker = new Worker("worker.js");
  // Start worker
  // worker gets data from backend every 10 sec
  // convert data into html
  if (authorizationStatus === "Authorized") {
    return (
      <>
            <div>
      <h1>Hello World</h1>
      <WorkerExample />
        </div>
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
