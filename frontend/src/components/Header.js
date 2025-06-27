import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="absolute top-0 w-full z-50 bg-transparent">
      <nav className="relative flex items-center justify-between px-24 h-24">
        {/* 왼쪽: 로고 */}
        <div className="flex items-center">
          <img
            src="/images/dog-logo.png"
            alt="Dog Logo"
            className="w-30 h-30 mr-3"
            loading="eager"
          />
          <span className="text-white font-bold text-2xl leading-6">
            우리개
            <br />
            어디가
          </span>
        </div>

        {/* 가운데: 메뉴 */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex gap-x-10">
          {/* 서비스 소개 */}
          <div className="relative">
            <a
              href="/#services"
              className="text-white text-lg font-medium hover:opacity-100"
            >
              서비스 소개
            </a>
            <div className="absolute bottom-[-2px] left-0 w-full h-px bg-white" />
          </div>

          {/* 여행지 추천 */}
          <div className="relative">
            <a
              href="/#features"
              className="text-white text-lg font-medium hover:opacity-100"
            >
              여행지 추천
            </a>
            <div className="absolute bottom-[-2px] left-0 w-full h-px bg-white" />
          </div>

          {/* 서비스 후기 */}
          <div className="relative">
            <a
              href="/#testimonials"
              className="text-white text-lg font-medium hover:opacity-100"
            >
              서비스 후기
            </a>
            <div className="absolute bottom-[-2px] left-0 w-full h-px bg-white" />
          </div>
        </div>

        {/* 오른쪽: 버튼 */}
        <div className="flex items-center gap-x-4">
          {user ? (
            <>
              <span className="text-white font-semibold">
                Welcome, {user.nickname || user.username}!
              </span>
              <button
                onClick={handleLogout}
                className="bg-transparent border border-white rounded-lg px-6 py-2 text-white font-semibold text-sm hover:bg-opacity-90 transition-all"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate("/login")}
                className="bg-transparent border border-white rounded-lg px-6 py-2 text-white font-semibold text-sm hover:bg-opacity-90 transition-all"
              >
                Login
              </button>
              <button
                onClick={() => navigate("/signup")}
                className="bg-transparent border border-white rounded-lg px-6 py-2 text-white font-semibold text-sm hover:bg-opacity-90 transition-all"
              >
                Create Account
              </button>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default React.memo(Header);
