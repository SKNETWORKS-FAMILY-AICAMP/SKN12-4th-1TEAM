import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const MainSection = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleChatbotClick = () => {
    if (user) {
      navigate("/chatbot");
    } else {
      navigate("/login");
    }
  };

  return (
    <section className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        className="absolute z-0 w-full h-full object-cover"
      >
        <source src="/assets/background.mp4" type="video/mp4" />
      </video>

      {/* Overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-50 z-10"></div>

      {/* Content */}
      <div className="relative z-20 text-white flex flex-col items-center">
        {/* 로고 + 타이틀 수평 배치 */}
        <div className="flex items-center justify-center mb-6">
          <img
            src="/images/chatbot-avatar.png"
            alt="logo"
            className="w-[100px] h-[100px] mr-4"
          />
          <h1 className="text-6xl font-bold">우리개 어디가</h1>
        </div>

        {/* 설명 문구 */}
        <p className="text-2xl mb-6">
          반려견과 함께하는 여행코스를 추천해주는 챗봇
        </p>

        {/* CTA Button */}
        <button
          onClick={handleChatbotClick}
          className="bg-[#3580A9] rounded-full px-20 py-6 text-white font-inter font-semibold text-3xl hover:bg-opacity-90 transition-all"
        >
          챗봇 시작하기
        </button>
      </div>
    </section>
  );
};

export default MainSection;
