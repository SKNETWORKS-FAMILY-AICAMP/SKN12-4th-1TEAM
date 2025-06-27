import React, { useState, useEffect, useCallback } from "react";

const ScrollToTop = () => {
  const [isVisible, setIsVisible] = useState(false);

  // 스크롤 위치 감지
  const toggleVisibility = useCallback(() => {
    if (window.pageYOffset > 300) {
      setIsVisible(true);
    } else {
      setIsVisible(false);
    }
  }, []);

  // 스로틀된 스크롤 핸들러
  const throttledToggleVisibility = useCallback(() => {
    let inThrottle = false;

    return function () {
      if (!inThrottle) {
        toggleVisibility();
        inThrottle = true;
        setTimeout(() => {
          inThrottle = false;
        }, 100);
      }
    };
  }, [toggleVisibility])();

  useEffect(() => {
    window.addEventListener("scroll", throttledToggleVisibility, { passive: true });
    return () => window.removeEventListener("scroll", throttledToggleVisibility);
  }, [throttledToggleVisibility]);

  // 상단으로 부드럽게 스크롤
  const scrollToTop = useCallback(() => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }, []);

  if (!isVisible) {
    return null;
  }

  return (
    <button
      onClick={scrollToTop}
      className="fixed bottom-8 right-8 z-50 w-14 h-14 bg-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center group border border-gray-200 hover:scale-110"
      aria-label="맨 위로 이동"
    >
      <svg
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        className="text-gray-600 group-hover:text-primary transition-colors duration-300"
      >
        <path
          d="M12 19V5M5 12L12 5L19 12"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
};

export default React.memo(ScrollToTop);
