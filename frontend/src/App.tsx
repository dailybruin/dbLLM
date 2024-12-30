import './App.css'
import styles from "./App.module.css";

import ChatBox from './components/ChatBox/ChatBox';
import Sidebar from './components/SideBar/SideBar';
import Banner from './components/Banner/Banner';

function App() {
  return (
    <div className={styles.background}>
      <Banner />
      <Sidebar />
      <ChatBox />
    </div>
  )
}

export default App
