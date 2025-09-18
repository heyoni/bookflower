# 📱 모바일 우선 독서 플랫폼 개발 요청 가이드

> **책바라기(Book Flower)** 프로젝트와 동일한 구조를 얻기 위한 완벽한 요청 가이드

## 🎯 한 번의 완벽한 요청 예시

```markdown
Django 5.2와 Tailwind CSS로 '책바라기(Book Flower)'라는 모바일 우선 독서 기록 플랫폼을 만들어줘.

## 🎯 프로젝트 개요
- 이름: 책바라기 (Book Flower)
- 컨셉: 독서량에 따라 해바라기가 성장하는 게이미피케이션 독서 플랫폼
- 타겟: 모바일 우선 (PWA 스타일)
- 스택: Django 5.2, SQLite, Tailwind CSS

## 📱 핵심 기능

### 1. 독서 기록 시스템
- **페이지 기반 기록**: 시간 측정 없음, 자유롭게 읽은 페이지 수 입력
- **포인트 시스템**: 1페이지 = 1포인트 자동 적립
- **독서 완료**: 세션 단위로 독서 기록 관리

### 2. 해바라기 성장 시각화
- 새싹 단계: 0-99P (🌱)
- 성장 단계: 100-499P (🌿)
- 꽃 단계: 500-999P (🌻)
- 만개 단계: 1000P+ (🌻✨)
- 실시간 성장 진행률 표시

### 3. 노트 및 독후감
- **독서 노트**: 페이지별 메모 작성 가능
- **AI 독후감**: 작성한 노트를 바탕으로 AI가 자동 독후감 생성
- **독후감 관리**: 책별 독후감 모아보기

### 4. 도서 관리
- **책 검색**: 로컬 DB + 외부 API 통합 (Mock 구현)
- **내 서재**: 읽은 책, 읽고 있는 책 관리
- **책 정보**: 제목, 저자 기본 정보

## 🏗️ 앱 구조

### accounts
- CustomUser 모델 (AbstractUser 확장)
- 포인트 필드 추가 (points = models.IntegerField(default=0))
- 배지 시스템 (JSON 필드)
- 로그인/회원가입 모바일 최적화

### books
- Book 모델 (title, author)
- 책 검색 기능
- 서재 관리

### reading
- ReadingSession 모델 (pages_read, earned_points, completed)
- Note 모델 (page_until, note)
- 독서 시작/진행/완료 플로우

### reviews
- Review 모델 (content, generated_by_ai)
- AI 독후감 생성 (Mock)
- 독후감 목록 및 상세

## 🎨 UI/UX 디자인 요구사항

### 모바일 우선 디자인
- 반응형 디자인 (Mobile First)
- Tailwind CSS 활용
- 최소 터치 영역: 44px × 44px
- 16px 이상 폰트 사이즈 (iOS 줌 방지)

### 네비게이션 구조
- **고정 헤더**: 햄버거 메뉴, 로고, 포인트 표시
- **하단 네비게이션**: 홈, 검색, 기록, 독후감 (4개 탭)
- **햄버거 메뉴**: 전체 메뉴 접근

### 컬러 테마 (해바라기 테마)
- Primary: 노란색 계열 (#ffc107, #ffda6a)
- Secondary: 초록색 계열 (#198754, #75b798)
- Gradient: sunflower-gradient, leaf-gradient
- 배경: from-yellow-50 to-green-50

### 컴포넌트 스타일
- **카드**: mobile-card (rounded-xl, shadow, p-4)
- **버튼**: mobile-button (min-height: 48px, rounded-xl)
- **터치 피드백**: active:scale(0.98) transform
- **모달**: 모바일 최적화 (backdrop-blur)

## 📊 데이터 모델 상세

### User (AbstractUser 확장)
```python
class User(AbstractUser):
    points = models.IntegerField(default=0)
    badges = models.JSONField(default=list)
```

### Book
```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True)
```

### ReadingSession
```python
class ReadingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    pages_read = models.IntegerField(default=0)
    earned_points = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Note
```python
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page_until = models.IntegerField(null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Review
```python
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, unique_together=['user', 'book'])
    content = models.TextField()
    generated_by_ai = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🔄 사용자 플로우

### 1. 온보딩
1. 회원가입 → 로그인
2. 대시보드 (해바라기 새싹 상태)
3. "독서 시작하기" 안내

### 2. 독서 기록
1. 책 검색 또는 직접 입력
2. 독서 세션 시작
3. 읽은 페이지 입력
4. 노트 작성 (선택)
5. 완료 → 포인트 적립

### 3. 독후감 생성
1. 독서 완료 후 "AI 독후감 생성" 버튼
2. 작성한 노트 기반으로 독후감 자동 생성
3. 독후감 확인 및 관리

## 📱 핵심 화면 구성

### 대시보드
- 해바라기 성장 상태 카드 (그라데이션 배경)
- 현재 포인트 & 진행률 바
- 독서 통계 (기록 수, 노트 수)
- 빠른 실행 버튼 (4×2 그리드)
- 최근 활동 리스트

### 독서 시작
- 탭 구조: "최근 읽은 책" / "새 책 추가"
- 책 선택 (라디오 버튼)
- 전체 너비 실행 버튼

### 독서 진행
- 책 정보 카드
- 페이지 수 입력 (실시간 포인트 계산)
- 전체 너비 완료 버튼
- 노트 작성 모달

### 독후감 목록
- 카드 기반 리스트
- AI 생성 배지
- 미리보기 텍스트 (line-clamp-3)
- 터치 친화적 액션 버튼

## ⚡ 기술적 요구사항

### Django 설정
- Django 5.2
- SQLite 데이터베이스
- 한국어 설정 (LANGUAGE_CODE = 'ko-kr')
- 시간대: 'Asia/Seoul'

### CSS 프레임워크
- Tailwind CSS (CDN)
- 커스텀 CSS 클래스
- 모바일 우선 반응형
- 다크 모드 대응 준비

### JavaScript 기능
- 바닐라 JS (라이브러리 최소화)
- 터치 이벤트 최적화
- 모달 관리
- 실시간 UI 업데이트

### 성능 최적화
- 이미지 lazy loading
- 터치 스크롤 최적화
- 최소한의 외부 의존성
- PWA 준비 (viewport, 아이콘 설정)

## 🎨 스타일 가이드

### 타이포그래피
- 헤딩: text-2xl (모바일), text-3xl (데스크톱)
- 본문: text-sm (모바일), text-base (데스크톱)
- 캡션: text-xs
- 한글 폰트 최적화

### 간격
- 컨테이너: px-4 py-6
- 카드 내부: p-4
- 요소 간격: space-y-6, space-y-4, space-y-3
- 마진: mb-3, mb-4, mb-6

### 애니메이션
- 버튼: hover:opacity-90, active:scale(0.98)
- 카드: hover:shadow-xl
- 모달: backdrop-blur-sm
- 부드러운 전환: transition-all duration-200

## 🧪 구현 우선순위

### Phase 1: 핵심 기능
1. User 모델 및 인증
2. 기본 독서 기록 플로우
3. 포인트 시스템
4. 모바일 기본 UI

### Phase 2: 고도화
1. 노트 시스템
2. AI 독후감 (Mock)
3. 해바라기 성장 시각화
4. 통계 및 대시보드

### Phase 3: 완성도
1. 책 검색 시스템
2. 세부 UI 개선
3. 성능 최적화
4. 접근성 개선

모든 템플릿을 모바일 우선으로 구현하고, 터치 친화적인 인터페이스를 만들어줘.
```

## 🔑 핵심 키워드 체크리스트

요청할 때 다음 키워드들을 꼭 포함하세요:

- ✅ **모바일 우선** (Mobile First)
- ✅ **페이지 기반 독서 기록**
- ✅ **1페이지 = 1포인트**
- ✅ **해바라기 성장 시각화**
- ✅ **AI 독후감 생성**
- ✅ **Tailwind CSS**
- ✅ **터치 친화적**
- ✅ **카드 기반 레이아웃**
- ✅ **해바라기 테마 색상**

## 💡 추가 요청 팁

### 더 구체적인 결과를 원할 때:
```
"위 요구사항에 추가로:
- 모든 버튼에 터치 피드백 애니메이션 적용
- iOS Safari 호환성 고려 (줌 방지, 터치 최적화)
- 한 손 조작이 가능한 UI 배치
- 오프라인에서도 기본 기능 동작
- 접근성 (ARIA 라벨, 시맨틱 HTML) 준수"
```

### 특정 기능에 집중하고 싶을 때:
```
"특히 해바라기 성장 시각화에 집중해서:
- 실시간 애니메이션 효과
- 단계별 축하 메시지
- 진행률 바 시각화
- 성취감을 주는 UI/UX"
```

이 가이드를 참고하여 요청하시면 현재 프로젝트와 동일한 수준의 모바일 우선 독서 플랫폼을 얻으실 수 있습니다! 🌻