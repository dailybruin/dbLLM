import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../../Context/useAuth";

const Login: React.FC = () => {
  const { loginUser } = useAuth();

  return (
    <GoogleLogin
      onSuccess={(credentialResponse) => {
        if (credentialResponse.credential) {
          loginUser(credentialResponse.credential);
        }
      }}
      onError={() => console.error("Login failed")}
      auto_select={true}
    />
  );
};

export default Login;
