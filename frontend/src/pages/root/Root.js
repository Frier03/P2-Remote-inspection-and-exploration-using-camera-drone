import withAuthorization from "../../authzVerify";
import RelaysSidebar from "./components/RelaysSidebar";
import "./Root.css";

function RootForm({ authorizationStatus }) {
  if (authorizationStatus === "Authorized") {
    return (
      <>
        <div>
          <RelaysSidebar/>
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
