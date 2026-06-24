from django.db import models

# 한글 초성 (디자인의 두문자 목록: 쌍자음은 기본자음으로 합침)
_CHOSEONG = [
    'ㄱ', 'ㄱ', 'ㄴ', 'ㄷ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅂ', 'ㅅ',
    'ㅅ', 'ㅇ', 'ㅈ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
]


def leading_initial(text):
    """단어 첫 글자의 두문자(초성/영문/숫자)를 구한다."""
    if not text:
        return '#'
    ch = text.strip()[0]
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:  # 한글 음절
        return _CHOSEONG[(code - 0xAC00) // 588]
    if ch.isdigit():
        return '0-9'
    if ch.isalpha():
        return ch.upper()
    return '#'


class Term(models.Model):
    """경제 용어 사전 항목."""

    SUBJECT_CHOICES = [
        ('economy', '경제'),
        ('management', '경영'),
        ('finance', '금융'),
        ('society', '사회'),
        ('science', '과학'),
        ('etc', '기타'),
    ]

    subject = models.CharField(
        '주제', max_length=20, choices=SUBJECT_CHOICES, default='economy'
    )
    term = models.CharField('용어', max_length=120)
    description = models.TextField('설명')
    initial = models.CharField('두문자', max_length=4, blank=True, db_index=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)

    class Meta:
        ordering = ['term']

    def save(self, *args, **kwargs):
        self.initial = leading_initial(self.term)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.term
