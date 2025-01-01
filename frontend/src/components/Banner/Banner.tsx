import styles from "./Banner.module.css";
import { googleLogout } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

function Banner() {
  const navigate = useNavigate();

  function handleLogout() {
    googleLogout();
    navigate("/");
  }

  return (
    <div className={styles.gridContainer}>
      <h2 className={styles.bannerTitle}> UCLA Daily Bruin — Project Oliver </h2>
      <button className={styles.logoutButton} onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Banner;