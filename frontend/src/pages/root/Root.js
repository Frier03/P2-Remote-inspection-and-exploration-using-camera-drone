import withAuthorization from "../../authzVerify";
import RelaysSidenav from "./components/RelaysSidenav";
import Navbar from "./components/Navbar"
import "./Root.css";

function RootForm({ authorizationStatus }) {
  if (authorizationStatus === "Authorized") {
    return (
      <>
          <Navbar />
          <RelaysSidenav />
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
