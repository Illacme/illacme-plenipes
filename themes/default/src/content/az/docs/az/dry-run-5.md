---
title: Yaratıcılar üçün 5 dəqiqəlik sürətli giriş kılavuzu
description: Yeni yaradıcıların sistem konfiqurasiyasını sürətlərlə həyata keçirməsi, nəşr platformalarını idarə etməsi və bütün kanallarla sinkronlaşdırma funksiyasını sınaması üçün təlimat.
author: Illacme Onboarding Group
date: 2026-08-03 10:29:33.615179+08:00
tags: İstifadəçi qəbuledənlik təlimatı
hreflangs:
- lang: zh
  url: /zh/dry-run-5
- lang: az
  url: /az/dry-run-5
language: az
route_prefix: ''
route_source: ''
mapped_sub_dir: ''
slug: dry-run-5
date_formatted: '2026-08-03'
---

# 📖 Yaradıcı üçün 5 dəqiqəlik sürətli giriş kılavuzu

**Illacme Plenipes**-i istifadə etməyə xoş gəldiniz! Bu təlimat sizə idarə mərkəzindən istifadə qaydalarını və nəşr prosedurlarını 5 dəqiqə ərzində öyrətməyə kömək edəcək.

---

## 🛠️ Addım 1: İdarəetmə mərkəzini kəşf edin (Governance Dashboard)

Brauzeri açın və `http://127.0.0.1:43212/dashboard/` ünvanını daxil edərək idarəetmə panelinə girin:

1. **Əsas konfiqurasiya və idarəetmə (`general`)**: İdentiﬁkatorları, rəqəmsal uyğunluq meta məlumatlarını və hesablama qabiliyyəti ehtiyatının təmizlənməsi mərkəzini yoxlayın.
2. **Dizayn və rejim (`layout`)**: Brend imprintlərini idarə edin, vizual temaları (məsələn, Starlight) dəyişdirin və nəşr rejimlərini tənzimləyin.
3. **Dil tərcüməsi və idarəetmə (`localization_gov`)**: Çoxdilli strukturu, blok səviyyəli qaydaları və terminologiya lüğətini konfiqurasiya edin.

---

## ⚡ Addım II: Komut Sətiri ilə sürətli sinkronizasiya

Grafik interfeysi əlavə olaraq, istənilən vaxt CLI komandaları ilə artıq yoxlama və sinkronizasiya əməliyyatlarını da həyata keçirə bilərsiniz:

```bash
# 启动全量增量扫描与对齐
python3 plenipes.py --once

# 启动看门狗实时监听模式
python3 plenipes.py --watch
```

---

## 🎨 Addım 3: Yerli Önizləmə və Ümumiləşdirilmiş Dağıtma

Yayım boru xəttini işə saldıqdan sonra, istənilən vaxt yerli önizləmə xidməti portu `43213`-ü başlataraq şık statik renderlənmiş veb-saytı real zaman rejimində izləyə bilərsiniz!


<!-- Sovereign-Tag: [[AEL-Iter-ID: Sync:getting-star]] -->