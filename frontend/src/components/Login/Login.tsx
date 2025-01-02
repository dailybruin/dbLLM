import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import { useNavigate } from "react-router-dom";
import axios, {
  AxiosResponse,
  AxiosRequestConfig,
  RawAxiosRequestHeaders,
} from "axios";

interface JwtPayload {
  email?: string;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  return (
    <>
      <GoogleLogin
        onSuccess={async (credentialResponse) => {
          if (credentialResponse.credential) {
            const decoded: JwtPayload = jwtDecode(
              credentialResponse.credential
            );

            const config: AxiosRequestConfig = {
              headers: {
                Accept: "application/json",
              } as RawAxiosRequestHeaders,
            };

            console.log(decoded);
            const response: AxiosResponse = await axios.post(
              "http://localhost:5001/is_valid_user",
              decoded,
              config
            );

            if (response.status == 200) {
              console.log("Login successful.");
              navigate("/chat");
            }
            else {
              console.log("Login unsuccessful.");
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
