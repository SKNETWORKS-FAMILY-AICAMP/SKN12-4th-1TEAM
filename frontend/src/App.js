import React, { useEffect, useRef } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
  useNavigate,
} from "react-router-dom";
import "./App.css";
import Header from "./components/Header";
import MainSection from "./components/MainSection";
import ServicesSection from "./components/ServicesSection";
import FeaturesSection from "./components/FeaturesSection";
import TestimonialsSection from "./components/TestimonialsSection";
import Footer from "./components/Footer";
import ChatbotInterface from "./components/ChatbotInterface";
import ScrollToTop from "./components/ScrollToTop";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import { AuthProvider, useAuth } from "./context/AuthContext";

// 토큰 처리를 위한 컴포넌트
const TokenHandler = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useAuth();
  const processedRef = useRef(false);

  useEffect(() => {
    // 토큰 처리는 한 번만 수행
    const handleToken = () => {
      if (processedRef.current) return;

      const params = new URLSearchParams(location.search);
      const token = params.get("token");

      if (token) {
        try {
          processedRef.current = true;

          // 토큰이 URL에 있으면 로그인 처리
          const userData = {
            username: "user", // 기본값, 실제로는 토큰에서 추출하거나 API 호출로 가져와야 함
            email: "",
            nickname: "",
          };

          login(userData, token);

          // 토큰 파라미터 제거하고 홈페이지로 리다이렉트
          navigate("/", { replace: true });
        } catch (error) {
          console.error("토큰 처리 오류:", error);
          navigate("/login", { replace: true });
        }
      }
    };

    handleToken();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  return children;
};

const HomePage = () => {
  return (
    <>
      <Header />
      <MainSection />
      <ServicesSection />
      <FeaturesSection />
      <TestimonialsSection />
      <Footer />
      <ScrollToTop />
    </>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <TokenHandler>
          <div className="App">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/main" element={<HomePage />} />
              <Route path="/chatbot" element={<ChatbotInterface />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignUpPage />} />
            </Routes>
          </div>
        </TokenHandler>
      </AuthProvider>
    </Router>
  );
}

export default App;
