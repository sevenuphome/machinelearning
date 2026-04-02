---
date: 2026-04-03
topic: web-interface
---

# Web Interface for Cat Brain AI

## Problem Frame

ตอนนี้ Cat Brain AI เล่นได้แค่ใน terminal ซึ่งไม่สะดวกสำหรับคนอื่น ต้องการ web interface ที่มีรูปแมวการ์ตูนน่ารัก + animation เปิดให้คนอื่นเล่นผ่าน internet ได้

## Requirements

- R1. **Cartoon Cat Visual** — แสดงแมวการ์ตูนน่ารักบนหน้าเว็บ มี animation เปลี่ยนตามอารมณ์แมว (happy, sleepy, annoyed, playful, curious, hungry, content)
- R2. **Interaction Buttons** — ปุ่มกด: ให้อาหาร, ลูบหัว, เล่นด้วย, พูดคุย, รอ — แทนการพิมพ์คำสั่ง
- R3. **Status Display** — แสดงสถานะแมว (hunger, energy, happiness, curiosity, bond) แบบ visual เช่น progress bar หรือ icon
- R4. **Response Text** — แสดงข้อความตอบสนองของแมว (ภาษาไทย) พร้อม animation เปลี่ยนท่าแมวตามการกระทำ
- R5. **ML Brain Backend** — ใช้ ML brain (DQN) ที่เทรนไว้แล้วเป็นตัวตัดสินใจ
- R6. **Public Deployment** — deploy บน internet ให้คนอื่นเปิด URL เล่นได้

## Success Criteria

- เปิด URL แล้วเล่นกับแมวได้ทันที ไม่ต้องติดตั้งอะไร
- แมวมี animation ที่เปลี่ยนตามอารมณ์ชัดเจน
- ตอบสนองเร็ว (< 1 วินาที)
- หน้าตาน่ารัก ใช้งานง่ายบนมือถือด้วย

## Scope Boundaries

- แต่ละคนเล่นแมวของตัวเอง (ไม่ share state กัน)
- ไม่ต้อง login/account
- ไม่ต้อง save state ข้าม session (เริ่มใหม่ทุกครั้ง)
- ไม่ต้องมีเสียง

## Key Decisions

- **Cartoon style:** แมวการ์ตูนสีสันสดใส ใช้ CSS/SVG animation — ไม่ใช้รูปจริงหรือ pixel art
- **Deploy publicly:** ให้คนอื่นเข้าถึงได้ผ่าน URL

## Outstanding Questions

### Deferred to Planning
- [Affects R1][Needs research] ใช้ CSS animation, SVG, หรือ canvas สำหรับแมว?
- [Affects R5][Technical] Web framework ไหน — Flask, FastAPI, หรือ frontend-only?
- [Affects R6][Technical] Deploy ที่ไหน — Vercel, Fly.io, Railway, หรืออื่น?
- [Affects R3][Technical] State management — server-side session หรือ client-side?

## Next Steps

→ `/ce:plan` for structured implementation planning
