import React, { useEffect, useRef, useState } from "react";

const ServicesSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [visibleCards, setVisibleCards] = useState([]);
  const sectionRef = useRef(null);
  const cardRefs = useRef([]);

  const services = [
    {
      title: "반려동물 동반 여행 A to Z",
      description: "여행 일수, 지역 등 사용자 정보에 맞게 \n 반려동물 동반 가능 장소 정보를 제공함",
      icon: (
        <div className="w-20 h-20 bg-white rounded-lg shadow-lg flex items-center justify-center">
          <img
            src="/images/icon_1.png"
            alt="Weather Icon"
            className="w-12 h-12 object-contain"
            loading="lazy"
          />
        </div>
      ),
    },
    {
      title: "교통수단별 이용 가이드",
      description: "버스, 지하철, 기차 등 다양한 교통수단에 대한 대중교통 이용 규정을 알려줌",
      icon: (
        <div className="w-20 h-20 bg-white rounded-lg shadow-lg flex items-center justify-center">
          <img
            src="/images/icon_2.png"
            alt="Transportation Icon"
            className="w-12 h-12 object-contain"
            loading="lazy"
          />
        </div>
      ),
    },
    {
      title: "실시간 날씨 체크",
      description: "반려동물과의 행복한 여행을 위해 \n 실시간 날씨 API가 연동되어 있음",
      icon: (
        <div className="w-20 h-20 bg-white rounded-lg shadow-lg flex items-center justify-center">
          <img
            src="/images/icon_3.png"
            alt="Pet Travel Icon"
            className="w-12 h-12 object-contain"
            loading="lazy"
          />
        </div>
      ),
    },
  ];

  // 섹션 헤더 애니메이션을 위한 Intersection Observer
  useEffect(() => {
    const currentSectionRef = sectionRef.current;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      {
        threshold: 0.3,
        rootMargin: "-50px",
      },
    );

    if (currentSectionRef) {
      observer.observe(currentSectionRef);
    }

    return () => {
      if (currentSectionRef) {
        observer.unobserve(currentSectionRef);
      }
    };
  }, []);

  // 개별 카드 애니메이션을 위한 Intersection Observer
  useEffect(() => {
    const currentCardRefs = cardRefs.current;

    const observers = currentCardRefs.map((cardRef, index) => {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              setVisibleCards((prev) => [...prev, index]);
            }, index * 200); // 각 카드마다 200ms 지연
          }
        },
        {
          threshold: 0.2,
          rootMargin: "-30px",
        },
      );

      if (cardRef) {
        observer.observe(cardRef);
      }

      return observer;
    });

    return () => {
      observers.forEach((observer, index) => {
        if (currentCardRefs[index]) {
          observer.unobserve(currentCardRefs[index]);
        }
      });
    };
  }, []);

  return (
    <section id="services" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-8">
        {/* Section Header */}
        <div
          ref={sectionRef}
          className={`text-center mb-20 transform transition-all duration-1000 ease-out ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <h2 className="text-dark font-poppins font-bold text-5xl leading-tight mb-6">
            서비스 소개
          </h2>
          <p className="text-gray-text font-poppins text-lg leading-7 max-w-2xl mx-auto">
            반려동물과 함께하는 당신의 여행이 최고가 될 수 있도록,
            <br />
            우리개 어디가는 다음과 같은 서비스를 제공하고 있습니다
          </p>
        </div>

        {/* Service Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div
              key={index}
              ref={(el) => (cardRefs.current[index] = el)}
              className={`bg-white rounded-xl p-8 transform transition-all duration-800 ease-out ${
                visibleCards.includes(index)
                  ? "translate-y-0 opacity-100 scale-100"
                  : "translate-y-12 opacity-0 scale-95"
              } ${index === 1 ? "shadow-2xl" : "shadow-lg"} hover:shadow-2xl hover:scale-105 transition-shadow duration-300`}
              style={{
                transitionDelay: visibleCards.includes(index) ? "0ms" : `${index * 100}ms`,
              }}
            >
              {/* Icon */}
              <div
                className={`mb-8 transform transition-all duration-600 ease-out ${
                  visibleCards.includes(index)
                    ? "translate-y-0 opacity-100 rotate-0"
                    : "translate-y-4 opacity-0 rotate-12"
                }`}
                style={{
                  transitionDelay: visibleCards.includes(index) ? "200ms" : "0ms",
                }}
              >
                {service.icon}
              </div>

              {/* Content */}
              <div
                className={`transform transition-all duration-600 ease-out ${
                  visibleCards.includes(index)
                    ? "translate-y-0 opacity-100"
                    : "translate-y-4 opacity-0"
                }`}
                style={{
                  transitionDelay: visibleCards.includes(index) ? "400ms" : "0ms",
                }}
              >
                <h3 className="text-dark font-poppins font-semibold text-2xl leading-9 mb-4">
                  {service.title}
                </h3>
                <p className="text-gray-text font-poppins text-base leading-6 whitespace-pre-line">
                  {service.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default React.memo(ServicesSection);
