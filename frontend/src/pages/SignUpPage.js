import React, { useState } from "react";
// react-router-dom이 설치되어 있어야 합니다.
// npm install react-router-dom
import { useNavigate, Link } from "react-router-dom";
import axios from "axios"; // 백엔드 API 연동 시 필요

const SignUpPage = () => {
  const [userId, setUserId] = useState("");
  const [nickname, setNickname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [userIdChecked, setUserIdChecked] = useState(false);
  const [nicknameChecked, setNicknameChecked] = useState(false);
  const [userIdAvailable, setUserIdAvailable] = useState(false);
  const [nicknameAvailable, setNicknameAvailable] = useState(false);
  const navigate = useNavigate();

  // 아이디 중복 확인 로직
  const checkUserIdDuplicate = async () => {
    if (!userId.trim()) {
      alert("아이디를 입력해주세요.");
      return;
    }
    const idRegex = /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]{4,}$/;
    if (!idRegex.test(userId)) {
      alert("아이디는 4자 이상의 영문과 숫자를 포함해야 합니다.");
      return;
    }

    try {
      const res = await axios.get(`http://localhost:8000/api/check-username`, {
        params: { username: userId },
      });
      const isAvailable = res.data.available;
      setUserIdChecked(true);
      setUserIdAvailable(isAvailable);
      alert(
        isAvailable
          ? "사용 가능한 아이디입니다."
          : "이미 사용중인 아이디입니다."
      );
    } catch (err) {
      alert("서버 오류로 아이디 중복 확인 실패");
    }
  };

  const checkNicknameDuplicate = async () => {
    if (!nickname.trim() || nickname.length < 2) {
      alert("닉네임은 2자 이상이어야 합니다.");
      return;
    }

    try {
      const res = await axios.get(`http://localhost:8000/api/check-nickname`, {
        params: { nickname: nickname },
      });
      const isAvailable = res.data.available;
      setNicknameChecked(true);
      setNicknameAvailable(isAvailable);
      alert(
        isAvailable
          ? "사용 가능한 닉네임입니다."
          : "이미 사용중인 닉네임입니다."
      );
    } catch (err) {
      alert("서버 오류로 닉네임 중복 확인 실패");
    }
  };

  // 입력 값이 변경되면 중복 확인 상태 초기화
  const handleUserIdChange = (e) => {
    setUserId(e.target.value);
    setUserIdChecked(false);
    setUserIdAvailable(false);
  };

  const handleNicknameChange = (e) => {
    setNickname(e.target.value);
    setNicknameChecked(false);
    setNicknameAvailable(false);
  };

  // 회원가입 처리 로직
  const handleSignUp = async (e) => {
    e.preventDefault();
    if (!userIdChecked || !userIdAvailable) {
      alert("아이디 중복 확인을 완료해주세요.");
      return;
    }
    if (!nicknameChecked || !nicknameAvailable) {
      alert("닉네임 중복 확인을 완료해주세요.");
      return;
    }
    if (password !== confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/api/signup", {
        username: userId,
        nickname: nickname,
        email: email,
        password: password,
      });

      if (response.status === 200 || response.status === 201) {
        alert("회원가입 성공! 로그인 페이지로 이동합니다.");
        navigate("/login");
      }
    } catch (error) {
      console.error(error);
      alert("회원가입에 실패했습니다. 다시 시도해주세요.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white p-6 rounded-2xl shadow-lg w-full max-w-sm">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">계정 만들기</h2>
          <p className="text-gray-500 mt-1 text-sm">
            환영합니다! 정보를 입력해주세요.
          </p>
        </div>

        <form onSubmit={handleSignUp} className="space-y-3">
          {/* 아이디 */}
          <div>
            {/* --- 변경점: text-left 클래스 추가 --- */}
            <label
              htmlFor="userId"
              className="block text-sm font-medium text-gray-700 mb-1 text-left"
            >
              아이디
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                id="userId"
                placeholder="영문, 숫자 포함 4자 이상"
                className="flex-1 w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={userId}
                onChange={handleUserIdChange}
                required
              />
              <button
                type="button"
                onClick={checkUserIdDuplicate}
                className="px-3 py-1.5 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 text-xs font-semibold whitespace-nowrap transition"
              >
                중복확인
              </button>
            </div>
            {userIdChecked && (
              <p
                className={`text-xs mt-1.5 ${
                  userIdAvailable ? "text-green-600" : "text-red-600"
                }`}
              >
                {userIdAvailable
                  ? "✓ 사용 가능한 아이디입니다."
                  : "✗ 이미 사용중인 아이디입니다."}
              </p>
            )}
          </div>

          {/* 닉네임 */}
          <div>
            {/* --- 변경점: text-left 클래스 추가 --- */}
            <label
              htmlFor="nickname"
              className="block text-sm font-medium text-gray-700 mb-1 text-left"
            >
              닉네임
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                id="nickname"
                placeholder="2자 이상의 한글/영문"
                className="flex-1 w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                value={nickname}
                onChange={handleNicknameChange}
                required
              />
              <button
                type="button"
                onClick={checkNicknameDuplicate}
                className="px-3 py-1.5 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 text-xs font-semibold whitespace-nowrap transition"
              >
                중복확인
              </button>
            </div>
            {nicknameChecked && (
              <p
                className={`text-xs mt-1.5 ${
                  nicknameAvailable ? "text-green-600" : "text-red-600"
                }`}
              >
                {nicknameAvailable
                  ? "✓ 사용 가능한 닉네임입니다."
                  : "✗ 이미 사용중인 닉네임입니다."}
              </p>
            )}
          </div>

          {/* 이메일 */}
          <div>
            {/* --- 변경점: text-left 클래스 추가 --- */}
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1 text-left"
            >
              이메일
            </label>
            <input
              type="email"
              id="email"
              placeholder="example@email.com"
              className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          {/* 비밀번호 */}
          <div>
            {/* --- 변경점: text-left 클래스 추가 --- */}
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-1 text-left"
            >
              비밀번호
            </label>
            <input
              type="password"
              id="password"
              placeholder="비밀번호를 입력하세요"
              className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {/* 비밀번호 확인 */}
          <div>
            {/* --- 변경점: text-left 클래스 추가 --- */}
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700 mb-1 text-left"
            >
              비밀번호 확인
            </label>
            <input
              type="password"
              id="confirmPassword"
              placeholder="비밀번호를 다시 입력하세요"
              className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2.5 rounded-md hover:bg-blue-700 transition duration-300 font-semibold text-base shadow-md"
            >
              가입하기
            </button>
          </div>
        </form>

        <p className="text-center mt-5 text-xs text-gray-600">
          이미 계정이 있으신가요?{" "}
          <Link
            to="/login"
            className="text-blue-600 hover:underline font-medium"
          >
            로그인
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignUpPage;
