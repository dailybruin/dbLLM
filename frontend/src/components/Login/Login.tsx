import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../../Context/useAuth";

const Login: React.FC = () => {
  const { loginUser } = useAuth();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-evenly",
        alignItems: "center",
        height: "100vh",
      }}
    >
      <h1>Please Sign In</h1>

      <GoogleLogin
        onSuccess={(credentialResponse) => {
          if (credentialResponse.credential) {
            loginUser(credentialResponse.credential);
          }
        }}
        onError={() => console.error("Login failed")}
        auto_select={true}
        theme="filled_blue"
      />

      <div>
        <h4>Oliver Bot is currently under beta testing</h4>
        <h4>Full public access coming soon :)</h4>
      </div>
    </div>
  );
};

export default Login;
