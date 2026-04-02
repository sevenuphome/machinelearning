---
date: 2026-04-03
topic: cat-brain-ai
---

# Cat Brain AI — Virtual Pet with Cat-like Behavior

## Problem Frame

ผู้ใช้ต้องการสัตว์เลี้ยงเสมือนจริงที่มีพฤติกรรมเหมือนแมวจริง ๆ — ไม่ใช่แค่ random response แต่ต้องมีอารมณ์ ความต้องการ ความจำ และตัดสินใจเองได้ โดยโต้ตอบผ่านข้อความ

โปรเจคนี้เป็นทั้ง learning project สำหรับ ML/AI และเป้าหมายสร้าง product ที่น่าสนใจ รันบน Mac M4

## Requirements

- R1. **Internal State System** — แมวมีสถานะภายในที่เปลี่ยนแปลงตามเวลาและการโต้ตอบ: ความหิว, พลังงาน, อารมณ์ (happy, annoyed, curious, sleepy, playful), ระดับความผูกพันกับผู้เลี้ยง
- R2. **Autonomous Decision Making** — แมวตัดสินใจเองว่าจะทำอะไร (นอน, เล่น, สำรวจ, ร้องขออาหาร, เพิกเฉย) โดยอิงจาก internal state — ส่วนนี้คือ ML brain
- R3. **Memory & Relationship** — แมวจำได้ว่าผู้เลี้ยงเคยทำอะไร สร้างความสัมพันธ์ระยะยาว ถ้าดูแลดีจะสนิทขึ้น ถ้าทิ้งไว้นานจะห่างเหิน
- R4. **Cat-like Independence** — แมวไม่ทำตามคำสั่งเสมอ มีอิสระในการตัดสินใจ บางทีเพิกเฉย บางทีมาหาเอง ระดับความร่วมมือขึ้นกับอารมณ์และความผูกพัน
- R5. **Text-based Interaction** — ผู้ใช้ส่งคำสั่ง/ข้อความ (เช่น "ลูบหัว", "ให้อาหาร", "เล่นด้วย") แมวตอบสนองด้วยข้อความบรรยายพฤติกรรม
- R6. **Time Progression** — เวลาผ่านไป state ของแมวเปลี่ยน (หิวขึ้น, ง่วงขึ้น, เบื่อ) แม้ผู้ใช้ไม่ได้โต้ตอบ

## Architecture Direction

**Hybrid: State Machine + ML Brain**
- **Body Layer (State Machine):** จัดการ internal states — hunger, energy, mood, curiosity, bond level. เปลี่ยนแปลงตาม rules ที่กำหนด (เช่น หิวเพิ่มตามเวลา, กินอาหารแล้วหิวลด)
- **Brain Layer (ML):** Neural network ที่รับ internal state เป็น input แล้ว output เป็น action ที่แมวจะทำ — เทรนด้วย reinforcement learning หรือ supervised learning
- **Memory Layer:** เก็บประวัติการโต้ตอบ, คำนวณ bond level, ส่งผลต่อ decision

เริ่มจาก Body Layer ก่อน แล้วค่อย ๆ เพิ่ม ML เข้ามาแทนที่ rule-based decision

## Success Criteria

- แมวตอบสนองต่อ input เดียวกันไม่เหมือนกันทุกครั้ง ขึ้นกับ state ปัจจุบัน
- รู้สึกได้ว่าแมวมี "นิสัย" — ไม่ใช่ random แต่มีรูปแบบพฤติกรรมที่สอดคล้อง
- แมวที่ถูกดูแลดีจะมีพฤติกรรมต่างจากแมวที่ถูกเพิกเฉย
- ส่วน ML brain ตัดสินใจดีกว่า random choice อย่างมีนัยสำคัญ

## Scope Boundaries

- ไม่มี GUI/animation ในเฟสแรก — text only
- ไม่ต้องเข้าใจภาษาธรรมชาติ — ใช้ command-based input ก่อน (เช่น "feed", "pet", "play")
- ไม่ทำ multiplayer หรือหลายแมว
- ไม่ต้อง persistent storage ขั้นสูง — เก็บ state ใน memory หรือ simple file ก่อน
- รันบน Mac M4 เท่านั้น ไม่ต้องคิดเรื่อง cloud/deployment

## Key Decisions

- **Hybrid over pure ML:** เพราะผู้ใช้เพิ่งเริ่ม ML — state machine ให้ผลเร็ว ส่วน ML เพิ่มทีหลังได้
- **Text-based first:** โฟกัสที่ "สมอง" ก่อน UI มาทีหลัง
- **Command-based input:** ลด complexity ของ NLP — ใช้คำสั่งตรง ๆ ก่อน

## Outstanding Questions

### Deferred to Planning
- [Affects R2][Technical] ML framework ไหนเหมาะสุด — PyTorch + MPS หรือ MLX?
- [Affects R2][Needs research] RL algorithm ไหนเหมาะกับ action space ขนาดเล็ก (DQN, PPO, หรืออื่น)?
- [Affects R3][Technical] โครงสร้างข้อมูล memory ควรเป็นแบบไหน?
- [Affects R1][Technical] ค่า state parameters เริ่มต้นและ decay rate ที่เหมาะสม

## Next Steps

→ `/ce:plan` for structured implementation planning
