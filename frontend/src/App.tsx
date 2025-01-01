import "./App.css";
import styles from "./App.module.css";

import Login from "./components/Login/Login";
import ChatBox from "./components/ChatBox/ChatBox";
import Sidebar from "./components/SideBar/SideBar";
import Banner from "./components/Banner/Banner";

import { HashRouter, Route, Routes } from "react-router-dom";

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route
          path="/chat"
          element={
            <div className={styles.background}>
              <Banner />
              <Sidebar />
              <ChatBox />
            </div>
          }
        />
      </Routes>
    </HashRouter>
  );
}

export default App;
