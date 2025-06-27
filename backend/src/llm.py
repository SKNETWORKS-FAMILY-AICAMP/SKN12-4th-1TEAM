""" Pet Travel Chatbot System"""
import logging
import traceback
from typing import Dict, List, Optional, Any
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import vector_manger as vm
from module import get_category, get_user_parser, get_naver_map_link
from weather import get_weather, get_current_time
from app.models.db import get_db
from app.models.chat import ChatLog

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 후보 장소 개수 설정
candiate_num = None

class Chatbot: # 챗봇 클래스
    """ Pet Travel Chatbot"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key, temperature=0.3)
        logger.info(" Chatbot initialized")
    
    def process_query(self, query: str, session_id: Optional[int] = None, stream: bool = False) -> str:
        """Main processing pipeline"""
        try:
            # Check greetings first
            greeting_response = self.check_greeting(query)
            if greeting_response:
                return greeting_response
            
            # 이전 대화 내역 가져오기
            chat_history = []
            if session_id:
                chat_history = self._get_chat_history(session_id)
            
            # Analyze query
            categories = get_category(query)
            user_parsed = get_user_parser(query)
            
            # Search VectorDB
            results = vm.multiretrieve_by_category(query=query, categories=categories, k_each=10, top_k=10)
            
            # Handle weather separately
            if "날씨" in categories:
                region = user_parsed.get("region")
                # If the travel parser didn't find a region, try weather-specific parsing
                if not region or region == "" or region == "null":
                    region = self._extract_weather_region(query)
                
                if region:
                    results["날씨"] = self._get_weather_info(region)
                else:
                    results["날씨"] = [Document(page_content="지역을 명시해주세요. (예: 서울 날씨, 부산 날씨)", metadata={})]
            
            # Generate response
            return self._generate_response(query, user_parsed, results, chat_history)
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return "죄송합니다. 요청을 처리하는 중 오류가 발생했습니다."
    
    def _get_chat_history(self, session_id: int) -> List[Dict[str, str]]:
        """세션 ID에 해당하는 이전 대화 내역을 가져옵니다."""
        try:
            # DB 세션 가져오기
            db = next(get_db())
            
            # 최근 대화 내역 5개 가져오기
            messages = db.query(ChatLog).filter(
                ChatLog.session_id == session_id
            ).order_by(ChatLog.timestamp.desc()).limit(5).all()
            
            # 시간순으로 정렬
            messages = sorted(messages, key=lambda x: x.timestamp)
            
            # 대화 내역 형식 변환
            chat_history = []
            for msg in messages:
                chat_history.append({
                    "role": "user" if msg.sender == "user" else "assistant",
                    "content": msg.message
                })
            
            return chat_history
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def generate_title(self, first_message: str) -> str:
        """사용자의 첫 메시지를 기반으로 채팅 세션의 제목을 생성합니다."""
        try:
            template = """
            사용자의 첫 메시지를 기반으로 채팅 세션의 제목을 생성해주세요.
            제목은 간결하게 핵심 키워드를 포함하여 20자 이내로 작성해주세요.
            따옴표나 특수문자 없이 순수한 텍스트로만 작성해주세요.
            
            예시:
            - 사용자: "제주도에 반려견과 함께 여행 가고 싶어요" -> 제주도 반려견 여행
            - 사용자: "서울에서 애견 동반 가능한 카페 추천해주세요" -> 서울 애견 동반 카페
            - 사용자: "부산 해운대 날씨 어때?" -> 부산 해운대 날씨
            
            사용자 메시지: {message}
            
            제목: 
            """
            
            prompt = PromptTemplate.from_template(template)
            chain = prompt | self.llm | StrOutputParser()
            
            title = chain.invoke({"message": first_message})
            # 따옴표 제거
            title = title.strip().replace('"', '').replace("'", '')
            return title
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            return "새 채팅"  # 오류 발생 시 기본 제목 반환
    
    def check_greeting(self, query: str) -> Optional[str]:
        """Check for greetings"""
        greetings = ["안녕", "안녕하세요", "hello", "hi"]
        query_lower = query.lower().strip()
        
        if any(greeting in query_lower for greeting in greetings):
            return """# 안녕하세요! 🐶 반려동물 여행 전문 도우미입니다.
                        
## 다음과 같은 도움을 드릴 수 있어요:
* 🗺️ 반려동물 동반 가능한 관광지 추천
* 🏨 펜션, 호텔 등 숙박시설 안내  
* 🚌 대중교통 이용 규정 안내
* ☀️ 여행지 날씨 정보
* 🐾 반려동물 동반 가능한 미용실, 동물병원, 애견용품점, 쇼핑물 등 추천
                        
**예시**: "제주도에 강아지랑 2박 3일 여행 가고 싶어"

어떤 여행을 계획하고 계신가요? 😊"""
        return None
    
    def _get_weather_info(self, region: str) -> List[Document]:
        """Get weather information"""
        try:
            weather_data = get_weather(region)
            current_time = get_current_time()
            
            if "error" not in weather_data:
                content = f"""## 현재 시간: {current_time['full_datetime']}
* **도시**: {weather_data['city']}
* **기온**: {weather_data['temperature']}°C
* **습도**: {weather_data['humidity']}%
* **강수형태**: {weather_data['precipitation_type']}
* **풍속**: {weather_data['wind_speed']} m/s"""
                return [Document(page_content=content, metadata=weather_data)]
            else:
                # 날씨 정보를 가져오지 못한 경우 기본 응답 제공
                logger.warning(f"날씨 정보 조회 실패: {weather_data.get('error', '알 수 없는 오류')}")
                
                # no_data 필드가 있으면 기상청 API가 데이터를 제공하지 않는 경우
                if weather_data.get('no_data', False):
                    content = f"""## 현재 시간: {current_time['full_datetime']}
* **도시**: {region}
* **날씨 정보**: 현재 기상청에서 제공하는 데이터가 없습니다.

반려동물과 외출 시에는 항상 다음 사항을 주의해 주세요:

1. 충분한 물을 준비해 수시로 수분을 공급해 주세요.
2. 더운 날씨에는 아스팔트 온도를 확인하고 발바닥 화상에 주의하세요.
3. 비가 올 경우 반려동물용 우비나 수건을 준비하세요.
4. 외출 전후에 반려동물의 상태를 확인해 주세요."""
                else:
                    content = f"""## 현재 시간: {current_time['full_datetime']}
* **도시**: {region}
* **기온**: 정보 조회 실패
* **습도**: 정보 조회 실패
* **강수형태**: 정보 조회 실패
* **풍속**: 정보 조회 실패

죄송합니다만, 현재 날씨 정보를 제공하는 서비스에 일시적인 문제가 있습니다.
하지만 반려동물과의 외출 시 항상 다음 사항을 주의해 주세요:

1. 충분한 물을 준비해 수시로 수분을 공급해 주세요.
2. 더운 날씨에는 아스팔트 온도를 확인하고 발바닥 화상에 주의하세요.
3. 비가 올 경우 반려동물용 우비나 수건을 준비하세요.
4. 외출 전후에 반려동물의 상태를 확인해 주세요."""
                
                # city 필드가 있으면 사용하고, 없으면 입력받은 region 사용
                city = weather_data.get('city', region)
                return [Document(page_content=content, metadata={"city": city})]
        except Exception as e:
            logger.error(f"Weather error: {str(e)}")
            current_time = get_current_time()
            content = f"""## 현재 시간: {current_time['full_datetime']}
* **도시**: {region}
* **날씨 정보**: 일시적으로 제공할 수 없습니다.

반려동물과 외출 시에는 항상 기상 상황을 확인하고 적절한 준비를 하시기 바랍니다."""
            return [Document(page_content=content, metadata={"city": region})]
    
    def _analyze_query_categories(self, query: str) -> List[str]:
        """Analyze query and detect relevant categories"""
        try:
            return get_category(query)
        except Exception as e:
            logger.error(f"Error analyzing categories: {str(e)}")
            return ["관광지"]
    
    def _search_vector_db(self, query: str, categories: List[str]) -> Dict[str, List[Document]]:
        """Search vector database for each category"""
        try:
            return vm.multiretrieve_by_category(query=query, categories=categories, k_each=10, top_k=10)
        except Exception as e:
            logger.error(f"Error searching vector DB: {str(e)}")
            return {}
    
    def _generate_response(self, query: str, user_parsed: Dict[str, Any], 
                        results: Dict[str, List[Document]], chat_history: List[Dict[str, str]] = None) -> str:
        """Generate final response"""
        content_sections = []
        
        for category, docs in results.items():
            if not docs:
                continue
                
            category_content = f"## {category} 정보\n"
            
            for i, doc in enumerate(docs, 1):
                metadata = doc.metadata
                place_name = metadata.get("title", f"장소 {i}")
                map_link = get_naver_map_link(place_name) if place_name != f"장소 {i}" else "#"
                
                place_info = f"### {i}. [{place_name}]({map_link})\n"
                place_info += doc.page_content + "\n\n"
                category_content += place_info
            
            content_sections.append(category_content)
        
        content = "\n".join(content_sections)
        
        # 대화 히스토리 포맷팅
        chat_history_text = ""
        if chat_history and len(chat_history) > 0:
            chat_history_text = "## 이전 대화 내역\n"
            for msg in chat_history:
                role = "사용자" if msg["role"] == "user" else "챗봇"
                chat_history_text += f"**{role}**: {msg['content']}\n\n"
        
        template ="""
당신은 반려동물과의 여행을 도와주는 감성적인 여행 플래너, 가이드 입니다.  
아래 정보에 따라 **정확히 '장소 질의'인지, '날씨 응답'인지, '여행 코스 요청'인지 구분하여 답변**하세요.

---
🧾 사용자 질문: {query}  
📍 지역: {region}  
🐕 반려동물: {pet_type}  
🗓️ 여행 기간: {days}일  

{chat_history}

🔍 제공된 정보:  
{content}
---

🎯 작성 지침:

1. **사용자가 특정 장소(G2, OO카페 등)의 위치나 정체를 묻는 질문**인 경우에는  
    - 장소 이름, 위치, 간단한 설명, 지도 링크를 포함하세요.
    - *장소가 DB에 없으면 ‘정확한 정보를 찾기 어려워요’라고 말해주세요.*
    - **여행 일정이나 날씨 정보는 절대 포함하지 마세요.**
    - 예시:
    
    ### 📍 G2 (부산 영도)
    - 위치: 부산광역시 영도구 동삼동 123-4
    - 설명: 영도 해양과학기술원 근처에 위치한 문화 복합공간입니다.
    - 지도 링크: [네이버지도에서 보기](https://map.naver.com/v5/search/G2%20영도)

2. **사용자가 '날씨'만 요청한 경우에는**,  
    - 해당지역 기온/날씨/풍속/습도 + 반려동물 외출 시 유의사항 포함  
    - 날씨 외 정보는 작성하지 마세요
    - 예시는 다음과 같아요:

    # 서울 날씨 정보

    ## 🌤️ 오늘의 서울 날씨
    * 🌡️ **기온**: 18.5°C
    * 💧 **습도**: 55%
    * 🌬️ **바람**: 1.5 m/s
    * 🌤️ **날씨 상태**: 맑음

    맑고 산뜻한 날씨네요!  
    반려동물과 외출하시기 좋은 날이에요. 🐶💕

    ## 🐾 외출 시 주의사항
    * 햇빛이 강할 수 있으니 **그늘에서 쉬는 시간**을 자주 주세요.
    * **수분 보충**을 위해 물을 꼭 챙겨주세요.
    * **뜨거운 아스팔트**로부터 발바닥을 보호해 주세요.

3. **'여행 코스' 요청일 경우에는** `## 🐾 1일차, 2일차` 등으로 일정 구성  
    - 오전 → 점심 → 오후 → 저녁 순서
    - 각 장소는 이름 + 설명 + 반려동물 동반 여부

4. **날씨 + 여행 일정이 모두 포함된 경우**  
    👉 먼저 날씨 정보를 출력하고 → 아래에 여행 일정을 이어서 작성

5. **숙소 추천이 필요한 경우**,  
    - 마지막 또는 별도 섹션에 `## 🏨 숙소 추천` 제목으로 정리  
    - 숙소명, 위치, 반려동물 동반 여부, 특징, 추가요금 여부

6. 전체 말투는 따뜻하고 친근하게. 여행을 함께 준비하는 친구처럼 작성해주세요.

7. 🐾, 🌳, 🍽️, 🐶, ✨ 등의 이모지를 적절히 활용해 가독성과 감성을 살려주세요.

8. 마지막에는 감성적인 인사로 마무리해주세요.  
    - 예: "반려견과 함께하는 이번 여행이 오래도록 기억에 남기를 바랍니다! 🐕💕"

9. 모든 응답은 마크다운 형식으로 작성해주세요.  
   - 제목은 #, ##, ### 등을 사용하고, 목록은 *, - 등을 사용하세요.  
   - 강조가 필요한 부분은 **강조** 또는 *기울임*을 사용하세요.

10. 이전 대화 내역이 있다면 그 내용을 참고하여 더 연속성 있고 맥락에 맞는 답변을 제공해주세요.
    - 사용자가 이전에 언급한 선호도, 장소, 반려동물 정보 등을 기억하고 활용하세요.
"""
        prompt = PromptTemplate.from_template(template)
        inputs = {
            "query": query,
            "region": user_parsed.get("region", "정보 없음"),
            "pet_type": user_parsed.get("pet_type", "정보 없음"),
            "days": user_parsed.get("days", "정보 없음"),
            "content": content or "관련 정보를 찾을 수 없습니다.",
            "chat_history": chat_history_text
        }
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(inputs)

    def _extract_weather_region(self, query: str) -> Optional[str]:
        """Extract region from weather queries using simple parsing"""
        import re
        
        # Common weather keywords and modifiers to exclude
        weather_keywords = ["날씨", "기온", "온도", "비", "눈", "바람", "습도", "맑", "흐림", "현재", "지금", "오늘", "내일", "어때"]
        
        # Check if it's a weather query
        if not any(keyword in query for keyword in ["날씨", "기온", "온도"]):
            return None
            
        # Simple region extraction patterns - prioritize patterns that come before weather keywords
        city_patterns = [
            r'([가-힣]+(?:시|구|군|도))\s*(?:의\s*)?(?:날씨|기온|온도|현재)',  # 서울시 날씨, 강남구 날씨
            r'([가-힣]+)\s*(?:의\s*)?(?:날씨|기온|온도)',      # 서울 날씨, 서울의 날씨
            r'([가-힣]+)\s+(?:현재|지금)',                    # 서울 현재, 부산 지금
        ]
        
        for pattern in city_patterns:
            match = re.search(pattern, query)
            if match:
                candidate = match.group(1)
                if candidate not in weather_keywords:
                    return candidate
        
        # Fallback: find the first meaningful Korean word that's not a weather keyword
        words = re.findall(r'[가-힣]+', query)
        for word in words:
            if word not in weather_keywords and len(word) >= 2:
                return word
                
        return None

# Global instance
chatbot = None

def get_chatbot() -> Chatbot:
    """Get global  chatbot instance"""
    global chatbot
    if chatbot is None:
        chatbot = Chatbot()
    return chatbot


def process_query(query: str, session_id: Optional[int] = None, stream: bool = False) -> str:
    """Process query using  chatbot"""
    chatbot = get_chatbot()
    return chatbot.process_query(query, session_id, stream)


def check_greeting(query: str) -> Optional[str]:
    """Check for greetings"""
    chatbot = get_chatbot()
    return chatbot.check_greeting(query)
