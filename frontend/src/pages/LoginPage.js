import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import axios from "axios";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

const LoginPage = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // 리다이렉트 경로 계산 함수를 메모이제이션
  // 소셜 로그인 콜백 처리
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const userStr = params.get("user");
    const error = params.get("error");
    const redirectPath = location.state?.from?.pathname || "/chatbot";

    if (error) {
      let errorMessage = "로그인에 실패했습니다.";
      switch (error) {
        case "token_error":
          errorMessage = "인증 토큰 발급에 실패했습니다.";
          break;
        case "api_error":
          errorMessage = "사용자 정보를 가져오는데 실패했습니다.";
          break;
        case "no_email":
          errorMessage = "이메일 정보를 가져올 수 없습니다.";
          break;
        case "server_error":
          errorMessage = "서버 오류가 발생했습니다.";
          break;
        default:
          errorMessage = "로그인에 실패했습니다.";
          break;
      }

      alert(errorMessage + " 다시 시도해주세요.");
      navigate("/", { replace: true });
      return;
    }

    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        login(token, user);
        navigate(redirectPath, { replace: true });
      } catch (e) {
        console.error("Error parsing user data:", e);
        alert("로그인 처리 중 오류가 발생했습니다.");
        navigate("/", { replace: true });
      }
    }
  }, [login, navigate, location]);

  const handleTraditionalLogin = async (e) => {
    e.preventDefault();
    const redirectPath = location.state?.from?.pathname || "/chatbot";

    try {
      // Form 데이터로 변환하여 전송
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await axios.post(`${BACKEND_URL}/api/login`, formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const { access_token, user } = response.data;
      login(access_token, user);
      navigate(redirectPath, { replace: true });
    } catch (error) {
      console.error("Login error:", error);
      alert("로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인해주세요.");
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/v1/login/google`);
      window.location.href = response.data.google_auth_url;
    } catch (error) {
      console.error("Google login error:", error);
    }
  };

  const handleNaverLogin = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/v1/login/naver`);
      window.location.href = response.data.naver_auth_url;
    } catch (error) {
      console.error("Naver login error:", error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="bg-white p-6 rounded-xl shadow-2xl w-full max-w-sm transform transition duration-500 hover:scale-105">
        <h2 className="text-3xl font-extrabold text-center mb-6 text-gray-900">
          로그인
        </h2>

        <form onSubmit={handleTraditionalLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className="sr-only">
              아이디
            </label>
            <input
              type="text"
              id="username"
              placeholder="아이디"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="sr-only">
              비밀번호
            </label>
            <input
              type="password"
              id="password"
              placeholder="비밀번호"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition duration-300 font-bold text-lg shadow-lg"
          >
            로그인
          </button>
        </form>

        <div className="my-6 text-center text-gray-600 relative">
          <span className="relative inline-block px-3 bg-white z-10 text-sm">
            또는
          </span>
          <span className="absolute inset-x-0 top-1/2 h-px bg-gray-300 transform -translate-y-1/2"></span>
        </div>

        <div className="flex flex-col space-y-3">
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full bg-white text-gray-800 border border-gray-300 py-2 rounded-lg hover:bg-gray-100 transition duration-300 font-semibold text-base shadow-md flex items-center justify-center space-x-2"
          >
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/512px-Google_%22G%22_logo.svg.png"
              alt="Google logo"
              className="w-5 h-5"
            />
            <span>Google로 로그인</span>
          </button>

          <button
            type="button"
            onClick={handleNaverLogin}
            className="w-full py-2 rounded-lg font-bold text-base shadow-md flex items-center justify-center space-x-2"
            style={{ backgroundColor: "#03C75A", color: "white" }}
          >
            <img
              src="https://www.naver.com/favicon.ico"
              alt="Naver logo"
              className="w-5 h-5"
            />
            <span>네이버로 로그인</span>
          </button>
        </div>

        <p className="text-center mt-6 text-gray-700 text-sm">
          계정이 없으신가요?{" "}
          <Link
            to="/signup"
            className="text-blue-600 hover:underline font-semibold"
          >
            회원가입
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
