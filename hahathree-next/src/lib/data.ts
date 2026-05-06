import type { Program, ProgramDetail, Review, SupportPolicy } from '@/types';

export const PROGRAMS: Program[] = [
  {
    id: 1, tag: '회복 프로그램', dDay: 'D-13',
    title: '천천히, 다시 만나는 일상',
    org: '경기 청년센터', status: '모집 중',
    bg: 'var(--card-blue)',
    chips: ['전체 신청 가능', '경기', '온·오프라인'],
    weeks: '8주 · 주 1회', deadline: '마감 2026.05.18',
  },
  {
    id: 2, tag: '온라인 모임', dDay: 'D-5',
    title: '방 안에서 세상으로,\n온라인 살롱',
    org: '나나센터 수원', status: '모집 중',
    bg: 'var(--card-yellow)',
    chips: ['전체 신청 가능', '경기', '온라인'],
    weeks: '4주 · 주 1회', deadline: '마감 2026.05.10',
  },
  {
    id: 3, tag: '월데이', dDay: '곧오픈',
    title: '글쓰기로 나를 정리하는 시간',
    org: '서울 청년허브', status: '모집 예정',
    bg: 'var(--card-orange)',
    chips: ['모집 예정', '서울', '온·오프라인'],
    weeks: '하루 · 4시간', deadline: '마감 2026.06.01',
    statusVariant: 'soon',
  },
  {
    id: 4, tag: '회복 프로그램', dDay: 'D-17',
    title: '식물 돌봄, 나도 돌봄',
    org: '부산 청년정책연구원', status: '모집 중',
    bg: 'var(--card-purple)',
    chips: ['전체 신청 가능', '부산', '오프라인'],
    weeks: '8주 · 주 1회', deadline: '마감 2026.05.22',
  },
  {
    id: 5, tag: '사회 적응', dDay: 'D-10',
    title: '취업 전, 나를\n알아가는 워크숍',
    org: '인천 청년센터', status: '모집 중',
    bg: 'var(--card-mustard)',
    chips: ['전체 신청 가능', '인천', '오프라인'],
    weeks: '8주 · 주 2회', deadline: '마감 2026.05.15',
  },
  {
    id: 6, tag: '온라인 모임', dDay: 'D-25',
    title: '늦은 밤 라디오, 청년 사연함',
    org: '광주 청년재단', status: '모집 중',
    bg: 'var(--card-lemon)',
    chips: ['전체 신청 가능', '광주', '온라인'],
    weeks: '4주 · 주 1회', deadline: '마감 2026.05.30',
  },
  {
    id: 7, tag: '회복 프로그램', dDay: '마감',
    title: '동네 한 바퀴, 산책 클럽',
    org: '대전 청년정책본부', status: '모집 중',
    bg: 'var(--card-pink)',
    chips: ['마감', '대전', '오프라인'],
    weeks: '6주 · 주 1회', deadline: '마감 2026.04.10',
    statusVariant: 'closed',
  },
  {
    id: 8, tag: '온라인 모임', dDay: '곧오픈',
    title: '게임으로 만나는 또래 살롱',
    org: '강원 청년허브', status: '모집 예정',
    bg: 'var(--card-mint)',
    chips: ['모집 예정', '강원', '온라인'],
    weeks: '8주 · 주 1회', deadline: '마감 2026.06.10',
    statusVariant: 'soon',
  },
{   id:9,
    tag: "일경험",
    dDay: "2026-05-01",
    title: "타이틀이 없으면 어떡해",
    org: "두더지땅굴 (사단법인 씨즈)",
    status: "모집 중",bg: 'var(--card-mint)',
    statusVariant: "open",
    chips: [],
    weeks: "5주",
    deadline: "마감 2026-05-01",
    sourceUrl: "https://dudug.kr/196",}
  
];

export const DETAIL_DATA: ProgramDetail = {
  intro: '아주 작은 외출에서 시작해, 또래와 함께 일상의 리듬을 천천히 되찾아가는 8주 프로그램.',
  description:
    '집 밖으로 나오는 첫걸음에 필요한 것들을 함께 마련해, 처음 4주는 1:1 동행으로 시작해 점차 소그룹 활동으로 옮겨갑니다. 끝과 길이, 본인의 속도에 맞춰 참여할 수 있어요.',
  qualification:
    '현재 사회적 고립 또는 은둔 상태에 있는 만 19~34세 청년으로, 일상 회복과 관계 경험을 희망하는 분이면 누구나 신청 가능합니다. 학력, 경력, 소득 제한 없이 참여하실 수 있습니다.',
  curriculum: [
    { weeks: '1~2주차', desc: '1:1 동행 프로그램 — 메니저와 함께 가까운 장소 방문, 외출 연습' },
    { weeks: '3~4주차', desc: '소그룹 활동 진입 — 3~4명 소그룹으로 카페/공원 방문' },
    { weeks: '5~6주차', desc: '문화 활동 체험 — 영화관, 전시회 등 문화공간 방문' },
    { weeks: '7~8주차', desc: '재입 활동 — 혼자 또는 또래와 함께 자율 활동 계획 및 실천' },
  ],
  org: {
    name: '경기 청년재단',
    region: '경기',
    phone: '031-123-4567',
    kakao: '@경기청년재단',
    homepage: 'https://open.kakao.com/example',
    email: 'support@example.or.kr',
  },
};

export const FILTER_OPTIONS: Record<string, string[]> = {
  region: ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충청', '전라', '경상', '제주'],
  level: ['일상 회복', '사회 복귀', '관계 형성'],
  mode: ['온라인', '오프라인', '온·오프라인'],
  period: ['1회(원데이)', '2회-4회', '5회 이상'],
  status: ['현재 신청 가능', '모집 예정', '마감'],
  people: ['1:1 상담', '여러명'],
};

export const FILTERS = [
  { id: 'region', label: '지역' },
  { id: 'level', label: '참여 동기' },
  { id: 'mode', label: '온/오프라인' },
  { id: 'period', label: '참여 기간' },
  { id: 'status', label: '모집 상태' },
  { id: 'people', label: '참가 인원' },
] as const;

export const REVIEWS: Review[] = [
  { id: 1, name: '참여자 A', program: '천천히, 다시 만나는 일상', body: '처음에는 두려웠는데 매니저 선생님 덕분에 조금씩 나올 수 있었어요.' },
  { id: 2, name: '참여자 B', program: '온라인 살롱', body: '집에서도 사람들을 만날 수 있다는 게 신기했고, 다음 기수도 신청할 거예요.' },
  { id: 3, name: '참여자 C', program: '식물 돌봄, 나도 돌봄', body: '식물에 물을 주다 보니 저도 돌봄을 받는 기분이었어요.' },
  { id: 4, name: '참여자 D', program: '늦은 밤 라디오', body: '밤에 혼자 있어도 누군가 함께한다는 느낌이 정말 좋았습니다.' },
];

export const SUPPORT_POLICIES: SupportPolicy[] = [
  { id: 1, title: '청년 고립·은둔 종합 지원 대책', category: '정책', summary: '2024년 발표된 범부처 종합 지원 대책으로, 발굴-연계-지원의 3단계 체계를 제시합니다.' },
  { id: 2, title: '청년 기본 소득', category: '경제', summary: '만 19~34세 청년에게 분기별 지급되는 기본 소득 지원 제도입니다.' },
  { id: 3, title: '청년 마음건강 바우처', category: '심리', summary: '전문 심리 상담을 저렴하게 이용할 수 있는 바우처 지원 사업입니다.' },
  { id: 4, title: '청년 주거 안정 지원', category: '주거', summary: '무보증 월세 지원 및 청년 전용 공공임대주택 신청 안내입니다.' },
];
