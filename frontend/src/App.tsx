import "./App.css";
import styles from "./App.module.css";

import Login from "./components/Login/Login";
import ChatBox from "./components/ChatBox/ChatBox";
import Sidebar from "./components/SideBar/SideBar";
import Banner from "./components/Banner/Banner";

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { UserProvider } from "./Context/useAuth";
import ProtectedRoute from "./Routes/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <Routes>
          <Route path="/" element={<Login />} />

          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <div className={styles.background}>
                  <Banner />
                  <Sidebar />
                  <ChatBox />
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </UserProvider>
    </BrowserRouter>
  );
}

export default App;
