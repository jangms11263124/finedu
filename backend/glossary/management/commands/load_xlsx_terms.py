import openpyxl
from django.core.management.base import BaseCommand
from glossary.models import Term, leading_initial

class Command(BaseCommand):
    help = 'data/20260623_시사경제용어사전.xlsx 파일의 데이터를 Term 모델에 저장합니다.'

    def handle(self, *args, **options):
        # 1. 엑셀 파일 열기
        wb = openpyxl.load_workbook('data/20260623_시사경제용어사전.xlsx', read_only=True)
        sheet = wb.active

        # 2. 카테고리 맵핑 사전
        subject_map = {
            '경제': 'economy',
            '경영': 'management',
            '금융': 'finance',
            '사회': 'society',
            '과학': 'science',
        }

        # 3. 기존 용어 삭제
        Term.objects.all().delete()
        self.stdout.write(self.style.WARNING('기존 경제 용어 데이터를 모두 삭제했습니다.'))

        # 4. 행 루프를 돌며 대량 삽입 준비
        term_instances = []
        count = 0

        # row index: (no, subject, term, description)
        for row in sheet.iter_rows(min_row=2, max_col=4, values_only=True):
            if len(row) < 4:
                continue
            _, sub_val, term_val, desc_val = row[:4]

            if not term_val or not desc_val:
                continue

            sub_key = subject_map.get(str(sub_val).strip(), 'etc')
            term_str = str(term_val).strip()
            desc_str = str(desc_val).strip()

            initial_ch = leading_initial(term_str)

            term_instances.append(Term(
                subject=sub_key,
                term=term_str,
                description=desc_str,
                initial=initial_ch
            ))
            
            count += 1
            if len(term_instances) >= 500:
                Term.objects.bulk_create(term_instances)
                term_instances = []

        if term_instances:
            Term.objects.bulk_create(term_instances)

        self.stdout.write(self.style.SUCCESS(f'총 {count}개의 경제 용어 데이터를 성공적으로 저장했습니다.'))
