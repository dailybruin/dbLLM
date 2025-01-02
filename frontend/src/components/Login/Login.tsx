import { GoogleLogin } from "@react-oauth/google";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login: React.FC = () => {
  const navigate = useNavigate();

  return (
    <GoogleLogin
      onSuccess={async (credentialResponse) => {
        if (credentialResponse.credential) {
          const jwt = {
            "token": credentialResponse
          }
          try {
            const response = await axios.post("http://localhost:5001/login", jwt );
            if (response.status === 200) {
              console.log("Login successful.");
              navigate("/chat");
            } else {
              console.error("Login failed");
            }
          } catch (error) {
            console.error("Error during login:", error);
          }
        }
      }}
      onError={() => console.error("Login failed")}
      auto_select={true}
    />
  );
};

export default Login;
