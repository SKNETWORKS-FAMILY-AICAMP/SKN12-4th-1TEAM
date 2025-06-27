import React from "react";

const Footer = () => {
  const socialLinks = [
    {
      name: "Pinterest",
      href: "#", // 실제 링크로 교체하세요.
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 0C4.477 0 0 4.477 0 10c0 4.237 2.636 7.855 6.356 9.312-.088-.791-.167-2.005.035-2.868.181-.78 1.172-4.97 1.172-4.97s-.299-.598-.299-1.482c0-1.388.805-2.425 1.809-2.425.853 0 1.264.641 1.264 1.408 0 .858-.546 2.14-.828 3.33-.236.996.5 1.807 1.481 1.807 1.778 0 3.144-1.874 3.144-4.58 0-2.393-1.72-4.068-4.176-4.068-2.845 0-4.516 2.135-4.516 4.34 0 .859.331 1.781.744 2.281a.3.3 0 01.069.287c-.076.315-.245.994-.278 1.133-.043.183-.141.222-.325.134-1.249-.581-2.03-2.407-2.03-3.874 0-3.154 2.292-6.052 6.608-6.052 3.469 0 6.165 2.473 6.165 5.776 0 3.447-2.173 6.22-5.19 6.22-1.013 0-1.965-.527-2.291-1.155l-.623 2.378c-.226.869-.835 1.958-1.244 2.621.937.29 1.931.446 2.962.446 5.523 0 10-4.477 10-10S15.523 0 10 0z" />
        </svg>
      ),
    },
    {
      name: "Facebook",
      href: "#", // 실제 링크로 교체하세요.
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" />
        </svg>
      ),
    },
    {
      name: "LinkedIn",
      href: "#", // 실제 링크로 교체하세요.
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path d="M18.335 18.339H15.67v-4.177c0-.996-.02-2.278-1.39-2.278-1.389 0-1.601 1.084-1.601 2.205v4.25h-2.666V9.75h2.56v1.17h.035c.358-.674 1.228-1.387 2.528-1.387 2.7 0 3.2 1.778 3.2 4.091v4.715zM4.943 8.57c-.86 0-1.548-.69-1.548-1.54s.688-1.54 1.548-1.54c.854 0 1.548.69 1.548 1.54S5.797 8.57 4.943 8.57zM6.276 18.339H3.61V9.75h2.667v8.589zM19.67 0H.329C.146 0 0 .154 0 .329v19.342C0 19.846.154 20 .329 20h19.341c.175 0 .329-.154.329-.329V.329C20 .154 19.846 0 19.67 0z" />
        </svg>
      ),
    },
    {
      name: "Twitter",
      href: "#", // 실제 링크로 교체하세요.
      icon: (
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
        </svg>
      ),
    },
  ];

  return (
    // 전체적인 상하 여백(padding)을 조절하여 더 컴팩트하게 만듭니다.
    <footer className="bg-black text-white py-16">
      <div className="max-w-7xl mx-auto px-8">
        {/* 모든 요소를 수직으로 쌓고, 중앙 정렬합니다. */}
        <div className="flex flex-col items-center text-center space-y-8">
          {/* 1. 로고와 회사명을 가로로 배치하는 컨테이너 */}
          <div className="flex flex-row items-center space-x-4">
            {/* 로고 이미지 */}
            <img
              src="/images/dog-logo.png"
              alt="Dog Logo"
              className="w-30 h-30 " // 이미지 크기 조절
            />
            {/* 회사명 텍스트 */}
            <span className="text-white font-poppins font-bold text-4xl leading-tight">
              우리개
              <br />
              어디가
            </span>
          </div>

          {/* 2. 회사 정보 (폰트 사이즈 조절) */}
          <div className="text-gray-400">
            <p className="font-poppins text-base leading-6">
              대표: 박슬기
              <br />
              주소: 서울 금천구 가산디지털1로 25 18층 플레이데이터
              <br />
              메일: keindus2@gmail.com
            </p>
          </div>

          {/* 3. 소셜 미디어 링크 (아이콘/텍스트 사이즈 조절) */}
          <div className="flex space-x-8">
            {socialLinks.map((social) => (
              <div key={social.name} className="flex flex-col items-center space-y-2">
                <a
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-7 h-7 bg-white rounded-full flex items-center justify-center text-black hover:bg-gray-200 transition-colors cursor-pointer"
                >
                  {social.icon}
                </a>
                <span className="text-white opacity-84 font-poppins font-medium text-sm">
                  {social.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default React.memo(Footer);
