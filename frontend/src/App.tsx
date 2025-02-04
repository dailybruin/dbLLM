import "./App.css";
import styles from "./App.module.css";
import { useState } from 'react'; // Add useState import
import Login from "./components/Login/Login";
import ChatBox from "./components/ChatBox/ChatBox";
import Sidebar from "./components/SideBar/SideBar";
import Banner from "./components/Banner/Banner";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { UserProvider } from "./Context/useAuth";
import ProtectedRoute from "./Routes/ProtectedRoute";

function App() {
  // Add state for timers
  const [timings, setTimings] = useState({
    queryTime: 0,
    responseTime: 0
  });

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
                  <Sidebar
                    queryTime={timings.queryTime}
                    responseTime={timings.responseTime}
                  />
                  <ChatBox
                    onTimingUpdate={(qt, rt) => setTimings({ queryTime: qt, responseTime: rt })}
                  />
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