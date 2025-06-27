import React, { useState, useEffect, useCallback, useMemo } from "react";
import { destinationsData } from "../data/destinationsData";

const DestinationCard = React.memo(({ destination, index, destinations }) => (
  <div className="flex-shrink-0 px-4" style={{ width: `${100 / destinations.length}%` }}>
    <div className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 overflow-hidden h-full">
      {/* Image Container */}
      <div className="relative">
        <img
          src={destination.image}
          alt={destination.name}
          className="w-full h-64 object-cover rounded-t-xl"
          loading="lazy"
        />
        {/* Overlay Gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent rounded-t-xl"></div>
      </div>

      {/* Card Content */}
      <div className="p-4">
        <h3 className="text-dark font-poppins font-semibold text-lg leading-6 mb-2">
          {destination.name}
        </h3>

        <div className="flex justify-between items-center mb-3">
          <div className="flex items-center text-gray-400">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" className="mr-1">
              <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="2" fill="none" />
              <path d="M8 4v4l3 2" stroke="currentColor" strokeWidth="2" fill="none" />
            </svg>
            <span className="text-sm font-poppins font-medium">{destination.location}</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-accent font-poppins font-semibold text-base">
            {destination.price}
          </span>
        </div>
      </div>
    </div>
  </div>
));

DestinationCard.displayName = "DestinationCard";

const FeaturesSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const destinations = destinationsData;

  const itemsPerView = 4;
  const maxIndex = useMemo(
    () => Math.max(0, destinations.length - itemsPerView),
    [destinations.length, itemsPerView],
  );

  // 자동 슬라이드 기능
  useEffect(() => {
    if (!isAutoPlaying) return;

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex >= maxIndex ? 0 : prevIndex + 1));
    }, 5000); // 5초마다 자동 넘김

    return () => clearInterval(interval);
  }, [maxIndex, isAutoPlaying]);

  const nextSlide = useCallback(() => {
    setIsAutoPlaying(false);
    setCurrentIndex((prevIndex) => (prevIndex >= maxIndex ? 0 : prevIndex + 1));
    setTimeout(() => setIsAutoPlaying(true), 10000); // 10초 후 자동 재생 재개
  }, [maxIndex]);

  const prevSlide = useCallback(() => {
    setIsAutoPlaying(false);
    setCurrentIndex((prevIndex) => (prevIndex <= 0 ? maxIndex : prevIndex - 1));
    setTimeout(() => setIsAutoPlaying(true), 10000); // 10초 후 자동 재생 재개
  }, [maxIndex]);

  const handleIndicatorClick = useCallback((index) => {
    setCurrentIndex(index);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 10000);
  }, []);

  const sliderStyle = useMemo(
    () => ({
      transform: `translateX(-${currentIndex * (100 / itemsPerView)}%)`,
      width: `${(destinations.length / itemsPerView) * 100}%`,
    }),
    [currentIndex, itemsPerView, destinations.length],
  );

  const indicators = useMemo(
    () =>
      Array.from({ length: maxIndex + 1 }).map((_, index) => (
        <button
          key={index}
          onClick={() => handleIndicatorClick(index)}
          className={`w-3 h-3 rounded-full transition-colors ${
            index === currentIndex ? "bg-primary" : "bg-gray-300"
          }`}
        />
      )),
    [maxIndex, currentIndex, handleIndicatorClick],
  );

  return (
    <section id="features" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-dark font-poppins font-bold text-5xl leading-tight mb-6">
            반려견과 함께하는 여행지 추천
          </h2>
          <p className="text-gray-text font-poppins text-lg leading-7 max-w-3xl mx-auto mb-8">
            우리개 어디가에서 제공하는 서비스 중<br />
            반려동물 동반 가능 장소의 경우, 다음과 같은 내용을 제공합니다
          </p>

          {/* Navigation Arrows */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={prevSlide}
              className="w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-shadow"
              aria-label="이전 슬라이드"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="#152137">
                <path d="M10 3l-5 5 5 5" />
              </svg>
            </button>
            <button
              onClick={nextSlide}
              className="w-16 h-16 bg-white rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-shadow"
              aria-label="다음 슬라이드"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="#152137">
                <path d="M6 3l5 5-5 5" />
              </svg>
            </button>
          </div>
        </div>

        {/* Destination Cards Slider */}
        <div className="relative overflow-hidden">
          <div className="flex transition-transform duration-500 ease-in-out" style={sliderStyle}>
            {destinations.map((destination, index) => (
              <DestinationCard
                key={`${destination.name}-${index}`}
                destination={destination}
                index={index}
                destinations={destinations}
              />
            ))}
          </div>
        </div>

        {/* Slide Indicators */}
        <div className="flex justify-center mt-8 space-x-2">{indicators}</div>
      </div>
    </section>
  );
};

export default React.memo(FeaturesSection);
