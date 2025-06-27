import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

const AuthContext = createContext(null);
const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

// 인터셉터 설정 함수 (컴포넌트 외부에 정의)
let requestInterceptor = null;
let responseInterceptor = null;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const isRefreshing = useRef(false);
  const refreshFailCount = useRef(0);
  const MAX_REFRESH_ATTEMPTS = 2;

  // 토큰 유효성 검사 함수
  const isTokenValid = useCallback((tokenToCheck) => {
    if (!tokenToCheck) return false;

    try {
      if (!tokenToCheck.includes(".") || tokenToCheck.split(".").length !== 3) {
        console.error("Invalid token format");
        return false;
      }

      const decoded = jwtDecode(tokenToCheck);
      return decoded.exp * 1000 > Date.now();
    } catch (error) {
      console.error("Token validation error:", error);
      return false;
    }
  }, []);

  // 로그아웃 함수
  const logout = useCallback(async () => {
    try {
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        try {
          await axios.post(`${BACKEND_URL}/api/logout`, null, {
            headers: { Authorization: `Bearer ${storedToken}` },
          });
        } catch (error) {
          console.error("Error during logout API call:", error);
        }
      }
    } finally {
      localStorage.removeItem("user");
      localStorage.removeItem("token");
      setUser(null);
      setToken(null);
      refreshFailCount.current = 0;
      window.location.href = "/login";
    }
  }, []);

  // 토큰 갱신 함수
  const refreshToken = useCallback(async () => {
    if (isRefreshing.current) {
      console.log("Token refresh already in progress");
      return false;
    }

    if (refreshFailCount.current >= MAX_REFRESH_ATTEMPTS) {
      console.log("Maximum refresh attempts reached");
      logout();
      return false;
    }

    isRefreshing.current = true;

    try {
      const storedToken = localStorage.getItem("token");
      if (!storedToken) {
        throw new Error("No token available");
      }

      console.log("Starting token refresh");

      const response = await axios.post(
        `${BACKEND_URL}/api/refresh-token`,
        {},
        { headers: { Authorization: `Bearer ${storedToken}` } }
      );

      const { access_token, user: userData } = response.data;

      if (!access_token) {
        throw new Error("No token received");
      }

      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      // 상태 업데이트
      setToken(access_token);
      setUser(userData);

      refreshFailCount.current = 0;
      console.log("Token refresh successful");
      return true;
    } catch (error) {
      console.error("Token refresh failed:", error);
      refreshFailCount.current += 1;

      if (refreshFailCount.current >= MAX_REFRESH_ATTEMPTS) {
        console.log("Maximum refresh attempts reached, logging out");
        logout();
      }
      return false;
    } finally {
      // 약간의 지연 후 갱신 상태 초기화
      setTimeout(() => {
        isRefreshing.current = false;
      }, 200);
    }
  }, [logout]);

  // 로그인 함수
  const login = useCallback(
    (userData, authToken) => {
      try {
        if (!userData || !authToken) {
          throw new Error("Invalid login data");
        }

        if (!authToken.includes(".") || authToken.split(".").length !== 3) {
          throw new Error("Invalid token format");
        }

        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", authToken);
        setUser(userData);
        setToken(authToken);
        refreshFailCount.current = 0;
      } catch (error) {
        console.error("Error during login:", error);
        logout();
      }
    },
    [logout]
  );

  // API 요청에 사용할 헤더를 반환하는 함수
  const getAuthHeaders = useCallback(() => {
    const storedToken = localStorage.getItem("token");
    return storedToken
      ? {
          Authorization: `Bearer ${storedToken}`,
          "Content-Type": "application/json",
        }
      : {};
  }, []);

  // 인증 상태 초기화
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem("token");
        const storedUser = localStorage.getItem("user");

        if (storedToken && storedUser) {
          if (isTokenValid(storedToken)) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
          } else {
            // 토큰이 만료된 경우 갱신 시도
            const refreshed = await refreshToken();
            if (!refreshed) {
              console.log("Token refresh failed, redirecting to login");
            }
          }
        }
      } catch (error) {
        console.error("Auth initialization error:", error);
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [isTokenValid, refreshToken]);

  // 인터셉터 설정 (컴포넌트 마운트 시 한 번만)
  useEffect(
    () => {
      // 기존 인터셉터 제거
      if (requestInterceptor !== null) {
        axios.interceptors.request.eject(requestInterceptor);
      }
      if (responseInterceptor !== null) {
        axios.interceptors.response.eject(responseInterceptor);
      }

      // 요청 인터셉터 설정
      requestInterceptor = axios.interceptors.request.use(
        (config) => {
          // 인증 관련 요청은 그대로 진행
          if (
            config.url?.includes("/login") ||
            config.url?.includes("/refresh-token") ||
            config.url?.includes("/logout")
          ) {
            return config;
          }

          const storedToken = localStorage.getItem("token");
          if (storedToken) {
            config.headers.Authorization = `Bearer ${storedToken}`;
          }

          return config;
        },
        (error) => Promise.reject(error)
      );

      // 응답 인터셉터 설정
      responseInterceptor = axios.interceptors.response.use(
        (response) => response,
        async (error) => {
          const originalRequest = error.config;

          // 401 에러이고 재시도하지 않은 요청이며 인증 관련 요청이 아닌 경우
          if (
            error.response?.status === 401 &&
            !originalRequest._retry &&
            !originalRequest.url?.includes("/login") &&
            !originalRequest.url?.includes("/refresh-token") &&
            !originalRequest.url?.includes("/logout") &&
            !isRefreshing.current
          ) {
            originalRequest._retry = true;

            try {
              const refreshed = await refreshToken();
              if (refreshed) {
                const newToken = localStorage.getItem("token");
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return axios(originalRequest);
              }
            } catch (refreshError) {
              console.error(
                "Error refreshing token in interceptor:",
                refreshError
              );
            }
          }

          return Promise.reject(error);
        }
      );

      // 클린업 함수
      return () => {
        if (requestInterceptor !== null) {
          axios.interceptors.request.eject(requestInterceptor);
        }
        if (responseInterceptor !== null) {
          axios.interceptors.response.eject(responseInterceptor);
        }
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    },
    [
      /* 의존성 배열을 비워두고 ESLint 경고 비활성화 */
    ]
  );

  // 토큰 만료 체크 및 자동 갱신
  useEffect(() => {
    if (!token) return;

    const checkTokenExpiration = () => {
      const storedToken = localStorage.getItem("token");
      if (storedToken && !isTokenValid(storedToken) && !isRefreshing.current) {
        console.log("Token expired, attempting refresh");
        refreshToken();
      }
    };

    // 5분마다 토큰 만료 체크
    const intervalId = setInterval(checkTokenExpiration, 5 * 60 * 1000);

    return () => clearInterval(intervalId);
  }, [token, isTokenValid, refreshToken]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        getAuthHeaders,
        refreshToken,
        isTokenValid,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
