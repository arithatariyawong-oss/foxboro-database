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
**FOXBORO DATABASE / SIGNAL MAP / FBM MODULE MANAGEMENT / MODBUS COMMUNICATION** —
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

## FBM MODULE MANAGEMENT

หน้า **`system-monitor.html`** ตอบสามคำถามต่อหนึ่ง system —
*มี module อะไรต่ออยู่บ้าง · เหลือ spare point ตรงไหน · รายละเอียด station เป็นยังไง*
เข้าจากแถบเมนูใต้ชื่อหน้า (ชื่อไฟล์ยังเป็น `system-monitor.html` เหมือนเดิมโดยตั้งใจ ลิงก์และ bookmark เก่าจึงยังใช้ได้)

**89 system · 1,436 module · 16,422 I/O point · ว่าง 6,315 จุด**

**แถบซ้าย** ย่อ/กางได้เหมือนหน้า FOXBORO DATABASE — กดปุ่มลูกศรกลมที่ขอบแถบ
จะยุบเหลือ 76px เหลือแค่ไอคอน กดที่ไอคอนเพื่อกางกลับ ระบบจำสถานะไว้ให้
(จำแยกจากหน้า FOXBORO DATABASE เพราะสองแถบเก็บคนละเรื่อง)
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

### อัปเดตข้อมูล FBM MODULE MANAGEMENT

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

## ไฟล์

| ไฟล์ | คืออะไร |
|---|---|
| `index.html` | ตัวเว็บทั้งหมด — HTML + CSS + JS + ฟอนต์ + ไอคอน อยู่ในไฟล์เดียว |
| `data.js` | ข้อมูล 77,010 แถว × 1,202 คอลัมน์ · 2.4 MB |
| `signal-map.html` | ผังการเดินสัญญาณระหว่างบล็อก (ต้องมี `graph.js`, `params.js`) |
| `system-monitor.html` | หน้า FBM MODULE MANAGEMENT — อุปกรณ์ / spare point / รายละเอียดของแต่ละ system (ต้องมี `systems.js`) |
| `systems.js` | ทะเบียนโมดูลและผังช่องสัญญาณ 1,436 โมดูล · 160 KB |
| `modbus.html` | หน้า MODBUS COMMUNICATION — register IN/OUT ของ gateway serial/ethernet (ต้องมี `modbus.js`) |
| `modbus.js` | 16,462 register point จาก 86 อุปกรณ์บน 65 gateway · 208 KB |
| `assets/fonts/` | SF Compact subset (woff2) ต้นฉบับของฟอนต์ที่ฝังไว้ใน `index.html` |
| `05.jpg` | ต้นฉบับไอคอนบนแถบ filter |
| `01.png`–`04.jpg` | ภาพอ้างอิงตอนออกแบบ (Power BI เดิม + style guide) |
| `serve.cmd` | ตัวสำรองไว้เปิดผ่าน localhost |
| `build/export_data.py` | สร้าง `data.js` ใหม่จาก `FOX DATABASE.xlsx` |
| `build/export_systems.py` | สร้าง `systems.js` ใหม่จาก `data.js` + ทะเบียนฮาร์ดแวร์ |
| `build/export_modbus.py` | สร้าง `modbus.js` ใหม่จาก `data.js` |
| `build/build_modbus_page.py` | ประกอบ `modbus.html` จาก `<head>` ของ `system-monitor.html` |
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
  และเปลี่ยนชื่อหน้าที่แสดงจาก SYSTEM MONITOR เป็น FBM MODULE MANAGEMENT
  (ชื่อไฟล์คงเดิม) → `build/add_page_nav.py`
- ขยาย `index.html` จาก `max-width:1760px` เป็น `1900px` (padding 22/20/26)
  ให้กว้างเท่าหน้า FBM — บนจอ 1920 เดิมเหลือขอบว่างข้างละ 74.5px
  และยกแถบ filter แบบพับได้ (ไอคอน + ปุ่มลูกศร) ไปใส่หน้า FBM ด้วย
  → `build/match_page_shell.py`

ทุกสคริปต์ใน `build/` แก้ `index.html` แบบระบุข้อความตรง ๆ และ assert ถ้าหาไม่เจอ
อ่านเพื่อดูว่าแก้อะไรไป หรือกลับด้านเพื่อย้อนกลับได้
