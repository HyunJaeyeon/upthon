from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Dict, Any

# .env 로드
load_dotenv()

class TextImprover:
    def __init__(self, api_key: str = None):
        """
        Upstage solar-pro2 모델을 사용하는 문장 개선기
        """
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("UPSTAGE_API_KEY가 설정되지 않았습니다.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.upstage.ai/v1"
        )

    def generate_text_options(self, original_text: str, context: Dict[str, str] = None, num_options: int = 3) -> Dict[str, Any]:
        """
        원문을 받아서 여러 개의 개선된 문장 옵션들을 반환
        """
        try:
            # 컨텍스트 정보가 있으면 더 구체적인 프롬프트 생성
            if context:
                context_str = ""
                if context.get('grade') and context.get('semester'):
                    context_str += f"- 대상: {context['grade']}학년 {context['semester']}학기\n"
                if context.get('subject'):
                    context_str += f"- 과목: {context['subject']}\n"
                if context.get('unit'):
                    context_str += f"- 단원: {context['unit']}\n"
                if context.get('domain'):
                    context_str += f"- 영역: {context['domain']}\n"
                if context.get('criteria'):
                    context_str += f"- 성취기준: {context['criteria']}\n"

                prompt = f"""다음은 초등학교 교육과정 평가요소 문장입니다.

아래 문장을 더 명확하고 간결하게 다듬어서 {num_options}가지 서로 다른 버전으로 제시해 주세요.

단, 다음 기준을 반드시 지켜 주세요:
1. 말투는 그대로 유지해 주세요. (예: '~을 실천하기', '~을 기르기', '~을 이해하기' 등의 형태로 끝나야 합니다.)
2. 각 옵션은 한 문장으로만 작성해 주세요.
3. 각 옵션은 서로 다른 관점이나 표현으로 작성해 주세요.
4. 번호나 '옵션 1:', '개선된 문장:' 등의 불필요한 문구는 포함하지 마세요.
5. 각 문장은 줄바꿈으로 구분해 주세요.

교육과정 정보:
{context_str}

원문 문장:
{original_text}
"""

            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # 다양성을 위해 조금 높임
                max_tokens=1024,
                stream=False,
                reasoning_effort="high"
            )

            improved_text = response.choices[0].message.content.strip()
            
            # 줄바꿈으로 분리하여 옵션들 추출
            options = [line.strip() for line in improved_text.split('\n') if line.strip()]
            
            # 정확히 num_options 개수만큼 반환 (부족하면 원문 기반으로 추가 생성)
            if len(options) < num_options:
                # 부족한 경우 간단한 변형 추가
                while len(options) < num_options:
                    options.append(original_text)
            elif len(options) > num_options:
                # 너무 많은 경우 처음 num_options개만 선택
                options = options[:num_options]

            return {
                "success": True,
                "original": original_text,
                "options": options
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def improve_text(self, original_text: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """
        원문을 받아서 더 명확하고 자연스럽게 개선된 문장 반환
        context: 학년, 학기, 과목, 단원명, 성취기준, 영역 정보
        """
        try:
            # 컨텍스트 정보가 있으면 더 구체적인 프롬프트 생성
            if context:
                context_str = ""
                if context.get('grade') and context.get('semester'):
                    context_str += f"- 대상: {context['grade']}학년 {context['semester']}학기\n"
                if context.get('subject'):
                    context_str += f"- 과목: {context['subject']}\n"
                if context.get('unit'):
                    context_str += f"- 단원: {context['unit']}\n"
                if context.get('domain'):
                    context_str += f"- 영역: {context['domain']}\n"
                if context.get('criteria'):
                    context_str += f"- 성취기준: {context['criteria']}\n"

                prompt = f"""다음은 초등학교 교육과정 평가요소 문장입니다.

아래 문장을 더 명확하고 간결하게 다듬어 주세요.

단, 다음 기준을 반드시 지켜 주세요:
1. 말투는 그대로 유지해 주세요. (예: '~을 실천하기', '~을 기르기', '~을 이해하기' 등의 형태로 끝나야 합니다.)
2. 한 문장으로만 출력해 주세요.
3. 평가 문장 외에 불필요한 설명, 개선 이유, '개선된 문장:' 등의 문구는 포함하지 마세요.

교육과정 정보:
{context_str}

원문 문장:
{original_text}
"""

            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=False,
                reasoning_effort="high"
            )

            improved = response.choices[0].message.content.strip()

            return {
                "success": True,
                "original": original_text,
                "improved": improved
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_evaluation_criteria(self, evaluation_element: str, original_criteria: Dict[str, str], context: Dict[str, str] = None) -> Dict[str, Any]:
        """
        평가요소를 기반으로 4단계 평가기준(매우잘함, 잘함, 보통, 노력요함)을 생성
        """
        try:
            # 컨텍스트 정보 구성
            context_str = ""
            if context:
                if context.get('grade') and context.get('semester'):
                    context_str += f"- 대상: {context['grade']}학년 {context['semester']}학기\n"
                if context.get('subject'):
                    context_str += f"- 과목: {context['subject']}\n"
                if context.get('unit'):
                    context_str += f"- 단원: {context['unit']}\n"
                if context.get('domain'):
                    context_str += f"- 영역: {context['domain']}\n"
                if context.get('criteria'):
                    context_str += f"- 성취기준: {context['criteria']}\n"

            # 기존 평가기준 분석을 위한 정보
            original_str = ""
            levels = ['매우잘함', '잘함', '보통', '노력요함']
            for level in levels:
                if original_criteria.get(level):
                    original_str += f"- {level}: {original_criteria[level]}\n"

            prompt = f"""다음은 초등학교 교육과정 평가기준을 생성하는 작업입니다.

교육과정 정보:
{context_str}

평가요소: {evaluation_element}

기존 평가기준 (참고용 - 정도와 스타일 참조):
{original_str}

위 정보를 바탕으로 새로운 평가요소에 맞는 4단계 평가기준을 생성해 주세요.

요구사항:
1. 기존 평가기준의 난이도 정도와 문체를 유지해 주세요
2. 새로운 평가요소의 내용에 맞게 구체적으로 작성해 주세요
3. 각 단계별로 명확한 차이가 있도록 해주세요
4. {context['grade']}학년 {context['semester']}학기 수준에 맞는 평가 내용으로 작성해 주세요
5. 각 기준은 한 문장으로 작성해 주세요

출력 형식 (정확히 이 형식으로):
매우잘함: [평가기준 내용]
잘함: [평가기준 내용]  
보통: [평가기준 내용]
노력요함: [평가기준 내용]"""

            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=False,
                reasoning_effort="high"
            )

            result_text = response.choices[0].message.content.strip()
            
            # 결과 파싱
            criteria = {}
            lines = result_text.split('\n')
            for line in lines:
                line = line.strip()
                for level in levels:
                    if line.startswith(f"{level}:"):
                        criteria[level] = line.replace(f"{level}:", "").strip()
                        break

            return {
                "success": True,
                "criteria": criteria
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_single_criteria(self, level: str, evaluation_element: str, original_text: str, context: Dict[str, str] = None) -> Dict[str, Any]:
        """
        특정 평가 수준(매우잘함, 잘함 등)에 대한 단일 평가기준 생성
        """
        try:
            # 컨텍스트 정보 구성
            context_str = ""
            if context:
                if context.get('grade') and context.get('semester'):
                    context_str += f"- 대상: {context['grade']}학년 {context['semester']}학기\n"
                if context.get('subject'):
                    context_str += f"- 과목: {context['subject']}\n"
                if context.get('unit'):
                    context_str += f"- 단원: {context['unit']}\n"
                if context.get('domain'):
                    context_str += f"- 영역: {context['domain']}\n"

            prompt = f"""다음은 초등학교 교육과정 평가기준을 생성하는 작업입니다.

교육과정 정보:
{context_str}

평가요소: {evaluation_element}
평가 수준: {level}
기존 {level} 기준 (참고용): {original_text}

위 정보를 바탕으로 새로운 평가요소에 맞는 '{level}' 수준의 평가기준을 생성해 주세요.

요구사항:
1. 기존 평가기준의 난이도 정도와 문체를 유지해 주세요
2. 새로운 평가요소의 내용에 맞게 구체적으로 작성해 주세요
3. '{level}' 수준에 적합한 내용으로 작성해 주세요
4. 초등학생 수준에 맞는 평가 내용으로 작성해 주세요
5. 한 문장으로 작성해 주세요
6. 평가기준 내용만 출력하고 다른 설명은 포함하지 마세요

{level} 평가기준:"""

            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512,
                stream=False,
                reasoning_effort="high"
            )

            criteria = response.choices[0].message.content.strip()

            return {
                "success": True,
                "criteria": criteria
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }