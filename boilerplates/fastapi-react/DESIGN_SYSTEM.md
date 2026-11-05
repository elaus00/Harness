# Harness 디자인 시스템

참조: [Atlassian 디자인 토큰](https://atlassian.design/foundations/design-tokens). Jira의 정보 밀도, 파란 선택 상태, 상단 바와 좌측 탐색, 업무 테이블을 개인 작업 공간에 적용한다.

## 기반

`@atlaskit/tokens`의 light theme을 `src/main.tsx`에서 로드한다. Atlassian 내부 실험 플래그는 로컬 resolver의 false 기본값으로 처리하며 외부 실험 서비스는 사용하지 않는다.

`src/App.css`의 색·배경·구분선·focus·간격·radius 변수는 `--ds-*` 토큰에 연결한다. 프로젝트 식별 색과 도메인 상태 색은 로컬 보조색이다. 시스템 글꼴을 사용하며 외부 글꼴 요청은 없다.

## 공통 컴포넌트

`src/components/ui.tsx`: Brand, Button(default/primary/subtle), TextField, Avatar, StatusBadge. Atlassian 토큰을 사용하는 로컬 React 컴포넌트이며 Atlaskit 전체 컴포넌트 라이브러리를 설치한 것은 아니다.

## 화면 규칙

- 로그인: 이름·이메일·비밀번호 폼, 입력 검증, 대기·오류 상태.
- 대시보드: 실제 업무 수 집계, 프로젝트 진행률, 검색·상태·프로젝트 필터, 활동.
- 업무 생성: native dialog의 포커스 관리·Escape·취소·저장 상태.
- 모바일: 메뉴 접기, 프로젝트 카드 세로 정렬, 테이블 내부 스크롤. 핵심 업무 기능 유지.
- 키보드 focus, label, 상태 텍스트, aria-live와 reduced-motion 적용.

계정별 프로젝트 분류는 기본 세 가지로 고정되어 있다. 프로젝트 생성과 팀 관리가 필요하면 데이터 모델부터 확장한다.
