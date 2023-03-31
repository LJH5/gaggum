import "./Start.style.scss";
import loginImg from "../../assets/start/kakao_login_large_wide.png";
import logoImg from "../../assets/logo/maskable_icon_x192_logo.png"

const StartPage = () => {
  const REST_API_KEY = process.env.REACT_APP_KAKAO_LOGIN_REST_API_KEY;
  // const REDIRECT_URI = "http://localhost:3000/auth/kakao/callback";
  const REDIRECT_URI = "https://j8b310.p.ssafy.io/auth/kakao/callback";
  const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;

  const handleLogin = () => {
    window.location.href = KAKAO_AUTH_URL;
  };
  const setToken = () => {
    localStorage.setItem("turtle_number", 1);
  };
  return (
    <div className="StartPage">
      <div className="start-content">
        <img 
          className="start__logo"
          src={logoImg}
        />
        <img
          className="button-content"
          src={loginImg}
          alt="카카오 로그인"
          onClick={handleLogin}
        />
      </div>
    </div>
  );
};

export default StartPage;
