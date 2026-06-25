const THEMES = [
  {
    keys: ['주식', 'ETF', '채권', '증권', '투자', '주가', '코스피'],
    icons: ['📈', '💹', '📊'],
    gradient: 'linear-gradient(135deg, #0f2044 0%, #1e40af 60%, #1d4ed8 100%)',
  },
  {
    keys: ['부동산', '주거', '전세', '임대', '청약', '주택'],
    icons: ['🏠', '🔑', '📋'],
    gradient: 'linear-gradient(135deg, #14532d 0%, #15803d 60%, #166534 100%)',
  },
  {
    keys: ['연금', '노후', '은퇴', '퇴직', '생애', '국민연금'],
    icons: ['🏦', '📅', '💼'],
    gradient: 'linear-gradient(135deg, #2e1065 0%, #7e22ce 60%, #6d28d9 100%)',
  },
  {
    keys: ['사기', '피싱', '예방', '보호', '보이스', '스미싱'],
    icons: ['🛡️', '🔒', '⚠️'],
    gradient: 'linear-gradient(135deg, #0c1a45 0%, #1e3a8a 60%, #1d4ed8 100%)',
  },
  {
    keys: ['청년', '캠프', '대학생', '사회초년생', '20대', '30대'],
    icons: ['🎯', '🌱', '💡'],
    gradient: 'linear-gradient(135deg, #6b21a8 0%, #c026d3 55%, #db2777 100%)',
  },
  {
    keys: ['핀테크', '디지털', 'AI', '기술', '트렌드', '컨퍼런스', '인공지능'],
    icons: ['🤖', '💡', '🚀'],
    gradient: 'linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0284c7 100%)',
  },
  {
    keys: ['소비', '재무', '설계', '재테크', '웨비나', '습관', '지출'],
    icons: ['💰', '📐', '🎯'],
    gradient: 'linear-gradient(135deg, #7c2d12 0%, #c2410c 60%, #ea580c 100%)',
  },
  {
    keys: ['박람회', '세미나', '설명회', '포럼', '강연'],
    icons: ['🎪', '🎤', '📢'],
    gradient: 'linear-gradient(135deg, #134e4a 0%, #0f766e 60%, #0d9488 100%)',
  },
  {
    keys: ['보험', '실손', '생명', '손해'],
    icons: ['🤝', '📜', '💊'],
    gradient: 'linear-gradient(135deg, #1e3a5f 0%, #155e75 60%, #0e7490 100%)',
  },
  {
    keys: ['세금', '절세', '세무', '부가가치세', '종합소득세'],
    icons: ['🧾', '🏛️', '💳'],
    gradient: 'linear-gradient(135deg, #292524 0%, #57534e 60%, #78716c 100%)',
  },
]

const DEFAULT = {
  icons: ['🎓', '📚', '✏️'],
  gradient: 'linear-gradient(135deg, #0b4f49 0%, #0f766e 55%, #15803d 100%)',
}

export function getEventTheme(event) {
  if (event.thumbnail) return { icons: null, gradient: null, image: event.thumbnail }

  const text = `${event.title} ${event.host || ''} ${event.summary || ''}`
  for (const t of THEMES) {
    if (t.keys.some((k) => text.includes(k))) {
      return { icons: t.icons, gradient: t.gradient, image: null }
    }
  }
  return { ...DEFAULT, image: null }
}
