# FOXBORO DATABASE — เว็บ

เว็บแทน Power BI report ของฐานข้อมูล tag ระบบ Foxboro I/A Series
ทำงานแบบ offline ทั้งหมด ไม่ต้องมีเซิร์ฟเวอร์ ไม่ต้องต่อเน็ต ไม่ต้องติดตั้งอะไร

**77,010 tag records · 87 control processors · 69 block types · 1,169 parameters**

## เปิดยังไง

**ออนไลน์** — เปิดลิงก์ GitHub Pages ของ repo นี้ได้เลย (ดูที่ About มุมขวาบนของหน้า repo)

**ในเครื่อง** — กด `Code ▾ → Download ZIP` แตกไฟล์ แล้วดับเบิลคลิก **`index.html`**
(แนะนำ Chrome หรือ Edge)

ถ้า policy ของเครื่องบล็อกไม่ให้เปิดไฟล์ตรง ๆ ให้ดับเบิลคลิก **`serve.cmd`** แทน
จะเปิดเว็บเซิร์ฟเวอร์ที่ `http://127.0.0.1:8712` ให้อัตโนมัติ (ปิดด้วย Ctrl+C)

> **ต้องวาง `index.html` กับ `data.js` ไว้โฟลเดอร์เดียวกันเสมอ** ไฟล์อื่นไม่จำเป็นตอนใช้งาน

## แถบเมนู

ทุกหน้ามีแถบเมนูเดียวกันอยู่ใต้การ์ดชื่อหน้า —
**SYSTEM MANAGER / TAG SEARCH / SIGNAL MAP / FBM (I/O) MODULE MANAGEMENT /
MODBUS COMMUNICATION** —
หน้าที่เปิดอยู่จะเป็นปุ่มสีเขียวมิ้นต์ กดข้ามไปมาได้จากทุกหน้า

## หน้าจอ

หน้าเดียวจบ ไม่มีแท็บ — ด้านบนเป็น KPI 4 ตัว ด้านล่างเป็นตาราง tag records เต็มจอ

**แถบ FILTER ทางซ้าย**

- `NAME`, `DESCRP` — พิมพ์ค้นหา
- `AREA`, `TYPE`, `CP NAME` — คลิกเลือกได้หลายอัน ตัวเลขข้างชื่อคือจำนวนแถว
- `CUSTOM COLUMN` — เลือกคอลัมน์ที่จะแสดงจาก 1,169 คอลัมน์ที่มีข้อมูล
  (ตัวเลขข้างชื่อคอลัมน์คือจำนวนแถวที่มีค่าในคอลัมน์นั้น) ค่าเริ่มต้นคือ 10 คอลัมน์หลัก

**ย่อแถบ filter ได้** — กดปุ่มลูกศรกลมที่ขอบแถบ แถบจะยุบเหลือ 76px เหลือแค่ไอคอน
ตารางกว้างขึ้น 259px กดที่ไอคอนเพื่อกางกลับ ระบบจำสถานะไว้ให้
เป็นท่าทางเดียวกับ PT2 ANALYSIS / ONLINE MONITOR ตั้งใจให้เหมือนกัน
ไอคอนตอนกางอยู่จะขยับเบา ๆ คลิกเพื่อหยุดได้

**อื่น ๆ** — คลิกหัวตารางเพื่อเรียงลำดับ · `Export CSV` ดาวน์โหลดเฉพาะแถวและคอลัมน์ที่กรองอยู่ ·
ปุ่ม ◐ สลับธีมสว่าง/มืด (จำค่าไว้)

## SYSTEM MANAGER

หน้า **`system-manager.html`** — เอาหน้าจอจริงสองตัวมารวมกัน
**System Auditor** ของ Schneider (`09.png`) คือแปด pane ที่ตอบเรื่องเดียวกัน
พร้อมกันในหน้าเดียว ไม่มีแท็บ ไม่มี drill-down ที่ทำให้สิ่งที่เพิ่งดูหายไป ·
และ **System Manager** ของ Foxboro (`08.png`) คือผังอุปกรณ์ฝั่งซ้าย
`network › station › FBM module › ช่องสัญญาณ` ที่กาง/ยุบได้

**แถบซ้ายคือผังอุปกรณ์** — พับได้ด้วยปุ่มลูกศรที่ขอบแถบ เหมือนช่อง filter
ของหน้า TAG SEARCH ทุกอย่าง (ยุบเหลือ 76px กดที่ไอคอนเพื่อกางกลับ
จำสถานะแยกไว้ที่ `fox-mgr-rail-collapsed`) · กดสามเหลี่ยมเพื่อกาง กดที่ชื่อเพื่อเลือก
เลือก **station** → panes ตอบทั้ง station · เลือก **FBM module** → panes แคบลงเหลือ
เฉพาะบล็อกที่ลงบนโมดูลนั้น · เลือก **ช่องสัญญาณ** → กระโดดไปที่บล็อกของช่องนั้น

**แปด pane** ใช้ชื่อเดียวกับเครื่องมือจริง

| pane | มีอะไร |
|---|---|
| **Foxboro Network** | กล่องอุปกรณ์ห้อยจาก bus กดได้ · `ALL NETWORK` + station ทั้ง 89 ตัว |
| **Parameter** | station block (`STA`) ของ station ที่เลือก ทีละพารามิเตอร์ |
| **Compound List** | `CP | COMPOUNDS` |
| **Compound Properties** | พารามิเตอร์ของ record ตัว compound เอง |
| **Blocks Types** | `ALL TYPES` + หนึ่งแถวต่อหนึ่งชนิด พร้อมจำนวน (กดเพื่อกรอง) |
| **Block List** | `CP | COMPOUND | BLOCK | TYPE` |
| **Block Properties** | ทุกพารามิเตอร์ของบล็อก แยก Inputs / Outputs / Data stores · มีช่องกรอง |
| **Block Mapping** | ผังหนึ่งชั้น: อะไรต่อเข้าบล็อกนี้บ้าง |

**Block Mapping** อ่านการต่อสองทาง — *ฮาร์ดแวร์* จาก `IOM_ID` ซึ่งชี้ไปที่ ECB
ชื่อ `<compound>:<IOM_ID>` ใน station เดียวกัน · และ *ซอฟต์แวร์* จากพารามิเตอร์
ขาเข้าที่มีค่าเป็นพินของบล็อกอื่น
พินซ้ายคือขาเข้า**ที่ต่อจริง**เท่านั้น (params.js นับพารามิเตอร์ของ AIN เป็น input
ถึง 56 ตัวเพราะตั้งค่าได้ ไม่ใช่เพราะมีสายลง) พินขวาคือ output ตามนิยามชนิดบล็อก

**กล่องทุกใบในผังเป็นลิงก์ไปหน้า SIGNAL MAP** ของ tag นั้น (`signal-map.html?tag=…`)
ทำเป็น `<a>` จริงใน SVG ไม่ใช่ตัวดัก click จึงได้พฤติกรรมของเบราว์เซอร์มาครบ —
เห็น URL ตอน hover, ctrl/คลิกกลางเปิดแท็บใหม่, tab ไปโฟกัสได้
พอถึงหน้า SIGNAL MAP **ขอบกล่องของ tag นั้นจะกระพริบ** สี่จังหวะแล้วหยุด
(ถ้าอยากเดินโซ่ต่อ*ในหน้านี้* ใช้ค่า reference ใน Block Properties ที่กดได้เหมือนเดิม)

**ความยาวโซ่** ปรับได้ 1–6 ชั้นด้วย slider บนหัว pane — ชั้นละคอลัมน์ ไล่ย้อนจาก
บล็อกที่เลือกไปทางต้นทาง บล็อกที่วาดไปแล้วจะไม่ถูกวาดซ้ำ แค่มีสายเพิ่มเข้าไป
และเส้น **ป้อนกลับ** (cascade ที่วาล์ววนกลับมาเข้า BCALCI ของ PID ตัวเดิม)
วิ่งสวนทางเส้นอื่น จึงวาดเป็นเส้นประสีเหลืองอ้อมใต้กล่องแทนที่จะลากทะลุ ·
ตัดที่ 36 บล็อกกันโซ่ระเบิด

แถบบนมี dropdown เลือก station · breadcrumb `TOP › CP › COMPOUND › BLOCK` ·
ช่องค้นหาที่กระโดดตรงไปยัง tag หรือ station · ค่าที่เป็น reference ของบล็อกอื่น
(`:05LICA061.OUT`) กดได้ · `Export CSV` ดาวน์โหลด Block List ที่กรองอยู่ ·
ลิงก์ตรงได้ด้วย `?tag=COMPOUND:BLOCK` หรือ `?cp=11CP01`

> เรื่อง spare point / lifecycle / firmware ของโมดูล ยังอยู่ที่หน้า
> **FBM (I/O) MODULE MANAGEMENT** — หน้านี้ใช้ผังอุปกรณ์เพื่อ *เลือกขอบเขต*
> ให้ pane ฝั่งบล็อกเท่านั้น

**ไม่มีค่าออนไลน์ในหน้านี้** ทั้งหมดคือ snapshot จาก SaveAll + ทะเบียนฮาร์ดแวร์
จึงไม่มี run mode, alarm feed หรือสถานะ scan แบบหน้าจอจริง และไม่มีการเดาค่าพวกนั้นขึ้นมา

### ประกอบหน้า SYSTEM MANAGER ใหม่

```
python build/build_system_manager_page.py
```

ยก `<head>` (ฟอนต์ + design token ทั้งชุด) มาจาก `system-monitor.html` ตรง ๆ
แล้วเขียนทับ `system-manager.html` — รันใหม่ทุกครั้งที่แก้ shell ในหน้า FBM
ตัวหน้าใช้ `data.js` + `systems.js` + `params.js` ไม่มีไฟล์ข้อมูลของตัวเอง

## FBM (I/O) MODULE MANAGEMENT

หน้า **`system-monitor.html`** ตอบสามคำถามต่อหนึ่ง system —
*มี module อะไรต่ออยู่บ้าง · เหลือ spare point ตรงไหน · รายละเอียด station เป็นยังไง*
เข้าจากแถบเมนูใต้ชื่อหน้า (ชื่อไฟล์ยังเป็น `system-monitor.html` เหมือนเดิมโดยตั้งใจ ลิงก์และ bookmark เก่าจึงยังใช้ได้)

**89 system · 1,436 module · 16,422 I/O point · ว่าง 6,315 จุด**

**แถบซ้าย** ย่อ/กางได้เหมือนหน้า TAG SEARCH — กดปุ่มลูกศรกลมที่ขอบแถบ
จะยุบเหลือ 76px เหลือแค่ไอคอน กดที่ไอคอนเพื่อกางกลับ ระบบจำสถานะไว้ให้
(จำแยกจากหน้า TAG SEARCH เพราะสองแถบเก็บคนละเรื่อง)
ไอคอนตอนกางอยู่จะขยับเบา ๆ คลิกเพื่อหยุดได้

เลือก system ได้ทีละตัว (กดซ้ำเพื่อกลับไปดูทั้งโรงงาน)
แต่ละแถวมีแถบสัดส่วนการใช้งาน เรียงตามชื่อ / spare มากสุด / ใช้งานหนักสุด /
module มากสุด และกรองตาม AREA ได้ · ช่องค้นหารับทั้งชื่อ system และ letterbug

**Modules** — ตารางโมดูลทั้งหมด: letterbug, รุ่น, วิธีระบุที่อยู่, จำนวนจุด,
ใช้แล้ว, จองไว้, ว่าง, lifecycle, firmware
คลิกที่แถวเพื่อกางผังช่องสัญญาณของโมดูลนั้น — ช่องเขียวคือมี tag,
ช่องเหลืองคือตั้ง ECB ไว้แล้วแต่ยังไม่มีบล็อก I/O, ช่องเทาคือว่างจริง
คลิกช่องเขียวเพื่อกระโดดไปดู signal map ของ tag นั้น

**Spare points** — รายการจุดว่างทุกจุด (system, letterbug, รุ่น, เลขจุด, ชนิด, area)
กรองด้วยชนิด AI / AO / DI / DO / PI ได้ ใช้ตอบว่า *"จะเพิ่ม AI ตัวใหม่ ลงตรงไหนได้"*

**รายละเอียด** — ข้อมูล station, spare แยกตามชนิดจุด, รุ่นโมดูลที่ติดตั้ง,
ชนิดบล็อก, scan period และรายการ I/O ที่อ้างถึงอุปกรณ์ซึ่งไม่มี ECB ใน station นั้น

`Export CSV` ดาวน์โหลดตารางที่เปิดอยู่ (Modules หรือ Spare points) ตามขอบเขตที่เลือก

### spare นับยังไง

จุดหนึ่งจะถูกนับว่า **ว่าง** ก็ต่อเมื่อโมดูลนั้นมีจำนวนช่องที่แน่นอนจริง ๆ

- **นับได้** — FBM ที่ระบุช่องด้วยเลขจุด (FBM01/02/05/07/09/41/201/202/204/205/206/
  207/217/240/241/242), FBM แบบ HART ที่หนึ่งช่องคือหนึ่ง ECB201 อ่านเลขช่องจาก
  `DVNAME` = `CH1`–`CH8` (FBM214/216/218/245) และ FBM43 ที่อ่านจาก `CHAN` ของ ECB18
- **นับไม่ได้ จึงไม่นับ** — FBM230/231/232/233 ที่จุดปลายทางเป็น register ของ
  Modbus/Ethernet และ FBM228 (FF) ที่จุดปลายทางเป็นอุปกรณ์บนเซกเมนต์
  สองกลุ่มนี้แสดงจำนวนจุดที่ต่ออยู่ แต่ช่อง spare เป็น `—`

ความจุอ้างอิงจาก `TOP-Foxboro-Hardware-2025_RevA-1.xlsx` เป็นหลัก
ถ้าเจอเลขช่องเกินสเปกรุ่น (FBM07 + expander FBM12, FBM09/41 + FBM42 ใช้ letterbug
เดียวกันแต่จุดเพิ่มเป็นสองเท่า) จะขยายความจุตามที่เจอจริงและติดเครื่องหมาย `⧉`
แทนที่จะรายงาน spare ติดลบ

`02CP02` กับ `03CP10` มีโมดูลในทะเบียนฮาร์ดแวร์แต่ไม่มีใน SaveAll
จึงขึ้นเป็น system ที่ระบุว่า *register only*

### อัปเดตข้อมูล FBM (I/O) MODULE MANAGEMENT

```
python build/export_systems.py
```

อ่าน `data.js` + `TOP-Foxboro-Hardware-2025_RevA-1.xlsx` แล้วเขียนทับ `systems.js`
(ต้องมี openpyxl) รันหลัง `export_data.py` ทุกครั้งที่ข้อมูล tag เปลี่ยน

## MODBUS COMMUNICATION

หน้า **`modbus.html`** — ทุก register point ของ gateway serial/ethernet
(FBM230/231/232/233) รวมไว้ตารางเดียว กรองด้วย CP / gateway / device / ทิศทาง /
register bank และค้นด้วย tag · register · คำอธิบาย

- **แท็บ Register points** — หนึ่งแถวต่อหนึ่ง register: ทิศทาง (IN = CP อ่านจากอุปกรณ์
  ผ่าน RIN/IIN/BIN/PAKIN · OUT = CP เขียนไปอุปกรณ์ผ่าน ROUT/IOUT/BOUT/PAKOUT),
  เลข register, bank ตามมาตรฐาน Modbus (เลขหลักแรก — 0 coil, 1 discrete input,
  3 input register, 4 holding register), รูปแบบข้อมูล (U2/S2/S4/F4/…), ชนิดบล็อก,
  tag (คลิกไป SIGNAL MAP), คำอธิบาย, ช่วงค่า engineering
- **แท็บ สรุปอุปกรณ์** — หนึ่งแถวต่อ ECB201 หนึ่งตัว: protocol, port, station/IP,
  DVOPTS และจำนวน point ฝั่ง IN / OUT / รวม — ตอบคำถาม "อุปกรณ์ตัวนี้รับ-ส่งอะไรบ้าง"
- `Export CSV` ดาวน์โหลดเฉพาะที่กรองอยู่ของแท็บที่เปิด

PAKIN/PAKOUT (packed contact group) ไม่มีเลข register ในฐานข้อมูล — ขึ้นเป็น *packed*
· pseudo-register วินิจฉัยของ gateway (`$M_OVERSCANS` ฯลฯ) ตัดออก

### อัปเดตข้อมูล MODBUS COMMUNICATION

```
python build/export_modbus.py
python build/build_modbus_page.py
```

`export_modbus.py` อ่าน `data.js` เขียนทับ `modbus.js` (208 KB · 16,462 point) ·
`build_modbus_page.py` ประกอบ `modbus.html` ใหม่จาก `<head>` ของ `system-monitor.html`
(ฟอนต์ + design token เหมือนกันทุกหน้า) รันหลัง `export_data.py`

## ปุ่ม Clear all filters

ทุกหน้าที่มีการกรอง มีปุ่มสีเหลืองอำพัน **`Clear all filters`** อยู่มุมขวาบน
ข้าง ๆ `Export CSV` ตำแหน่งเดียวกันทุกหน้า กดแล้วกลับไปสภาพตอนเปิดหน้าพอดี

| หน้า | ล้างอะไรบ้าง |
|---|---|
| **TAG SEARCH** | ค้นหา NAME / DESCRP · chip ของ AREA · TYPE · CP · **และช่องค้นหาเล็ก ๆ ที่กรองรายการ chip เอง** (`qType`/`qCp`/`qCol`) |
| **FBM (I/O) MODULE MANAGEMENT** | system ที่เลือก · AREA · ค้นหา system · การเรียงลำดับ · chip ชนิด spare point |
| **MODBUS COMMUNICATION** | select ทั้งห้า (CP · gateway · device · ทิศทาง · register bank) และช่องค้นหา |
| **SYSTEM MANAGER** | อุปกรณ์ที่เลือก · Blocks Types · ช่องกรองใน Block Properties · ช่องค้นหา |
| **SEQUENCE VIEW** | ช่องกรอง parameter · ช่องค้นในซอร์ส |

**แท็บไม่ใช่ filter จึงไม่ถูกล้าง** — หน้า MODBUS ยังอยู่แท็บเดิม หน้า FBM ยังอยู่
Modules หรือ Spare points ตามที่กำลังอ่าน · การล้าง filter ไม่ควรทำให้เสียตำแหน่งที่ดูอยู่

ของเดิม TAG SEARCH มีปุ่มนี้อยู่แล้วแต่ **ไม่ได้ล้างช่องค้นหาของ chip** —
กดล้างแล้วแถบ TYPE ยังเหลือ 4 จาก 69 ชนิดโดยไม่มีอะไรบนจอบอกว่าทำไม ตอนนี้ล้างครบ

`signal-map.html` กับ `logic-view.html` **ไม่มีปุ่มนี้โดยตั้งใจ** — สองหน้านั้นมีแต่ช่องค้นหา
ที่ใช้*กระโดดไป*หา tag ไม่ได้ซ่อนแถวอะไร ปุ่มชื่อ clear all filters จึงไม่มีอะไรให้ล้าง

## ค่าเริ่มต้นของสองหน้านี้ (แก้ 2026-09-04)

**SIGNAL MAP เปิดมาที่ความยาวโซ่ = 1** (เดิม 4) — เห็นบล็อกที่เลือกกับสิ่งที่ต่อกับมันตรง ๆ
เท่านั้น สี่ชั้นบนบล็อกที่ต่อเยอะคือกำแพง 150 กล่อง ต้องลากกลับลงมาก่อนทุกที
จะกางเพิ่มก็ลาก slider ทีเดียว

**SYSTEM MANAGER ไม่เดาให้ว่าจะดู station ไหน** — เดิม boot เรียก `pickCp(0)`
แล้วเติมหกเพนด้วยข้อมูล station ที่บังเอิญเรียงมาก่อน ตอนนี้ **Compound List /
Blocks Types / Block List / Compound Properties / Parameter / Block Properties
จะว่างไว้จนกว่าจะกดเลือกอุปกรณ์จากผังทางซ้าย** (station · FBM · ช่องสัญญาณ) ·
Foxboro Network กับผังอุปกรณ์ยังวาดตามปกติ เพราะสองอันนั้นคือตัวที่ใช้เลือก ·
Block Mapping มีข้อความ "เลือก block จาก Block List" ของตัวเองอยู่แล้ว

ไม่ใช่แค่ซ่อน — หกเพนนั้นถูก **ข้ามไม่คำนวณ** ตอนยังไม่ได้เลือก
ซึ่งบน ALL NETWORK คือไม่ต้องไล่ 77,010 แถวเพื่อสร้างตารางที่ยังไม่มีใครถาม ·
ลิงก์ตรง `?tag=` และ `?cp=` ยังเข้าหน้าเดิมทุกอย่าง เพราะการกดลิงก์ก็คือการเลือกแล้ว

## Jove (OPC / historian) ใน SIGNAL MAP

เพิ่ม 2026-09-04 · SIGNAL MAP มีปลายทางที่สามแล้ว นอกจาก **บล็อก** (สีฟ้า)
กับ **ECB/FBM** (สีเหลือง) ตอนนี้มี **Jove object** (สีม่วง) ด้วย

ข้อมูลมาจาก `00 RAW DATABASE/Jove/*.exp` (Jove OBJECTS export v1.13)
ในไฟล์มีสามส่วน คั่นด้วยบรรทัดขึ้นต้น `#`

| ส่วน | จำนวน | ใช้ได้ไหม |
|---|---|---|
| Object Type 0 | 14,375 | object ที่ Jove คำนวณเอง (`.MAS-MISMATCH`, `.PUMP-WORD`) ไม่มีคอลัมน์ `Connection` — ไม่มีอะไรให้ join |
| **Object Type 1** | **18,871** | **ตัวที่ต่อผ่าน OM/API — ส่วนนี้แหละที่ใช้** |
| OPC UA | 0 | มีหัวตารางแต่ไม่มีข้อมูล |

ทุกแถวในส่วนที่ 2 มีคอลัมน์ `Connection` เก็บ path เต็มของ Foxboro —
`PS1MCR_MOV05:39MOV229.MA`, `13000F203DI1:130GBS165C.CIN` — **แปลงได้ครบทั้ง 18,871 แถว**
ลงบนบล็อกจริง 18,502 แถว (98%) เหลือ 369 แถวที่ไม่เจอชื่อบล็อก (`T116_T:LEVEL` ฯลฯ)

**ทิศทางอยู่ในไฟล์และสำคัญมาก** — `Buffered Read` / `Buffered Write` บอกว่า
connection นั้นวิ่งทางไหน และ **Jove เขียนกลับเข้า DCS ถึง 5,985 เส้น**
(write อย่างเดียว 4,146 + สองทาง 2,004) เช่น `39MOV229.FIELDCLOSE` →
`PS1MCR_MOV05:39MOV229.AUTCLS` คือคำสั่งปิดวาล์วจากฝั่ง historian/API
เส้นพวกนี้จึงวาดเข้าทางขาเข้าของบล็อก ส่วน 10,378 เส้นที่อ่านอย่างเดียววาดออกทางขาออก ·
อีก 2,343 เส้นที่ไม่ติดธงทั้งคู่ วาดเป็น *อ่าน* — connection มีจริงแต่จะเรียกว่า
command path โดยไม่มีอะไรยืนยันก็เป็นการเดา

**สิ่งที่ได้เพิ่มมาจริง ๆ** — **4,027 บล็อกที่ก่อนหน้านี้ไม่มีสายอะไรเลยในผัง**
(record ของมันไม่อ้างถึงใครและไม่มีใครอ้างถึง) ที่จริงต่อกับ Jove อยู่
เมื่อก่อนเปิด SIGNAL MAP แล้วเจอจอว่าง ตอนนี้เห็นแล้ว

หนึ่ง node ต่อหนึ่ง **Jove object** ไม่ใช่ต่อ prefix — `39MOV229` มี 8 object
ห้อยจากบล็อกเดียว อ่านได้เหมือน PAKCIN fan-out ที่มีอยู่แล้ว ถ้าจับกลุ่มตาม prefix
กล่อง `MOGAS` กล่องเดียวจะมี 291 ขา · ขาฝั่ง Jove คือชื่อ attribute (`CLOSE_SWITCH`)
ฝั่ง Foxboro คือชื่อพารามิเตอร์ — ไวยากรณ์เดียวกับ ECB ที่ขาคือหมายเลขช่อง

Jove object **ไม่มีแถวใน `data.js`** (field 7 = -1) กด Properties แล้วจะแสดง
host / attribute / คำอธิบาย / พารามิเตอร์ที่ผูกอยู่ โดยไม่แตะ `data.js` เลย

### อัปเดตข้อมูล Jove

วางไฟล์ `.exp` ใหม่ลง `00 RAW DATABASE/Jove/` แล้ว

```
python build/export_graph.py
```

`export_graph.py` หยิบไฟล์ `.exp` ที่ชื่อใหม่สุดในโฟลเดอร์เอง (ชื่อไฟล์มีวันที่อยู่แล้ว)
ไม่ต้องแก้อะไร · ถ้าโฟลเดอร์ว่างหรืออ่านไม่ได้ มันจะพิมพ์บอกแล้วสร้าง graph.js
แบบไม่มี Jove ต่อไปตามปกติ · `graph.js` โตจาก 1.4 MB เป็น **1.9 MB**
(82,897 node · 108,897 edge)

## LOGIC VIEW

หน้า **`logic-view.html`** — โปรแกรม `STEP01–STEP50` ของบล็อก CALC / CALCA / LOGIC / MATH
วาดเป็นผังเกตแบบ ICC (`12.png`) · **ไม่มีในแถบเมนู** เปิดจากการคลิกขวาบล็อกใน SIGNAL MAP
มี 4,232 บล็อกที่มีโปรแกรม

**โปรแกรมที่มี branch ก็วาดได้แล้ว** (แก้ 2026-09-04) — เดิมหน้านี้ยอมแพ้ทันทีที่เจอ
`GTO / BIF / BIN / BIZ / BIT / BII / EXIT / SSx` ซึ่งคือ **2,280 จาก 4,232 โปรแกรม**
รวมทุกตัว interlock ของ MOV (`PS1F203MOV1:130MOV059VPL` และพี่น้องอีก ~750 ตัว)

เหตุผลที่ทำได้ อยู่ใน **B0193AX Rev U §14.8.1**

> "Unconditional transfer of control is supported only in a **forward** direction;
> looping backwards is not allowed."

และหน้า opcode ทุกตัวย้ำอีกว่า กระโดดไป step ที่ ≤ step ปัจจุบัน จะเขียน `-4`
(invalid goto syntax error) ลง `PERROR` · **ผัง control flow ของโปรแกรมที่ถูกต้อง
จึงเป็น DAG ที่วิ่งไปข้างหน้าอย่างเดียว ไม่มีลูป** ตรวจกับของจริงแล้ว: ทั้งโรงงาน
**ไม่มี backward jump และไม่มี `GTI` เลยสักตัว**

วิธีวาด — ตัดโปรแกรมที่ทุก branch เป็น **basic block** (ตัวเริ่มบล็อกคือ step 1,
ปลายทางของ branch ทุกอัน และ step ที่ตกมาจากคำสั่งควบคุม) แล้ววาดแต่ละบล็อกด้วย
เครื่องวาดผังเกตตัวเดิมทั้งดุ้น · **26,215 บล็อกในโรงงาน คอมไพล์ผ่านหมด 100%**
จากนั้นเรียงบล็อกเป็น flowchart หนึ่ง rank ต่อหนึ่งชั้นของ DAG

- บล็อกที่จบด้วย branch มี **กล่องตัดสินใจหกเหลี่ยม** อยู่ท้ายผัง ป้อนด้วยค่า accumulator
  ตรงนั้น (branch ไม่ pop — ทุก opcode เขียนว่า `sptr(after) = sptr(before)`)
  เงื่อนไขเอามาจากคู่มือตรง ๆ: `BIF`/`BIZ` = 0 · `BIT` ≠ 0 · `BIN` < 0 ·
  `BIP` ≥ 0 (บวก**หรือศูนย์**) · `BII` = กำลัง initialize · `SSx` = ตั้งค่าแล้วข้าม 1 step
- เส้น **ใช่** (เขียว) / **ไม่** (เทา) ออกจากใต้กล่องตัดสินใจ
- กล่องที่กิน stack ลึกกว่าที่ตัวเองใส่ (อ่านค่าที่บล็อกก่อนหน้าค้างไว้) จะได้
  **ชิปเส้นประ `↑ ค่าค้างจาก step ก่อน`** ไม่ใช่ลากสายทะลุผนังกล่อง —
  ด้วยเหตุผลเดียวกับกฎเดินสายของ `signal-map.html`
- รายการ step ทางขวาถูกคั่นเป็นแถบตามบล็อกเดียวกัน อ่านคู่กับผังได้
- โปรแกรมที่ไม่มี branch (1,952 ตัว) มีบล็อกเดียว วาดเหมือนเดิมทุกประการ ไม่มีกรอบ

ผลลัพธ์: **วาดได้ 4,231 จาก 4,232** เหลือตัวเดียวคือ `SMS_SYS:SYS_COM3`
ที่อ่าน BI01–BI07 แล้วไม่เขียนอะไรเลย — ไม่มีขาออกให้วาดจริง ๆ

### ประกอบ LOGIC VIEW ใหม่

```
python build/export_logic.py
python build/draw_branching_logic.py
python build/layout_branching_logic.py
python build/fix_branching_polish.py
```

สามตัวหลังต้องรันตามลำดับนี้ และรันบน `logic-view.html` ที่ยังไม่เคยรัน
(ทุกตัว assert ว่าเจอ anchor พอดี 1 ที่ ถ้ารันซ้ำจะ ABORT ให้เอง)
`draw_` คือความหมายจากคู่มือ · `layout_` คือเรขาคณิตของ flowchart ·
`fix_` คือสามจุดที่เจอตอนลองใช้จริง

## SEQUENCE VIEW

หน้า **`sequence-view.html`** — หน้าจอ Block Detail ของ ICC สำหรับบล็อก **IND**
(independent sequence) ตามภาพ `13.png` · **ไม่มีในแถบเมนู** เปิดได้สองทาง

- ตาราง **TAG SEARCH** → คลิกชื่อ tag → *เปิด Sequence View* (ขึ้นเฉพาะแถวที่ TYPE = IND)
- **SIGNAL MAP** → คลิกขวาที่บล็อก → *Sequence View…* (เปิดเป็น popup ทับผังเดิม)

**ทำไมต้องมีหน้านี้** — บล็อก sequence ต่อสายด้วย *โค้ด* ไม่ใช่ด้วยค่าพารามิเตอร์
record ของ `39FCP003_SQ:39ACP301` เป็นศูนย์ทั้งแถว ทั้งที่โปรแกรมมันเขียนไปหา
`39ACP302.ACTIVE` และอ่านจาก `39BATCH3.II0005` — `graph.js` ซึ่งดูแต่ค่าพารามิเตอร์
จึงมองไม่เห็นเลย และ SIGNAL MAP ของบล็อกพวกนี้ว่างเปล่า
ข้อมูลการเชื่อมต่อทั้งหมดอยู่ในไฟล์ `.s` ใน `00 RAW DATABASE/S/S` ที่เดียว

**สาม pane บนสุด — ตรงตาม `13.png`**

| pane | อ่านยังไง |
|---|---|
| **Block Properties** | `Parameter \| Value` เรียงตามลำดับจริงใน record ของไฟล์ SaveAll (ไม่ใช่ลำดับคอลัมน์ของ `data.js`) · CP/COMPOUND/BLOCK เติมให้สามแถวบนสุดเหมือน ICC · ชื่อย่อจาก `USER_LABELS` ขึ้นใต้ชื่อ parameter |
| **Input References** | `Input References \| Parameter` — อะไรวิ่งเข้ามาหาบล็อกนี้ |
| **Output References** | `Parameter \| Output References` — บล็อกนี้ไปถึงอะไร |

ป้าย **SEQ** สีเขียวหมายถึงแถวนั้นมาจากโค้ด ไม่ใช่จากค่าพารามิเตอร์ ·
บล็อกเดียวกันขึ้นได้ *ทั้งสอง* pane และไม่ใช่บั๊ก — main sequence สั่ง
`39ACP301.ACTIVE := TRUE` แล้ววนอ่านบิตเดิมด้วย `WAIT UNTIL` เพื่อรู้ว่าจบหรือยัง
เป็นสายคนละเส้นจริง ๆ (`13.png` แสดงแบบนี้สามคู่)

**pane ล่างคือซอร์ส `.s`** — เลขบรรทัด ไฮไลต์ syntax และ reference ทุกตัวคลิกได้
สีเขียว = เขียนออก · สีฟ้า = อ่านเข้า · สีเทาขีดหยัก = หาปลายทางไม่ได้
(ชื่อประกอบตอนรันอย่าง `:39FC'FC_NUM1'_AS:...` ซึ่ง ICC เองก็หาไม่ได้ 1,273 จุด
หรือไม่มีบล็อกชื่อนั้นในดัมพ์ 256 จุด) · บรรทัดที่อ้างผ่าน `#define`
เช่น `CBPSPT := Lprevspt;` ใน `01LY065.s` จะมีบรรทัดกำกับใต้ว่าจริง ๆ แล้วเขียนไปที่
`V101:01LRCA065.SPT` · ลากแถบคั่นกลางเพื่อแบ่งความสูง (จำค่าไว้)

### อัปเดตข้อมูล SEQUENCE VIEW

```
python build/export_sequence.py --check
python build/build_sequence_view_page.py
```

`export_sequence.py` อ่านไฟล์ `.s` ทั้ง 779 ไฟล์ + ไฟล์ SaveAll `.txt` ทุก CP +
`graph.js` แล้วเขียนทับ `sequence.js` (0.47 MB · 942 บล็อก) ·
`--check` จะประกอบ `39FCP003_SQ:39ACP301` ขึ้นมาใหม่แล้วเทียบกับ `13.png`
ทั้ง 4 แถว input, 5 แถว output และลำดับ parameter — ถ้าไม่ตรงให้แก้ parser ไม่ใช่แก้ assertion ·
`build_sequence_view_page.py` ประกอบ `sequence-view.html` โดยยก `<style>`
ทั้งก้อนมาจาก `logic-view.html` (ฟอนต์ + design token จะได้ไม่หลุดจากกัน)

## ไฟล์

| ไฟล์ | คืออะไร |
|---|---|
| `index.html` | ตัวเว็บทั้งหมด — HTML + CSS + JS + ฟอนต์ + ไอคอน อยู่ในไฟล์เดียว |
| `data.js` | ข้อมูล 77,010 แถว × 1,202 คอลัมน์ · 2.4 MB |
| `signal-map.html` | ผังการเดินสัญญาณระหว่างบล็อก (ต้องมี `graph.js`, `params.js`) |
| `system-manager.html` | หน้า SYSTEM MANAGER — ผังอุปกรณ์/บล็อกทั้งลำดับชั้น (ต้องมี `data.js`, `systems.js`, `params.js`) |
| `system-monitor.html` | หน้า FBM (I/O) MODULE MANAGEMENT — อุปกรณ์ / spare point / รายละเอียดของแต่ละ system (ต้องมี `systems.js`) |
| `systems.js` | ทะเบียนโมดูลและผังช่องสัญญาณ 1,436 โมดูล · 160 KB |
| `modbus.html` | หน้า MODBUS COMMUNICATION — register IN/OUT ของ gateway serial/ethernet (ต้องมี `modbus.js`) |
| `modbus.js` | 16,462 register point จาก 86 อุปกรณ์บน 65 gateway · 208 KB |
| `logic-view.html` | หน้า LOGIC VIEW — ผังเกต + flowchart ของ step program (ต้องมี `logic.js`) ไม่อยู่ในแถบเมนู |
| `logic.js` | step program ของ 4,232 บล็อก CALC/CALCA/LOGIC/MATH · 0.43 MB |
| `sequence-view.html` | หน้า SEQUENCE VIEW — Block Detail ของบล็อก IND ตาม `13.png` (ต้องมี `sequence.js`) ไม่อยู่ในแถบเมนู |
| `sequence.js` | 942 บล็อก sequence + ซอร์ส `.s` 779 ไฟล์ + reference ที่ถอดจากโค้ด · 0.47 MB |
| `assets/fonts/` | SF Compact subset (woff2) ต้นฉบับของฟอนต์ที่ฝังไว้ใน `index.html` |
| `05.jpg` | ต้นฉบับไอคอนบนแถบ filter |
| `01.png`–`04.jpg` | ภาพอ้างอิงตอนออกแบบ (Power BI เดิม + style guide) |
| `08.png`–`10.png` | ภาพอ้างอิงหน้า SYSTEM MANAGER (Foxboro System Manager + Schneider System Auditor) |
| `13.png` | ภาพอ้างอิงหน้า SEQUENCE VIEW — Block Detail ของ ICC (`39FCP003_SQ:39ACP301`) ใช้เป็น regression case ของ `export_sequence.py --check` |
| `serve.cmd` | ตัวสำรองไว้เปิดผ่าน localhost |
| `build/export_data.py` | สร้าง `data.js` ใหม่จาก `FOX DATABASE.xlsx` |
| `build/export_systems.py` | สร้าง `systems.js` ใหม่จาก `data.js` + ทะเบียนฮาร์ดแวร์ |
| `build/export_modbus.py` | สร้าง `modbus.js` ใหม่จาก `data.js` |
| `build/add_clear_filters.py` | ปุ่ม Clear all filters ทั้ง 5 หน้าที่มีการกรอง |
| `build/quiet_default_views.py` | SIGNAL MAP เริ่มที่โซ่ชั้น 1 · SYSTEM MANAGER ไม่เติมหกเพนจนกว่าจะเลือกอุปกรณ์ |
| `build/add_jove_to_graph.py` | สอน `export_graph.py` ให้อ่าน Jove export (รันครั้งเดียว) |
| `build/style_jove_nodes.py` | สี/legend/Properties ของ Jove node ใน `signal-map.html` |
| `build/export_logic.py` | สร้าง `logic.js` ใหม่จาก `data.js` + `graph.js` |
| `build/draw_branching_logic.py` | ให้ LOGIC VIEW วาดโปรแกรมที่มี branch ได้ (ความหมายจาก B0193AX) |
| `build/layout_branching_logic.py` | เรียง basic block เป็น flowchart + เดินเส้นควบคุม |
| `build/fix_branching_polish.py` | แก้ backfill ที่วนไม่จบ · จุดออกของเส้น ใช่/ไม่ · `fit()` เร็วไป |
| `build/export_sequence.py` | สร้าง `sequence.js` ใหม่จาก `00 RAW DATABASE/S/S/*.s` + ไฟล์ SaveAll + `graph.js` (`--check` เทียบกับ `13.png`) |
| `build/build_sequence_view_page.py` | ประกอบ `sequence-view.html` จาก `<style>` ของ `logic-view.html` |
| `build/build_modbus_page.py` | ประกอบ `modbus.html` จาก `<head>` ของ `system-monitor.html` |
| `build/build_system_manager_page.py` | ประกอบ `system-manager.html` จาก `<head>` เดียวกัน |
| `build/add_page_nav.py` | ใส่/ซิงก์แถบเมนูทุกหน้า และเปลี่ยนชื่อหน้าที่สาม |
| `build/match_page_shell.py` | ขยาย `index.html` ให้เต็มจอเท่าหน้า FBM และใส่แถบ filter แบบพับได้ให้หน้า FBM |
| `build/embed_fonts.py` | ฝังฟอนต์เป็น data URI ลง `index.html` |
| `build/refresh_rail_icon.py` | สร้างไอคอนใหม่จาก `05.jpg` |
| `build/*.py` (ที่เหลือ) | บันทึกการแก้ layout แต่ละครั้ง รันไปแล้ว เก็บไว้ให้ย้อนดู/ย้อนกลับได้ |

## ข้อมูลมาจากไหน

`data.js` generate จาก `FOX DATABASE.xlsx` (ไฟล์ 28 MB ไม่ได้อยู่ใน repo นี้)
ซึ่งรวมมาจากไฟล์ SaveAll ของแต่ละ CP อีกที

คอลัมน์ถูกเก็บแบบ dictionary-encoded + sparse แล้ว gzip + base64
หน้าเว็บคลายด้วย `DecompressionStream` ตอนโหลด **1,202 คอลัมน์จึงเหลือแค่ 2.4 MB**
และจะกางเป็น array เต็มเฉพาะคอลัมน์ที่แสดงจริง — เลือก 10 จาก 1,202 คอลัมน์
กินหน่วยความจำ 10 × 308 KB แทนที่จะเป็น 370 MB ตารางใช้ virtual scrolling

### อัปเดตข้อมูล

```
python build/export_data.py
python build/export_data.py "D:\some\path\FOX DATABASE.xlsx"
```

แบบแรกจะหา `FOX DATABASE.xlsx` จากโฟลเดอร์แม่ของ repo แบบที่สองระบุเอง
เขียนทับ `data.js` ให้เลย ใช้เวลาราว 30 วินาที ไม่ต้องแก้ `index.html`
ใช้แค่ `zipfile` + `ElementTree` ที่มากับ Python ไม่ต้องลง openpyxl

### เปลี่ยนไอคอนแถบ filter

วางรูปสี่เหลี่ยมจัตุรัสทับ `05.jpg` แล้วรัน `python build/refresh_rail_icon.py`
สคริปต์จะตัดขอบขาวรอบรูปออกเอง ย่อเหลือ 256px แล้วฝังกลับเข้า `index.html` ให้
(ต้องมี Pillow)

## ข้อมูลต่างจาก Power BI ตรงไหน

ทั้งสามข้อคือการแก้ปัญหาที่มีอยู่เดิม ไม่ใช่การเปลี่ยนข้อมูล

1. **77,010 แถว แทน 75,940** — Power Query ทิ้งบล็อก STRING ของ `03CP09`, `31CP01`, `31CP02`
   ไว้ในคอลัมน์ทั่วไป `Column1..Column5` ทำให้ Power BI นับไม่ติด 1,070 แถว
   สคริปต์ย้ายกลับเข้าคอลัมน์จริง (`Column5` ตั้งชื่อเป็น `VALUE`)
   และตัดแถวหัวตารางที่ปนมา 3 แถวทิ้ง

2. **IOM_ID กลับมาเป็น 6 หลัก** — Excel เก็บเป็นตัวเลข ทำให้ `010404` เหลือ `10404`
   สคริปต์เติม 0 ให้ครบ 6 หลักตามที่ `CONVERT 5 TO 6 DIGID.txt` ทำ
   ใช้กับ `IOM_ID`, `IOMIDR`, `DEV_ID`, `PARENT` รวม 2,654 ค่า

3. **AREA ว่าง 13,781 แถว** — `CP AREA.xlsx` มีแค่ 65 CP จาก 87 CP ที่มีข้อมูล
   ยังขาด: `01CP02`, `01CP04`, `01MG01`, `01MG02`, `02CP10`, `161CP1`, `162CP1`, `162CP2`,
   `162CP3`, `162FD1`, `162FD2`, `31CP16`, `31CP19`, `31FD05`, `31FD07`, `31OM01`, `35CP01`,
   `94CP01`–`94CP04`, `94MG02`, `CPTCI1`–`CPTCI3`, `FGMG01`, `FGMG02`
   เติมใน `CP AREA.xlsx` แล้วรัน export ใหม่ ตัวเลขจะหายไปเอง

## ฟอนต์

ใช้ **SF Compact** ฝังเป็น data URI อยู่ใน `index.html` แล้ว จึงไม่ต้องติดตั้งฟอนต์บนเครื่อง
และเปิดจากไฟล์ตรง ๆ ได้ (Chrome ไม่ยอมโหลด `@font-face` จากไฟล์ข้าง ๆ บน `file://`)

SF Compact ไม่มีตัวอักษรไทย ข้อความไทยจึงตกไปใช้ Noto Sans Thai / Leelawadee UI
ตามลำดับใน `--font-ui` เบราว์เซอร์สลับให้เองทีละตัวอักษร

`SF-Compact.dmg` ไม่ได้อยู่ใน repo — 168 MB เกินลิมิต 100 MB ต่อไฟล์ของ GitHub
และไม่จำเป็น เพราะ woff2 ใน `assets/fonts/` subset มาจากมันแล้ว

## ประวัติการเปลี่ยน layout

- ถอดกราฟ Rows by area และตาราง Breakdown ให้ตาราง tag records เป็นตัวหลัก
  → `build/table_first_layout.py`
- ยุบหน้า OVERVIEW กับ CUSTOM TABLE เป็นหน้าเดียว โดยใช้ layout ของ CUSTOM TABLE
  → `build/merge_pages.py`
- ถอดกราฟ Rows by block type เพราะซ้ำกับ chip TYPE ในแถบซ้ายที่มีตัวเลขอยู่แล้ว
  และอยู่ใต้ตารางเต็มจอจนไม่มีใครเลื่อนไปเห็น → `build/drop_type_chart.py`
- เพิ่มไอคอนและปุ่มย่อแถบ filter → `build/add_rail_fold.py`
- เพิ่มหน้า SYSTEM MONITOR และปุ่มเข้าหน้าใหม่ในอีกสองหน้า
  → `build/export_systems.py` + `build/add_system_monitor.py`
- ย้ายลิงก์ข้ามหน้าออกจาก topbar มารวมเป็นแถบเมนูเดียวใต้ชื่อหน้าทั้งสามหน้า
  และเปลี่ยนชื่อหน้าที่แสดงจาก SYSTEM MONITOR เป็น FBM (I/O) MODULE MANAGEMENT
  (ชื่อไฟล์คงเดิม) → `build/add_page_nav.py`
- เพิ่มหน้า SYSTEM MANAGER ตามหน้าจอ System Manager / System Auditor ของจริง
  (`08.png`–`10.png`) — ผังลำดับชั้นสองมุมมอง + status/information + ตารางตามบริบท
  → `build/build_system_manager_page.py` และเพิ่มเข้าแถบเมนูใน `build/add_page_nav.py`
- ขยาย `index.html` จาก `max-width:1760px` เป็น `1900px` (padding 22/20/26)
  ให้กว้างเท่าหน้า FBM — บนจอ 1920 เดิมเหลือขอบว่างข้างละ 74.5px
  และยกแถบ filter แบบพับได้ (ไอคอน + ปุ่มลูกศร) ไปใส่หน้า FBM ด้วย
  → `build/match_page_shell.py`
- เอาเพดานความกว้างออกจากทุกหน้า — `max-width:1900px` คงที่ → `.app{width:100%}`
  หน้าจึงเต็มความกว้างหน้าต่าง (เหลือแค่ padding ของ body ~20px ข้างละ)
- ปรับสเกลตัวหนังสือของ `index.html` ให้ตรงกับอีกสี่หน้า — h1 `clamp(26px,3.4vw,40px)`,
  eyebrow 11px/800, lede 13px, topbar padding `16px 24px`, ระยะห่างคอลัมน์/บล็อก 16px
  (เดิม `index.html` ถูก bump ให้ใหญ่กว่าตอนยังเป็นหน้าเดียว — `build/bump_type_scale.py`)
- เขียนหน้า SYSTEM MANAGER ใหม่ตาม layout ของ System Auditor (`09.png`) —
  จากแถบผังซ้าย + KPI + แท็บ เปลี่ยนเป็นแปด pane เห็นพร้อมกันในหน้าเดียว
  (Foxboro Network เป็นกล่องกดได้ · Parameter · Compound List/Properties ·
  Blocks Types · Block List · Block Properties · Block Mapping)
  → `build/build_system_manager_page.py`
- คืนผังอุปกรณ์ของ `08.png` มาเป็นแถบซ้ายที่พับได้เหมือนช่อง filter
  (`network › station › FBM › ช่องสัญญาณ` เลือกโมดูลแล้ว pane ฝั่งบล็อกแคบตาม)
  และเพิ่ม slider **ความยาวโซ่** 1–6 ชั้นให้ Block Mapping พร้อมเส้นป้อนกลับแบบเส้นประ
- ทำกล่องใน Block Mapping เป็นลิงก์ `<a>` ไปหน้า SIGNAL MAP ของ tag นั้น
  และให้ `signal-map.html` กระพริบขอบกล่องของ tag ที่เปิดมาด้วย `?tag=`
  (ทุกหน้าที่ลิงก์เข้า SIGNAL MAP ได้ผลนี้เหมือนกัน ไม่ใช่แค่ SYSTEM MANAGER)
- ย่อกล่อง KPI (สรุปจำนวน) และแถบ filter ให้เท่ากันทุกหน้าและเล็กลง —
  `.kpis` เป็น `minmax(140px,1fr)`/gap 10px, ตัวเลข 34px → 25px, การ์ด padding `11px 14px 10px`;
  แถบซ้าย `.layout` คอลัมน์ 312/335px → 288px, `.rail` padding `14px`/gap 12px
  (4 หน้าที่มีสองกล่องนี้ — TAG SEARCH / SYSTEM MANAGER / FBM / MODBUS; SIGNAL MAP ไม่มี)

ทุกสคริปต์ใน `build/` แก้ `index.html` แบบระบุข้อความตรง ๆ และ assert ถ้าหาไม่เจอ
อ่านเพื่อดูว่าแก้อะไรไป หรือกลับด้านเพื่อย้อนกลับได้
