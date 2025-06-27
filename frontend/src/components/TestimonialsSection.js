import React, { useState, useEffect, useCallback, useMemo } from "react";
import { testimonialsData } from "../data/testimonialsData";

const StarRating = React.memo(({ rating }) => {
  const stars = useMemo(() => {
    return [...Array(5)].map((_, index) => (
      <svg
        key={index}
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill={index < rating ? "#FAB33F" : "#E5E7EB"}
      >
        <path d="M8 1l1.5 4.5H14l-3.5 2.5 1.5 4.5L8 10 4.5 12.5 6 8 2.5 5.5H7L8 1z" />
      </svg>
    ));
  }, [rating]);

  return <div className="flex space-x-1">{stars}</div>;
});

StarRating.displayName = "StarRating";

const TestimonialCard = React.memo(({ testimonial, index, testimonials }) => (
  <div className="flex-shrink-0 px-4" style={{ width: `${100 / testimonials.length}%` }}>
    <div
      className={`bg-white rounded-xl p-8 h-full ${testimonial.featured ? "shadow-2xl" : "shadow-lg"} hover:shadow-2xl transition-shadow duration-300`}
    >
      {/* User Image */}
      <div className="flex justify-center mb-6">
        <img
          src={testimonial.image}
          alt={testimonial.name}
          className="w-20 h-20 rounded-full object-cover shadow-lg"
          loading="lazy"
        />
      </div>

      {/* User Info */}
      <div className="text-center mb-4">
        <h3 className="text-dark font-poppins font-semibold text-xl leading-6 mb-1">
          {testimonial.name}
        </h3>
        <div className="flex justify-center mb-2">
          <span className="text-gray-400 font-poppins text-sm bg-gray-100 px-3 py-1 rounded">
            {testimonial.title}
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="w-full h-px bg-gray-200 mb-6"></div>

      {/* Rating */}
      <div className="flex justify-center mb-4">
        <StarRating rating={testimonial.rating} />
      </div>

      {/* Testimonial Text */}
      <p className="text-gray-600 font-poppins text-base leading-6 text-center whitespace-pre-line">
        {testimonial.text}
      </p>
    </div>
  </div>
));

TestimonialCard.displayName = "TestimonialCard";

const TestimonialsSection = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);

  const testimonials = testimonialsData;

  const itemsPerView = 4;
  const maxIndex = useMemo(
    () => Math.max(0, testimonials.length - itemsPerView),
    [testimonials.length, itemsPerView],
  );

  // 자동 슬라이드 기능
  useEffect(() => {
    if (!isAutoPlaying) return;

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex >= maxIndex ? 0 : prevIndex + 1));
    }, 4000); // 4초마다 자동 넘김

    return () => clearInterval(interval);
  }, [maxIndex, isAutoPlaying]);

  const nextSlide = useCallback(() => {
    setIsAutoPlaying(false);
    setCurrentIndex((prevIndex) => (prevIndex >= maxIndex ? 0 : prevIndex + 1));
    setTimeout(() => setIsAutoPlaying(true), 8000); // 8초 후 자동 재생 재개
  }, [maxIndex]);

  const prevSlide = useCallback(() => {
    setIsAutoPlaying(false);
    setCurrentIndex((prevIndex) => (prevIndex <= 0 ? maxIndex : prevIndex - 1));
    setTimeout(() => setIsAutoPlaying(true), 8000); // 8초 후 자동 재생 재개
  }, [maxIndex]);

  const handleIndicatorClick = useCallback((index) => {
    setCurrentIndex(index);
    setIsAutoPlaying(false);
    setTimeout(() => setIsAutoPlaying(true), 8000);
  }, []);

  const sliderStyle = useMemo(
    () => ({
      transform: `translateX(-${currentIndex * (100 / itemsPerView)}%)`,
      width: `${(testimonials.length / itemsPerView) * 100}%`,
    }),
    [currentIndex, itemsPerView, testimonials.length],
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
    <section id="testimonials" className="bg-white py-24">
      <div className="max-w-7xl mx-auto px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-dark font-poppins font-bold text-4xl leading-tight mb-6">
            고객님들의 서비스 실사용 후기
          </h2>
          <p className="text-gray-text font-poppins text-base leading-7 mb-8">
            우리개 어디가를 실제로 사용한 유저들의 반응입니다
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

        {/* Testimonial Cards Slider */}
        <div className="relative overflow-hidden">
          <div className="flex transition-transform duration-500 ease-in-out" style={sliderStyle}>
            {testimonials.map((testimonial, index) => (
              <TestimonialCard
                key={`${testimonial.name}-${index}`}
                testimonial={testimonial}
                index={index}
                testimonials={testimonials}
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

export default React.memo(TestimonialsSection);
