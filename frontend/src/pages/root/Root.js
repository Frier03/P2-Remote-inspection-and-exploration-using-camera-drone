import withAuthorization from "../../HOC";

function RootForm({ authorizationStatus }) {
  const handleLogout = () => {
    window.location.href = '/logout';
  };
  if (authorizationStatus === "Authorized") {
    return (
      <>
        <h1>Authorized</h1>
        <button onClick={handleLogout}>
        Logout
        </button>
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