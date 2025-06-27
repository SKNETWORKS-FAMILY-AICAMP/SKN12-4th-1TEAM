import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// 마크다운 컴포넌트 스타일 정의
const MarkdownComponents = {
  // 각 마크다운 요소에 대한 스타일 정의
  p: ({ children, ...props }) => (
    <p className="markdown-content" {...props}>
      {children}
    </p>
  ),
  h1: ({ children, ...props }) => (
    <h1 className="markdown-content" {...props}>
      {children}
    </h1>
  ),
  h2: ({ children, ...props }) => (
    <h2 className="markdown-content" {...props}>
      {children}
    </h2>
  ),
  h3: ({ children, ...props }) => (
    <h3 className="markdown-content" {...props}>
      {children}
    </h3>
  ),
  h4: ({ children, ...props }) => (
    <h4 className="markdown-content" {...props}>
      {children}
    </h4>
  ),
  ul: ({ children, ...props }) => (
    <ul className="markdown-content" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }) => (
    <ol className="markdown-content" {...props}>
      {children}
    </ol>
  ),
  li: ({ children, ...props }) => (
    <li className="markdown-content" {...props}>
      {children}
    </li>
  ),
  a: ({ children, ...props }) => (
    <a className="markdown-content" {...props}>
      {children}
    </a>
  ),
  blockquote: ({ children, ...props }) => (
    <blockquote className="markdown-content" {...props}>
      {children}
    </blockquote>
  ),
  pre: ({ children, ...props }) => (
    <pre className="markdown-content" {...props}>
      {children}
    </pre>
  ),
  code: ({ node, inline, children, ...props }) =>
    inline ? (
      <code className="markdown-content" {...props}>
        {children}
      </code>
    ) : (
      <code className="markdown-content block" {...props}>
        {children}
      </code>
    ),
  table: ({ children, ...props }) => (
    <table className="markdown-content" {...props}>
      {children}
    </table>
  ),
  tr: ({ children, ...props }) => (
    <tr className="markdown-content" {...props}>
      {children}
    </tr>
  ),
  th: ({ children, ...props }) => (
    <th className="markdown-content" {...props}>
      {children}
    </th>
  ),
  td: ({ children, ...props }) => (
    <td className="markdown-content" {...props}>
      {children}
    </td>
  ),
};

const ChatHistory = ({ selectedChat, onSelectChat, onNewChat }) => {
  const chatHistory = [
    { id: 1, title: "말티즈 제주도 숙소 추천" },
    { id: 2, title: "지하철 이용" },
  ];

  return (
    <div className="flex flex-col h-full">
      <button
        onClick={onNewChat}
        className="flex items-center gap-2 px-2 py-3 text-white/90 hover:text-white"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path
            d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
            fill="#FFFFFF"
            fillOpacity="0.9"
          />
        </svg>
        <span className="text-lg">새 채팅</span>
      </button>
      <div className="text-left text-gray-400 text-lg px-2 my-5">채팅 내역</div>
      <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
        {chatHistory.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat(chat)}
            className={`text-left text-lg w-full py-2 px-2 rounded hover:bg-white/10 transition-colors ${
              selectedChat?.id === chat.id ? "text-white" : "text-white/90"
            }`}
          >
            {chat.title}
          </button>
        ))}
      </div>
    </div>
  );
};

const ChatbotInterface = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [selectedChat, setSelectedChat] = useState(null);
  const [chatId, setChatId] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleNewChat = () => {
    const newChatId = chatId + 1;
    setChatId(newChatId);
    setMessages([]);
    setSelectedChat(null);
    setInputMessage("");
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      isBot: false,
    };

    setMessages([...messages, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // 백엔드 API 호출
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: userMessage.text }),
      });

      if (!response.ok) {
        throw new Error("API 요청 실패");
      }

      const data = await response.json();

      const botResponse = {
        id: messages.length + 2,
        text: data.response || "죄송합니다, 응답을 받지 못했습니다.",
        isBot: true,
      };

      setMessages((prev) => [...prev, botResponse]);
    } catch (error) {
      console.error("Error:", error);

      const errorResponse = {
        id: messages.length + 2,
        text: "죄송합니다. 서버와의 연결에 문제가 발생했습니다.",
        isBot: true,
      };

      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex">
      {/* Left Sidebar */}
      <div className="w-[300px] bg-[#141944] flex flex-col h-screen">
        <div className="flex items-center gap-4 p-4">
          <button
            onClick={() => navigate("/")}
            className="text-white/90 text-base hover:text-white"
          >
            ← 홈으로
          </button>
        </div>
        <div className="flex flex-col items-center mb-4">
          <img
            src="/images/chatbot/chatbot-logo.png"
            alt="Chatbot Logo"
            className="w-[120px] h-[120px] rounded-full"
          />
        </div>
        <div className="flex-1 min-h-0 px-4">
          <ChatHistory
            selectedChat={selectedChat}
            onSelectChat={setSelectedChat}
            onNewChat={handleNewChat}
          />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 bg-[#C1C9D9]">
        <div className="h-screen flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <div className="space-y-4 py-6">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-10">
                  <p>반려동물 여행 챗봇에 오신 것을 환영합니다!</p>
                  <p>무엇이든 물어보세요.</p>
                </div>
              )}
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.isBot ? "justify-start pl-6" : "justify-end pr-6"
                  }`}
                >
                  <div
                    className={`${
                      message.isBot
                        ? "bg-[#141944]/65 text-white/80 rounded-[16px]"
                        : "bg-white text-black/90 rounded-[16px]"
                    } max-w-[500px] p-4 text-base text-left`}
                  >
                    {message.isBot ? (
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={MarkdownComponents}
                      >
                        {message.text}
                      </ReactMarkdown>
                    ) : (
                      message.text
                    )}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start pl-6">
                  <div className="bg-[#141944]/50 text-black/90 rounded-[16px] max-w-[500px] p-4 text-base">
                    <div className="flex items-center space-x-2">
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "0s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"
                        style={{ animationDelay: "0.4s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="p-6 bg-[#C1C9D9]">
            <form onSubmit={handleSendMessage}>
              <div className="relative">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="무엇이든 물어보세요"
                  className="w-full h-[50px] bg-white rounded-[16px] pl-4 pr-12 text-base text-gray-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  className="absolute right-3 top-1/2 -translate-y-1/2"
                  disabled={isLoading}
                >
                  <img
                    src="/images/chatbot/send-icon.png"
                    alt="Send"
                    className="w-[30px] h-[30px]"
                  />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotInterface;
