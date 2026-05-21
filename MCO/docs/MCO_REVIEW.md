# MCO 시스템 분석 및 리뷰

> 대상: Message-Layer Compliance Oracle (MCO) — `D:\AAI\IdeaFirst\MCO`
> 출처: IdeaFirst SA-AOX Standalone Loop, winner `IDEA-CAP-20-004` (Run `SA-AOX-20260521-002`)
> 리뷰 일자: 2026-05-21
> 리뷰 방식: 전체 산출물 정적 분석 + `verify.py`/`mco_oracle.py` 실행 검증 + fallback 경로 재현

---

## 1. 요약 (Executive Summary)

MCO는 ISO 20022 / 스테이블코인 결제 메시지를 다중 관할권 컴플라이언스 규칙에 대조해
제재·AML 위반을 판정하고 암호학적 attestation token을 발급하는 **탐색용(exploratory) 컴플라이언스 오라클**이다.

PGF Gantree → 디렉토리 구조 매핑, 실행 가능한 prototype + 자동 검증 suite, 명시적 경계 선언
(`production_compliance_certified: false`) 등 IdeaFirst standalone 트랙으로서의 골격은 견고하다.
`verify.py` 통합 테스트 4건은 현재 환경에서 전부 통과한다.

그러나 **명세(spec)와 구현(impl) 사이의 분기**가 심각하다. 108줄짜리
`compliance_scoring_spec.md`는 전혀 구현되지 않았고, `compliance_rules.yaml`의
`compliance_rules` 섹션은 코드가 한 번도 읽지 않으며, "stdlib-only" 설계 목표는
PyYAML 하드 의존으로 사실상 깨져 있다. 검증 4건이 통과하는 것은 테스트 데이터가
하드코딩된 기본값과 우연히 겹치고 PyYAML이 설치돼 있기 때문이지, 구현이
명세를 만족해서가 아니다.

**판정: MVP 골격은 합격, 그러나 "컴플라이언스 오라클"이라는 이름값을 하려면
명세-구현 정합성 회복이 선결 과제다. 현재는 boolean 규칙 매처(rule matcher)이지 oracle이 아니다.**

| 항목 | 평가 |
|---|---|
| 구조/패키징 | ★★★★☆ — Gantree↔디렉토리 매핑 깔끔, 자체완결적 |
| 문서화 | ★★★★☆ — README/ENGINEERING_GUIDE/scoring spec 충실 (단, spec이 구현과 불일치) |
| 명세-구현 정합성 | ★☆☆☆☆ — scoring spec 미구현, rules YAML 미사용 |
| 정확성/견고성 | ★★☆☆☆ — fallback 크래시, 입력 검증 부재 |
| 테스트 커버리지 | ★★☆☆☆ — stablecoin 경로 0%, KYC-통과 경로 미검증 |
| 경계/정직성 | ★★★★☆ — exploratory 마킹 명확, 단 일부 문서 과장 |

---

## 2. 시스템 개요

### 2.1 목적
결제 메시지 payload(ISO 20022 또는 스테이블코인 tx)를 받아 다음을 판정한다:
제재 대상 포함 여부 / AML 한도 초과 여부 / 고위험 관할권 여부. 통과 시 SHA-256 기반
mock attestation token을 발급하고, 위반 시 `BLOCKED` 감사 기록을 남긴다.

### 2.2 End-to-End 흐름 (`docs/ENGINEERING_GUIDE.md` §2)
```
JSON payload → mco_oracle.py → 스키마 파싱(ISO/Stablecoin)
  → 제재 스크리닝(이름·국가) → AML 한도 평가 → SHA-256 해시 → 서명 → attestation/BLOCK
```

### 2.3 구성 산출물
| 영역 | 파일 | 상태 |
|---|---|---|
| 설계 | `.pgf/DESIGN-MCO.md`, `WORKPLAN-MCO.md`, `status-MCO.json` | G1–G6 completed, **G7 pending** |
| 데이터 계약 | `spec/message_schema.yaml`, `spec/compliance_rules.yaml` | 정의됨 |
| 채점 계약 | `spec/compliance_scoring_spec.md` | **정의만, 미구현** |
| 엔진 | `tools/mco_oracle.py` (194줄) | 실행 가능 |
| 검증 | `verification/verify.py` (122줄) | 4 테스트 통과 |
| 예제 | `examples/sample_message.json`, `attestation_output.json` | 존재 |
| 문서 | `README.md`, `docs/ENGINEERING_GUIDE.md` | 충실 |

---

## 3. 강점

1. **자체완결적 product 트랙** — `.sa-*`/`.aox`/`.cix`/`.evx` 프로덕션 경로를 오염시키지
   않고 `MCO/` 하위에 독립 존재. WORKPLAN의 격리 정책을 준수.
2. **PGF Gantree ↔ 디렉토리 정합** — `ComplianceEngine`/`DataContract`/`Prototype`/
   `VerificationSystem` 노드가 실제 폴더·파일과 1:1 매핑. AI 에이전트 탐색 누락 방지.
3. **실행 가능한 prototype + 자동 검증** — 개념 노트에 머물지 않고 CLI로 돌아가는
   엔진과 통합 테스트를 함께 제공. `python verification/verify.py` → 4/4 PASS 재현 확인.
4. **명시적 경계 선언** — `message_schema.yaml`의 `boundary` 블록, `status-MCO.json`의
   `production_certified: false`. SA-AOX standalone 규율과 일관됨. 정직한 한계 표기.
5. **이중 포맷 데이터 계약** — ISO 20022 / 스테이블코인 양쪽 required field를 스키마에 명세.
6. **결정론적 트랜잭션 해시** — `transaction_hash`(payload의 sort_keys SHA-256)는
   재실행 시에도 동일함을 실측 확인 (`65f9cceb...d7d52` 재현).

---

## 4. 발견 사항 (Findings)

심각도: **C**ritical / **H**igh / **M**edium / **L**ow

### C1 — "stdlib-only" 주장이 거짓이며 fallback YAML 파서가 자기 규칙 파일에서 크래시한다

`ENGINEERING_GUIDE.md` §1은 *"dependencies: Python standard library only for maximum
auditability"*라고 명시한다. 그러나 실제로는:

- 규칙·스키마가 모두 YAML이고, `mco_oracle.py`는 PyYAML이 있으면 그것을 쓴다.
- PyYAML이 없을 때를 위한 fallback 파서(`load_yaml`, line 14–62)는 **`compliance_rules.yaml`
  파싱 중 하드 크래시**한다.

재현 (PyYAML import를 강제로 막고 fallback 실행):
```
TypeError: list indices must be integers or slices, not str
  at load_yaml line 41:  data[current_section][key] = val
```
원인: `compliance_rules:` 의 list-of-dicts 섹션을 만나면 line 49–51에서
`data['compliance_rules']`를 `[]`(list)로 바꾼 뒤, 다음 줄 `name: ...`을 처리하며
line 41에서 `list['name']` 문자열 인덱싱을 시도 → TypeError.

즉 **PyYAML이 없으면 오라클은 규칙 파일을 아예 로드하지 못하고 죽는다.** 현재 4/4 테스트가
통과하는 것은 리뷰 환경에 PyYAML이 설치돼 있기 때문이다. "stdlib-only"는 사실이 아니라
"PyYAML 하드 의존"이며, fallback의 존재가 오히려 안전하다는 *착각*을 준다.

부가 결함(크래시하지 않는 부분도 부정확):
- 중첩 평탄화: `blocked_names`가 `sanctions_list` 하위가 아닌 최상위로 새어나옴 →
  `rules_data.get('sanctions_list')`는 빈 dict가 되어, 오라클은 **YAML 내용 대신
  하드코딩 기본값**(`mco_oracle.py` line 72–77)을 쓴다. 컴플라이언스 도구에서 이는
  "규칙 파일에 제재 대상을 추가했는데 조용히 무시되는" 치명적 실패 모드다.
- 인라인 주석 미제거: `- "KP" # North Korea` → 값이 `KP" # North Korea`로 파싱됨.

**권고:** (a) PyYAML을 정식 의존성으로 선언하고 "stdlib-only" 문구 삭제, 또는
(b) 규칙/스키마를 JSON으로 전환해 `json`(stdlib)으로 일관되게 로드. 어중간한 fallback
파서는 제거하는 편이 안전하다.

### C2 — `compliance_scoring_spec.md` 전체가 미구현 (dead spec)

`spec/compliance_scoring_spec.md`(108줄)는 4개 가중 factor
(`sanction_screening` 0.40 / `aml_limit` 0.30 / `country_risk` 0.20 /
`data_completeness` 0.10)로 `compliance_risk_score`(0–100)를 산출하고
4단계 tier(`CRITICAL_VIOLATION`/`ENHANCED_REVIEW`/`MONITORED_OK`/`LOW_RISK`)로
분류하는 상세 계약을 정의한다.

그러나 `mco_oracle.py`는 **점수를 계산하지 않는다.** 순수 boolean 규칙 매칭으로
`BLOCKED`/`APPROVED`만 반환하고, 출력 JSON에 `compliance_risk_score`도 tier도 없다.
`ENGINEERING_GUIDE.md` §3 용어표는 "Compliance Score: 0–100 결정론적 지표"를 핵심
개념으로 소개하지만 그런 필드는 어디에도 생성되지 않는다.

결과적으로 scoring spec은 **읽히지 않는 죽은 문서**이고, MCO는 "다차원 위험 점수
오라클"이 아니라 boolean rule matcher다. 제품 명칭("Oracle")과 실제 동작의 간극.

**권고:** 둘 중 하나로 정합화 — (a) scoring 로직을 `mco_oracle.py`에 구현하고
출력에 `compliance_risk_score`/`tier` 추가, 또는 (b) scoring spec을 "v2 후보"로
강등 명시하고 현재 구현이 boolean 게이트임을 ENGINEERING_GUIDE에 정직하게 기술.
G7 전에 이 정합화가 우선이다.

### H1 — `compliance_rules` 섹션을 코드가 전혀 사용하지 않음

`compliance_rules.yaml`은 `RULE-AML-01`(`threshold_usd: 10000`),
`RULE-GEO-02`를 list로 정의한다. `DESIGN-MCO.md` PPR도
`for rule in compliance_rules: if rule.matches(...)`로 규칙 순회를 명세한다.
그러나 `mco_oracle.py`는 규칙 list를 순회하지 않고 `if amount >= 10000.0`
(line 123)으로 **임계값을 매직 넘버로 하드코딩**한다. `threshold_usd`가 YAML과
코드에 이중 정의되어 한쪽만 바꾸면 조용히 어긋난다.

**권고:** `compliance_rules`를 실제로 로드해 `threshold_usd`/`action`을 구동.
규칙을 데이터로 외부화하는 것이 이 제품의 핵심 가치 제안인데 현재는 장식이다.

### H2 — "결정론적 서명" 주장이 거짓 (실측 확인)

`ENGINEERING_GUIDE.md` §8 인수 체크리스트: *"Cryptographic signature changes
are deterministic."* 그러나 서명 payload는
`f"{private_key}:{tx_hash}:{timestamp}"`(line 152)이고 `timestamp`는
`datetime.utcnow()`(매 실행 변동)이다.

실측: 동일 `sample_message.json`을 두 번 실행 →
- `examples/attestation_output.json`: `mco_sig_0x322a9ee59ee0f617029fe474fc684171`
- 리뷰 중 재실행: `mco_sig_0x85f3124801566bb77ba3ac40e16d83b5`

서명은 **재현 불가**다. 결정론적인 것은 `transaction_hash`뿐. 체크리스트 주장이
코드와 모순된다.

**권고:** 문구를 *"transaction_hash is deterministic; signature is timestamp-bound"*로
정정하거나, 결정론이 요구사항이면 서명에서 timestamp를 분리.

### H3 — `--bypass`가 무경고로 exit 0, 컴플라이언스 도구로서 위험

`verify.py`의 `--bypass`/`-bypass`/`bypass`는 테스트를 한 건도 돌리지 않고
`exit(0)`을 반환한다(line 61–63). README와 ENGINEERING_GUIDE 양쪽이 이를
*정상 사용법*으로 비중 있게 안내한다. 컴플라이언스 검증 파이프라인에서 CI가
이 플래그를 실수로 물면 "검증 0건"이 "검증 성공"으로 둔갑한다. `aox_evaluation_report.md`가
이를 프로덕션 자동화 경로(`verify.py -bypass`)로 거론한 점도 우려스럽다.

**권고:** bypass 시 stderr에 굵은 경고 출력 + 별도 exit code(예: 0이 아닌 전용 코드)
또는 환경변수 게이팅. 최소한 "검증 통과"와 구분되는 신호를 남길 것.

### H4 — 금액 검증 부재 (음수/0 트랜잭션이 APPROVED)

`message_schema.yaml`은 `amount minimum: 0.01`, `validation_rules`는
*"Transaction amount must be positive"*를 명시한다. 그러나 `mco_oracle.py`는
`float(tx_data.get("amount", 0))`만 할 뿐 양수 검증을 하지 않는다. `amount: 0` 또는
음수 트랜잭션은 제재·국가 체크만 통과하면 `APPROVED` + attestation 발급된다.

**권고:** `evaluate_compliance` 진입부에 `amount > 0` 검증 추가, 위반 시 BLOCKED.

### H5 — 스키마/필수 필드 검증 전무

`message_schema.yaml`의 `required_fields_iso20022`/`required_fields_stablecoin`을
코드가 검사하지 않는다. `msg_id`, `creation_date_time`, `payment_type` 누락 payload도
그대로 통과한다. scoring spec의 `data_completeness_factor`가 이를 담당하기로 돼 있었으나
C2(scoring 미구현)로 인해 완전성 검사 자체가 없다.

**권고:** 최소한 required field 존재 검증 게이트 추가.

### M1 — 제재 매칭이 정확 일치(exact uppercase equality)뿐

`check_sanctions`는 `entity_name.upper() in blocked_names`만 수행(line 84).
scoring spec §1과 ENGINEERING_GUIDE §3은 *"close name matches"*를 약속한다.
공백·구두점·분음부호(diacritics)·음역(transliteration) 정규화도, 퍼지 매칭도 없다.
실제 SDN/OFAC 스크리닝은 퍼지 매칭이 필수이며, `ALEXEY SMIRNOV`를
`Aleksei Smirnov`로 쓰면 통과한다. 명세가 구현보다 과장됨.

**권고:** 최소 정규화(strip/collapse whitespace, casefold) + 토큰 기반 부분 일치.
퍼지 매칭이 v2 범위면 spec에서 "close match"를 빼거나 v2로 명시.

### M2 — "서명"이 평문 키 SHA-256, 누구나 위조 가능

`private_key_sig = "mco_secret_key_attestation_signature_v1"`는 소스에 평문
리터럴로 박혀 있다(line 81). 서명은 HMAC도 아닌
`sha256(secret:hash:timestamp)`이고, 비대칭 키쌍이 없어 **리포를 본 사람은 누구나
attestation을 위조**할 수 있다. 출력 필드명 `signature`/`oracle_id`/`certificate_type:
ISO20022_COMPLIANCE_COMPATIBILITY_v1`은 권위 있는 인증서처럼 보인다. 코드 주석은
"simulation"/"mock"이라 하지만 출력 산출물에는 mock 표식이 없다.

**권고:** 출력 필드를 `mock_signature`/`simulated_attestation`으로 명명하고
attestation token에 `"simulated": true` 플래그 추가. 실제 서명이 목표면 `hmac`(stdlib)
또는 비대칭 서명으로 교체하고 키를 소스 밖으로.

### M3 — ISO/Stablecoin 판별이 취약한 휴리스틱

`is_iso = "debtor" in tx_data and "creditor" in tx_data`(line 92). `payment_type`,
`tx_hash`, `chain_id` 같은 명확한 판별자가 스키마에 있는데도 쓰지 않는다. debtor만
있고 creditor가 누락된 손상 ISO 메시지는 스테이블코인 경로로 잘못 라우팅되어
`metadata`에서 이름을 못 찾고 빈 문자열로 제재 체크를 통과한다.

**권고:** `payment_type`/`tx_hash` 존재 여부로 명시적 판별, 판별 실패 시 BLOCKED.

### M4 — 테스트 커버리지 공백

`verify.py` 4건은 모두 ISO 경로다. 미검증 영역:
- **스테이블코인 분기(line 101–109) 커버리지 0%** — 한 번도 실행 안 됨.
- "AML 한도 초과 + 유효 KYC → APPROVED" 경로 미검증 (BLOCKED 케이스만 있음).
- attestation token 내용(해시·서명 형식) 검증 없음 — status 문자열만 비교.
- 음수/0 금액, 필수 필드 누락, 손상 JSON 케이스 없음.
- `examples/sample_message.json` 자체에 대한 회귀 테스트 없음.

**권고:** 스테이블코인 APPROVED/BLOCKED, AML+KYC APPROVED, 음수 금액, attestation
구조 검증을 테스트에 추가.

### M5 — `datetime.utcnow()` deprecated

line 137 `datetime.utcnow()`는 Python 3.12+에서 deprecated이며, 리뷰 환경(3.14)에서
`DeprecationWarning`이 실제 출력됨. 향후 제거 예정.

**권고:** `datetime.now(timezone.utc)`로 교체.

### M6 — `enhanced_kyc_verified` 진리값 파싱 불완전

`in (True, "true", "True")`(line 127–129)는 `"TRUE"`, `"1"`, 정수 `1`, `"yes"`를
놓친다. 사용자가 `"TRUE"`로 보내면 KYC 미검증으로 간주되어 고액 거래가 BLOCKED.

**권고:** `str(v).strip().lower() in ("true","1","yes")` 형태로 정규화.

### L1 — 산출물 간 버전 불일치
`compliance_rules.yaml` `version: '1.0'` vs `message_schema.yaml` `version: "0.1"`
vs `status-MCO.json` `mvp_created` vs certificate `_v1`. 단일 버전 정책 권장.

### L2 — scoring spec의 FATF watch-list(0.3 tier) 데이터 소스 부재
`compliance_scoring_spec.md` §3은 "high-risk FATF watch list (monitored)"의 0.3 tier를
정의하지만 해당 list가 `compliance_rules.yaml` 어디에도 없다. scoring을 구현하더라도
0.3 분기는 구동 불가.

### L3 — G7 미완 + ENLI 리뷰 교훈 부분 적용
`status-MCO.json` G7(`rule_expansion`) pending. 제재 DB가 toy 규모(이름 3·국가 3).
`aox_evaluation_report.md`의 "Review Lessons"는 *"pilot-only 산출물에 멈추지 말고
처음부터 자동화 scaffold와 검증 경로를 넣어라"*고 명시한다. MCO는 검증 scaffold
(`verify.py`)는 갖췄으나, ENLI가 받았던 **데이터 수집 ingestion scaffold**
(`tools/ingest_sources.py` 류)에 해당하는 것이 없다. 제재 데이터 소스 연동 scaffold가
G7의 실질 내용이어야 한다.

### L4 — fallback 파서 인라인 주석 처리 결함
C1에 포함. 크래시하지 않는 list 값도 `# 주석`을 값에 포함시킴.

---

## 5. 명세 ↔ 구현 정합성 매트릭스

| 명세 항목 | 출처 | 구현 상태 |
|---|---|---|
| 제재 이름/국가 BLOCK | rules.yaml, oracle | ✅ 구현 (단 정확 일치만, M1) |
| AML 한도 BLOCK | RULE-AML-01 | ⚠️ 하드코딩, YAML 미사용 (H1) |
| `compliance_risk_score` 0–100 | scoring_spec | ❌ 미구현 (C2) |
| 4단계 tier 분류 | scoring_spec | ❌ 미구현 (C2) |
| 4개 가중 factor | scoring_spec | ❌ 미구현 (C2) |
| 금액 양수 검증 | schema validation_rules | ❌ 미구현 (H4) |
| 필수 필드 검증 | schema required_fields | ❌ 미구현 (H5) |
| 결정론적 attestation | ENGINEERING_GUIDE §8 | ⚠️ hash만 결정론, 서명 비결정론 (H2) |
| stdlib-only 의존성 | ENGINEERING_GUIDE §1 | ❌ 거짓, PyYAML 하드 의존 (C1) |
| ISO/Stablecoin 이중 포맷 | schema, oracle | ⚠️ 구현되나 stablecoin 미검증·판별 취약 (M3,M4) |

명세 항목 10개 중 **완전 구현 1, 부분/결함 4, 미구현 5.**

---

## 6. 권고 우선순위

**P0 — 정합성 회복 (G7 착수 전 필수)**
1. C1: PyYAML을 정식 의존성으로 선언하거나 규칙을 JSON화. 깨진 fallback 파서 제거.
2. C2: scoring spec을 구현하거나 "v2 후보"로 강등 명시 — 둘 중 하나로 정직하게 정합.
3. H1: `compliance_rules` YAML을 실제로 로드해 `threshold_usd` 구동.

**P1 — 정확성/안전성**
4. H2: "결정론적 서명" 문구 정정.
5. H3: `--bypass`에 경고 + 구분 가능한 종료 신호.
6. H4/H5: 금액 양수 검증 + 필수 필드 검증 게이트 추가.

**P2 — 견고성/정직성**
7. M2: attestation 산출물에 `simulated: true` 표식, 필드명 `mock_*`화.
8. M3/M5/M6: 포맷 판별 명시화, `datetime` 교체, 진리값 파싱 정규화.
9. M4: 스테이블코인·KYC-통과·attestation 구조 테스트 추가.

**P3 — 확장 (G7 본체)**
10. L3: 제재 데이터 ingestion scaffold 추가 (ENLI 교훈 적용).
11. M1: 제재 매칭 정규화/퍼지 도입 또는 spec에서 "close match" 제거.

---

## 7. IdeaFirst 파이프라인 관점 코멘트

MCO는 SA-AOX standalone winner의 구체화물로서 **provenance 추적과 경계 마킹이 정직**하다
(`consumed_ideas.yaml`의 `IDEA-CAP-20-004` 기록, `production_certified: false`).
이는 SA-AOX 규율 준수 측면에서 모범적이다.

다만 CIX v1.5.1 cross-model surprise validation을 거쳐 **프로덕션 승격**을 노린다면,
현재의 명세-구현 분기(C1·C2·H1)는 승격 심사에서 곧바로 지적될 항목이다. standalone
exploratory 단계에서 P0를 닫아두는 것이 승격 비용을 크게 줄인다.

---

## 8. 결론

MCO는 **잘 짜인 MVP 골격 위에 명세-구현 분기를 안고 있는** 트랙이다. 구조·문서·검증
scaffold·경계 정직성은 우수하나, 핵심 가치 제안인 "다차원 위험 점수 오라클"이 코드에
존재하지 않고(현재는 boolean rule matcher), "stdlib-only" 같은 문서 주장이 사실과
어긋난다. `verify.py` 4/4 통과는 환경 우연(PyYAML 설치 + 테스트 데이터가 하드코딩
기본값과 중복)에 기댄 것이지 정합성의 증거가 아니다.

다음 노드 G7("규칙 의미·DB 확장")로 나아가기 전에, **P0 3건(C1·C2·H1)으로 명세와
구현을 일치시키는 것**이 가장 가치 있는 작업이다. 그 정합이 끝나면 MCO는 이름값
("Oracle")을 하는 제품이 되고, CIX 프로덕션 승격 경로도 현실적인 거리에 들어온다.

---

*리뷰 산출: IdeaFirst 컨텍스트 분석 기반. 본 문서는 MCO 트랙의 기술 리뷰이며
프로덕션 인증이 아니다.*
