import { UserProfile } from "../Models/User";
import React, { createContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { googleLogout } from "@react-oauth/google";

import axios from "axios";

type UserContextType = {
  user: UserProfile | null;
  token: string | null;
  loginUser: (jwt_token: string) => void;
  logoutUser: () => void;
  isLoggedIn: () => boolean;
};

type Props = { children: React.ReactNode };

const UserContext = createContext<UserContextType>({} as UserContextType);

//const BACKEND_DOMAIN = import.meta.env.BACKEND_DOMAIN;


export const UserProvider = ({ children }: Props) => {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);

  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const user = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    if (user && token) {
      setUser(JSON.parse(user));
      setToken(token);
    }
    setIsReady(true);
  }, []);

  const loginUser = async (jwt_token: string) => {
    await axios
      .post(`https://oliver.dailybruin.com/api/login/`, {"token": jwt_token})
      .then((res) => {
        if (res && res.status === 200) {
          const userObj = {
            name: res?.data.name,
            email: res?.data.email,
          };

          localStorage.setItem("user", JSON.stringify(userObj));
          localStorage.setItem("token", jwt_token);

          setUser(userObj);
          setToken(jwt_token);

          // Redirect to /chat after successful logijn
          navigate("/chat");
        }
        else {
          console.log("Login failed.");
        }
      })
      .catch((error) => console.error("Error during login:", error));
  };

  const isLoggedIn = () => {
    return !!user;
  }

  const logoutUser = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    setUser(null);
    setToken("");

    googleLogout();

    navigate("/");
  }

  return (
    <UserContext.Provider value={{ loginUser, user, token, logoutUser, isLoggedIn}}>
      {isReady ? children : null}
    </UserContext.Provider>
  )
};

export const useAuth = () => React.useContext(UserContext); 
