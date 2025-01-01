import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";

interface JwtPayload {
  email?: string;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  return (
    <>
      <GoogleLogin
        onSuccess={(credentialResponse) => {
          if (credentialResponse.credential) {
            const decoded: JwtPayload = jwtDecode(
              credentialResponse.credential
            );
            console.log(decoded);

            if (decoded.email && decoded.email.endsWith("@media.ucla.edu")) {
              navigate("/chat");
            }
          } else {
            console.error("No credential received.");
          }
        }}
        onError={() => console.log("Login failed.")}
        auto_select={true}
      />
    </>
  );
};

export default Login;
