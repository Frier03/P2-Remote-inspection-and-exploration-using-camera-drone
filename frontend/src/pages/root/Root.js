import withAuthorization from "../../HOC";

function RootForm({ authorizationStatus }) {
  if (authorizationStatus === "Authorized") {
    return (
      <>
        <h1>Authorized</h1>
      </>
    );
  } else {
    return null;
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