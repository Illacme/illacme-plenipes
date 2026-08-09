---
title: 주권 출판 아키텍처와 제로 인투전 마크다운 노드 거버넌스
description: Illacme Plenipes 의 물리적 주권 격리, 플러그인 매트릭스 및 자동 다운그레이드 보호 메커니즘에 대한 심층 분석.
author: Illacme Architecture Team
date: 2026-08-03 10:29:28.726631+08:00
tags: 아키텍처, 주권, 보안
hreflangs:
- lang: zh
  url: /zh/dry-run-markdown
- lang: ru
  url: /ru/dry-run-markdown
language: ko
route_prefix: ''
route_source: ''
mapped_sub_dir: ''
slug: dry-run-markdown
date_formatted: '2026-08-03'
---

# 🛡️ 주권 출판 아키텍처와 제로 인투전 마크다운 노드 거버넌스

디지털 출판 및 개인 지식 관리 (PKM) 분야에서 **콘텐츠 물리적 주권**과 **개인정보 보안**은 창작자가 지켜야 할 가장 중요한 적선입니다. Illacme Plenipes 는 혁신적인 '주권 출판 (Sovereign Publishing)' 아키텍처를 채택했습니다.

---

## 🏛️ 물리 아키텍처 디커플링

시스템 설계는 "제로 데이터 오염" 및 "물리적 침투 없음" 원칙을 따릅니다:

| 아키텍처 계층 | 물리적 구성 요소 | 책임 설명 |
|---|---|---|
| **원고 라이브러리 계층** | `./vault/` | 창작자의 순수한 Markdown 노트로, 시스템은 **읽기 전용 스캔**만 수행하며 원고 구조를 절대 파괴하지 않습니다. |
| **출판 주권 계층** | `imprints/*/` | 다중 브랜드 물리적 격리, 전용 주제, 컴퓨팅 자원 및 구성 템플릿을 저장합니다. |
| **장식 렌더링 계층** | `themes/*/` | 정적 SSG(Starlight / Docusaurus 등) 프론트엔드 템플릿 렌더링 및 결과물 출력을 담당합니다. |
| **상태기 장부** | `.plenipes/ledger.db` | SQLite/JSON 아키텍처로, 슬라이스 지문, Slug 매핑 및 증분 변경 사항을 기록합니다. |

---

## 🔒 물리적 보호 및 내오류 메커니즘

[DIRECT ANSWER MODE: Do NOT output
### 자동화 오프라인 안전 자가 치유 ###
- **주권 공백 보호**: 경로 누락 또는 구성 파일 손상 시, 시스템은 제로 설정 자동 복구 탐지 메커니즘을 시작합니다.
- **단일 인스턴스 프로세스 자리 잠금**: 포트 `43210` 에 바인딩하여 다중 프로세스 경쟁 충돌을 물리적으로 방지합니다.


<!-- Sovereign-Tag: [[AEL-Iter-ID: Sync:sovereign-pu]] -->