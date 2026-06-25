import datetime
from django.core.management.base import BaseCommand
from contents.models import Event

TODAY = datetime.date(2026, 6, 25)

EVENTS = [
    {
        'title': '2026 금융소비자 보호 온라인 교육',
        'summary': '금융소비자 권익 강화를 위한 필수 온라인 교육 과정',
        'body': (
            '금융감독원 주관 금융소비자 보호 교육으로, 금융 상품 이용 시 알아야 할 권리와 의무, '
            '불완전판매 대처법, 금융 분쟁 조정 절차 등을 다룹니다.\n\n'
            '누구나 무료로 수강 가능하며, 수료 시 금융감독원 명의 수료증이 발급됩니다.\n\n'
            '강의는 자기 주도 학습 방식으로 진행되며, 총 5개 모듈 · 약 3시간 분량입니다.'
        ),
        'status': 'open',
        'region': '온라인',
        'online_type': 'online',
        'host': '금융감독원',
        'start_date': TODAY - datetime.timedelta(days=5),
        'end_date': TODAY + datetime.timedelta(days=25),
        'place_name': '',
        'address': '',
    },
    {
        'title': '청년 주거 금융 지원 설명회 (서울)',
        'summary': '전세자금 대출·청년 버팀목 대출 등 주거 금융 지원 제도 안내',
        'body': (
            '국토교통부 및 주택금융공사가 공동 주관하는 청년 주거 금융 지원 설명회입니다.\n\n'
            '청년 전세자금 대출, 버팀목 전세 대출, 청년 우대형 청약통장 등 주요 지원 제도를 '
            '알기 쉽게 설명하고, 신청 방법부터 유의 사항까지 안내합니다.\n\n'
            '현장에서 1:1 상담 창구도 운영합니다. 사전 예약 없이 선착순 입장 가능합니다.'
        ),
        'status': 'open',
        'region': '서울',
        'online_type': 'offline',
        'host': '국토교통부 / 주택금융공사',
        'start_date': TODAY - datetime.timedelta(days=2),
        'end_date': TODAY + datetime.timedelta(days=10),
        'place_name': '서울 강남구청 대강당',
        'address': '서울특별시 강남구 학동로 426',
    },
    {
        'title': '2026 개인 투자자 주식 투자 교육 (기초반)',
        'summary': '주식 시장 구조부터 재무제표 읽기까지, 초보 투자자를 위한 8주 과정',
        'body': (
            '한국거래소(KRX) 투자자교육재단이 주관하는 개인 투자자 대상 기초 주식 교육입니다.\n\n'
            '주식 시장의 구조와 작동 원리, 기업 가치 분석 방법, 재무제표 읽는 법, '
            'PER·PBR·ROE 등 핵심 투자 지표 해석을 배웁니다.\n\n'
            '8주 과정 (매주 수요일 저녁 19:00~21:00), 온·오프라인 병행 운영. '
            '수강료 무료, 수료 후 KRX 수료증 발급.'
        ),
        'status': 'open',
        'region': '서울',
        'online_type': 'both',
        'host': '한국거래소(KRX) 투자자교육재단',
        'start_date': TODAY - datetime.timedelta(days=10),
        'end_date': TODAY + datetime.timedelta(days=46),
        'place_name': 'KRX 서울사무소 교육장',
        'address': '서울특별시 영등포구 여의나루로 76',
    },
    {
        'title': '생애주기별 재무 설계 웨비나 시리즈',
        'summary': '20대 ~ 60대 생애주기에 맞는 재무 설계 전략 6회 웨비나',
        'body': (
            '미래에셋증권 리타이어먼트연구소 주관 무료 웨비나 시리즈입니다.\n\n'
            '6회에 걸쳐 사회 초년생의 통장 관리, 30대 주택 마련 전략, 40대 자녀 교육비와 노후 준비 '
            '병행, 50~60대 은퇴 자산 인출 전략 등 생애주기별 맞춤 재무 설계를 다룹니다.\n\n'
            '매주 목요일 12:00~13:00 온라인 생중계. 사전 신청 필수. 다시보기 2주 제공.'
        ),
        'status': 'open',
        'region': '온라인',
        'online_type': 'online',
        'host': '미래에셋증권 리타이어먼트연구소',
        'start_date': TODAY - datetime.timedelta(days=7),
        'end_date': TODAY + datetime.timedelta(days=28),
        'place_name': '',
        'address': '',
    },
    {
        'title': '2026 부산 금융 박람회 참가자 금융 교육',
        'summary': '부산 국제 금융 박람회 연계 일반 시민 대상 금융 이해력 교육',
        'body': (
            '2026 부산 국제 금융 박람회와 연계하여 운영되는 시민 대상 금융 교육 프로그램입니다.\n\n'
            '예금·적금·펀드·보험의 차이, 금리 변동이 내 자산에 미치는 영향, '
            'ETF·채권 기초 개념 등을 강사가 쉽게 설명합니다.\n\n'
            '하루 4회 운영 (10:00 / 12:00 / 14:00 / 16:00), 회당 60분. 사전 신청 불필요.'
        ),
        'status': 'open',
        'region': '부산',
        'online_type': 'offline',
        'host': '부산광역시 / 한국금융연구원',
        'start_date': TODAY - datetime.timedelta(days=1),
        'end_date': TODAY + datetime.timedelta(days=6),
        'place_name': 'BEXCO 제1전시장',
        'address': '부산광역시 해운대구 APEC로 55',
    },
    {
        'title': '디지털 금융 사기 예방 교육 (시니어 특화)',
        'summary': '보이스피싱·스미싱·메신저피싱 등 디지털 금융 사기 유형별 예방 교육',
        'body': (
            '금융감독원과 경찰청이 공동 주관하는 시니어 특화 금융 사기 예방 교육입니다.\n\n'
            '최신 보이스피싱 수법과 대처 요령, 스마트폰 금융 앱 안전 이용법, '
            '가족 간 피해 예방 소통법 등을 다룹니다.\n\n'
            '전국 주민센터 순회 교육으로 진행되며, 참가비 무료. '
            '교재와 예방 체크리스트를 무료로 제공합니다.'
        ),
        'status': 'open',
        'region': '전국',
        'online_type': 'offline',
        'host': '금융감독원 / 경찰청',
        'start_date': TODAY - datetime.timedelta(days=14),
        'end_date': TODAY + datetime.timedelta(days=60),
        'place_name': '전국 주민센터 순회',
        'address': '',
    },
    {
        'title': 'ETF 투자 전략 집중 과정 (온라인)',
        'summary': 'ETF 기초부터 섹터·테마 ETF 전략까지 4주 완성 온라인 강의',
        'body': (
            '삼성자산운용이 주관하는 무료 ETF 투자 교육 과정입니다.\n\n'
            'ETF의 구조와 종류, 국내외 주요 ETF 상품 비교, 섹터 로테이션 전략, '
            '채권 ETF로 포트폴리오 안정화하는 방법, 레버리지·인버스 ETF 유의 사항 등을 다룹니다.\n\n'
            '총 8강, 강당 40~50분 분량. 수강 기간 내 반복 시청 가능. 수료 시 소정의 경품 증정.'
        ),
        'status': 'open',
        'region': '온라인',
        'online_type': 'online',
        'host': '삼성자산운용',
        'start_date': TODAY - datetime.timedelta(days=3),
        'end_date': TODAY + datetime.timedelta(days=25),
        'place_name': '',
        'address': '',
    },
    {
        'title': '2026 경기도 청년 금융 캠프',
        'summary': '경기도 거주 만 19~34세 청년 대상 1박 2일 금융 몰입 캠프',
        'body': (
            '경기도 금융복지상담센터 주관, 청년층의 금융 역량 강화를 위한 1박 2일 집중 캠프입니다.\n\n'
            '신용 관리와 부채 조정 전략, 사회 초년생 재무 목표 수립, '
            '금융 심리(과소비·충동 구매) 이해, 소액 투자 시뮬레이션 실습 등으로 구성됩니다.\n\n'
            '참가비 전액 무료 (숙식 제공). 모집 인원 40명, 선착순 마감. '
            '경기도 거주 청년이라면 누구나 신청 가능.'
        ),
        'status': 'open',
        'region': '경기',
        'online_type': 'offline',
        'host': '경기도 금융복지상담센터',
        'start_date': TODAY + datetime.timedelta(days=5),
        'end_date': TODAY + datetime.timedelta(days=14),
        'place_name': '경기도 인재개발원',
        'address': '경기도 수원시 장안구 경수대로 1150',
    },
    {
        'title': '국민연금 노후 설계 무료 상담 및 교육 (대구)',
        'summary': '국민연금 예상 수령액 조회 및 연금 수령 전략 맞춤 상담 교육',
        'body': (
            '국민연금공단 대구지사가 주관하는 노후 설계 무료 상담·교육 행사입니다.\n\n'
            '국민연금 예상 수령액 시뮬레이션, 임의가입·추납 제도 안내, '
            '개인연금·퇴직연금과의 연계 전략, 은퇴 후 건강보험료 절감 방법 등을 안내합니다.\n\n'
            '1인당 30분 1:1 맞춤 상담. 현장 접수 가능하나 사전 예약 시 우선 배정. '
            '평일 09:00~17:00 운영.'
        ),
        'status': 'open',
        'region': '대구',
        'online_type': 'offline',
        'host': '국민연금공단 대구지사',
        'start_date': TODAY - datetime.timedelta(days=8),
        'end_date': TODAY + datetime.timedelta(days=20),
        'place_name': '국민연금공단 대구지사',
        'address': '대구광역시 동구 동대구로 465',
    },
    {
        'title': '2026 핀테크·디지털 금융 트렌드 컨퍼런스',
        'summary': '오픈뱅킹·CBDC·AI 자산관리 등 최신 금융 기술 트렌드 강연',
        'body': (
            '한국핀테크산업협회 주관, 핀테크 및 디지털 금융 분야 최신 트렌드를 조망하는 컨퍼런스입니다.\n\n'
            '오픈뱅킹 2.0 정책 방향, 중앙은행 디지털화폐(CBDC) 파일럿 현황, '
            'AI 기반 로보어드바이저 성과 분석, 마이데이터 활용 개인 금융 혁신 사례 등 '
            '업계 전문가 8인의 발표로 구성됩니다.\n\n'
            '온·오프라인 동시 진행. 오프라인 참가 200명 선착순, 온라인은 제한 없음. '
            '참가 신청 필수 (무료).'
        ),
        'status': 'open',
        'region': '서울',
        'online_type': 'both',
        'host': '한국핀테크산업협회',
        'start_date': TODAY + datetime.timedelta(days=2),
        'end_date': TODAY + datetime.timedelta(days=9),
        'place_name': '서울 여의도 전경련회관',
        'address': '서울특별시 영등포구 여의대로 24',
    },
]


class Command(BaseCommand):
    help = '현재 진행 중인(open) 교육 행사 더미 데이터 10건 추가'

    def handle(self, *args, **options):
        created = 0
        for data in EVENTS:
            _, is_new = Event.objects.get_or_create(
                title=data['title'],
                defaults=data,
            )
            if is_new:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'완료: {created}건 추가 (이미 존재하는 항목은 건너뜀)'
        ))
