from machine import Pin, SoftI2C, Timer, ADC, UART  # นำเข้าโมดูลที่จำเป็นสำหรับการควบคุม GPIO, I2C, Timer, ADC, และ UART
import ssd1306, framebuf, menu_images  # นำเข้าไลบรารีสำหรับควบคุม OLED, การจัดการ frame buffer, และรูปภาพเมนู
from time import sleep  # นำเข้า sleep สำหรับการหน่วงเวลา

# กำหนดการตั้งค่า UART ที่ใช้สำหรับการสื่อสารแบบอนุกรม
uart = UART(1, baudrate=115200, tx=17, rx=16)  # ตั้งค่า UART 1 ที่ความเร็ว 115200 bps, ขา TX และ RX

# กำหนดปุ่มต่างๆ สำหรับการควบคุม
buttnDown = Pin(13, Pin.IN, Pin.PULL_UP)  # ปุ่มลง (Pin 13) ถูกตั้งเป็น INPUT พร้อม Pull-Up
buttnMid = Pin(12, Pin.IN, Pin.PULL_UP)   # ปุ่มกลาง (Pin 12) ถูกตั้งเป็น INPUT พร้อม Pull-Up
buttnUp = Pin(14, Pin.IN, Pin.PULL_UP)     # ปุ่มขึ้น (Pin 14) ถูกตั้งเป็น INPUT พร้อม Pull-Up

# กำหนด ADC สำหรับการอ่านค่า
adc = ADC(Pin(34))  # กำหนด ADC ที่ Pin 34
adc.atten(ADC.ATTN_11DB)  # ตั้งค่าการลดทอนสัญญาณ ADC เป็น 11 dB

# กำหนดการเชื่อมต่อ I2C
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # ตั้งค่า I2C โดยใช้ Pin 22 เป็น SCL และ Pin 21 เป็น SDA

# กำหนดขนาดของหน้าจอ OLED
width: int = 128  # ความกว้างของ OLED
height: int = 64  # ความสูงของ OLED
oled = ssd1306.SSD1306_I2C(width, height, i2c)  # สร้างวัตถุ OLED โดยใช้ I2C

# กำหนด LED ที่ใช้สำหรับสถานะต่างๆ
led = Pin(2, Pin.OUT)  # LED ที่ Pin 2 ถูกตั้งเป็น OUTPUT

# กำหนด Timer สำหรับการจัดการเวลา
tim0 = Timer(0)  # Timer 0 สำหรับการเปลี่ยนโหมด
tim1 = Timer(1)  # Timer 1 สำหรับการจัดการ LED

# กำหนดตัวแปรสถานะและเมนู
state: int = 0  # สถานะเริ่มต้น
menu: list = ["Pepsi", "Tea", "Cocoa", "Milk", "Americano", "Matcha Latte", "Lemonade", "Latte"]  # เมนูเครื่องดื่ม
stateMenu: int = 0  # ตัวแปรเก็บ index ของเมนู
selectMenu: int = 1  # ตัวแปรเก็บบรรทัดที่เลือก
oledPo: int = 0  # ตัวแปรสำหรับเลื่อนกรอบ
monitor: int = 1  # ตัวแปรสำหรับติดตามสถานะการทำงาน
quantity: int = 0  # ตัวแปรเก็บจำนวนเครื่องดื่มที่เลือก
menuImages = menu_images.menulist  # นำเข้ารูปภาพเมนู
flag: int = 0  # ตัวแปรสำหรับติดตามสถานะการทำงานของปุ่ม

# ฟังก์ชันสำหรับจัดการปุ่มลง
def showPushDown(Pin):
    global buttnDown, oled, state, stateMenu, menu, selectMenu, oledPo, monitor  # ใช้ตัวแปร global
    if buttnDown.value() == 0 and state == 0 and monitor == 1:  # ตรวจสอบว่าปุ่มกดลง ถูกกด และอยู่ในสถานะที่เหมาะสม
        state = 1  # เปลี่ยนสถานะ
        if selectMenu != 4:  # ถ้าไม่อยู่บรรทัดที่ 4
            oledPo += 15  # เลื่อนกรอบลง
            selectMenu += 1  # เพิ่มบรรทัดที่เลือก
        else:  # ถ้าอยู่บรรทัดที่ 4
            stateMenu += 1  # เลื่อนเมนู
            if stateMenu + 3 > len(menu) - 1:  # ตรวจสอบว่าต้อง Reset หรือไม่
                stateMenu = 0  # รีเซ็ตเมนู
                oledPo = 0  # รีเซ็ตตำแหน่งกรอบ
                selectMenu = 1  # รีเซ็ตบรรทัดที่เลือก
    else:
        state = 0  # เปลี่ยนสถานะกลับ

# ฟังก์ชันสำหรับจัดการปุ่มขึ้น
def showPushUp(Pin):
    global buttnUp, oled, state, stateMenu, menu, selectMenu, oledPo, monitor  # ใช้ตัวแปร global
    if buttnUp.value() == 0 and state == 0 and monitor == 1:  # ตรวจสอบว่าปุ่มกดขึ้น ถูกกด และอยู่ในสถานะที่เหมาะสม
        state = 1  # เปลี่ยนสถานะ
        if selectMenu != 1:  # ถ้าไม่อยู่บรรทัดที่ 1
            oledPo -= 15  # เลื่อนกรอบขึ้น
            selectMenu -= 1  # ลดบรรทัดที่เลือก
        else:  # ถ้าอยู่บรรทัดที่ 1
            stateMenu -= 1  # เลื่อนเมนูขึ้น
            if stateMenu < 0:  # ตรวจสอบว่าต้อง Reset หรือไม่
                stateMenu = len(menu) - 4  # รีเซ็ตเมนู
                oledPo = 45  # ตั้งตำแหน่งกรอบ
                selectMenu = 4  # ตั้งบรรทัดที่เลือก
    else:
        state = 0  # เปลี่ยนสถานะกลับ

# ฟังก์ชันสำหรับจัดการปุ่มกลาง
def showPushMid(Pin):
    global oled, state, monitor, buttnMid, uart  # ใช้ตัวแปร global
    if buttnMid.value() == 0 and state == 0:  # ตรวจสอบว่าปุ่มกลางถูกกด
        state = 1  # เปลี่ยนสถานะ
        if monitor == 2 or monitor == 5:  # ถ้าอยู่ในสถานะ 2 หรือ 5
            tim0.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t: switchMode())  # เริ่ม Timer เพื่อเปลี่ยนโหมด
        else:
            monitor += 1  # เปลี่ยนสถานะการทำงาน
    else:
        state = 0  # เปลี่ยนสถานะกลับ

# ฟังก์ชันสำหรับสลับโหมดการทำงาน
def switchMode():
    global monitor, buttnMid, uart, flag, lineMenu, selectMenu, quantity, oled, led  # ใช้ตัวแปร global
    if buttnMid.value() == 1 and monitor == 2:  # ตรวจสอบว่าปุ่มกลางถูกปล่อยและอยู่ในสถานะ 2
        uart.write(lineMenu[str(selectMenu)] + '\n')  # ส่งข้อมูลเมนูที่เลือกผ่าน UART
        uart.write(str(quantity) + '\n')  # ส่งจำนวนเครื่องดื่มผ่าน UART
        monitor += 1  # เปลี่ยนสถานะการทำงาน
        flag = 0  # รีเซ็ต flag
        tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: led.value(led.value() ^ 1))  # กระพริบ LED
    elif buttnMid.value() == 0:  # ถ้าปุ่มกลางถูกกด
        if flag == 0:  # ถ้า flag ยังไม่ถูกตั้ง
            tim0.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t: switchMode())  # เริ่ม Timer เพื่อสลับโหมด
            flag = 1  # ตั้ง flag
        else:
            monitor = 1  # รีเซ็ตสถานะการทำงาน
            led.off()  # ปิด LED
            flag = 0  # รีเซ็ต flag

# ติดตั้ง interrupt สำหรับปุ่ม
buttnDown.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPushDown)  # ตั้ง interrupt สำหรับปุ่มลง
buttnUp.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPushUp)  # ตั้ง interrupt สำหรับปุ่มขึ้น
buttnMid.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPushMid)  # ตั้ง interrupt สำหรับปุ่มกลาง

while(1):  # ลูปไม่สิ้นสุด
    adc_value = adc.read()  # อ่านค่าจาก ADC
    oled.fill(0)  # ล้างหน้าจอ OLED
    if monitor == 1:  # ถ้าอยู่ในสถานะ 1
        tim1.deinit()  # หยุด Timer 1
        led.value(0)  # ปิด LED
        lineMenu: dict[str:str] = {  # สร้างดิกชันนารีสำหรับเมนูที่แสดง
            "1": menu[stateMenu],
            "2": menu[stateMenu + 1],
            "3": menu[stateMenu + 2],
            "4": menu[stateMenu + 3]
        }
        oled.text(lineMenu["1"], 2, 5)  # แสดงเมนูบรรทัดที่ 1
        oled.text(lineMenu["2"], 2, 20)  # แสดงเมนูบรรทัดที่ 2
        oled.text(lineMenu["3"], 2, 35)  # แสดงเมนูบรรทัดที่ 3
        oled.text(lineMenu["4"], 2, 50)  # แสดงเมนูบรรทัดที่ 4
        oled.rect(0, oledPo, 128, 15, 1)  # วาดกรอบเพื่อเน้นบรรทัดที่เลือก
        oled.show()  # แสดงผลบน OLED

    elif monitor == 2:  # ถ้าอยู่ในสถานะ 2
        if adc_value <= 819:  # ถ้าอ่านค่า ADC น้อยกว่าหรือเท่ากับ 819
            quantity = 1  # ตั้งค่าปริมาณเป็น 1
        elif adc_value <= 1638:  # ถ้าอ่านค่า ADC น้อยกว่าหรือเท่ากับ 1638
            quantity = 2  # ตั้งค่าปริมาณเป็น 2
        elif adc_value <= 2457:  # ถ้าอ่านค่า ADC น้อยกว่าหรือเท่ากับ 2457
            quantity = 3  # ตั้งค่าปริมาณเป็น 3
        elif adc_value <= 3276:  # ถ้าอ่านค่า ADC น้อยกว่าหรือเท่ากับ 3276
            quantity = 4  # ตั้งค่าปริมาณเป็น 4
        elif adc_value <= 4095:  # ถ้าอ่านค่า ADC น้อยกว่าหรือเท่ากับ 4095
            quantity = 5  # ตั้งค่าปริมาณเป็น 5
        buffer = menuImages[stateMenu + (selectMenu - 1)]  # รับข้อมูลรูปภาพเมนูที่เลือก
        fb = framebuf.FrameBuffer(buffer, 29, 29, framebuf.MONO_HLSB)  # สร้าง frame buffer จากรูปภาพ
        oled.blit(fb, 49, 35)  # แสดงรูปภาพบน OLED
        oled.text(lineMenu[str(selectMenu)], 2, 5)  # แสดงเมนูที่เลือก
        oled.text(f"Quantity: {quantity}", 2, 20)  # แสดงจำนวนที่เลือก
        oled.show()  # แสดงผลบน OLED

    elif monitor == 3:  # ถ้าอยู่ในสถานะ 3
        oled.text("Loading", 25, 20)  # แสดงข้อความ "Loading"
        oled.show()  # แสดงผลบน OLED
        for x in range(1, 16, 5):  # ลูปเพื่อแสดงจุดโหลด
            oled.text(". ", 80 + x, 20)  # แสดงจุดโหลด
            if uart.any():  # ถ้ามีข้อมูลใน UART
                status = uart.readline()  # อ่านข้อมูลจาก UART
                status = status.decode('utf-8').strip()  # แปลงข้อมูลเป็น string
                if status == 'cancel':  # ถ้าข้อความคือ 'cancel'
                    oled.fill(0)  # ล้างหน้าจอ OLED
                    oled.text("Order canceled", 10, 20)  # แสดงข้อความยกเลิกคำสั่ง
                    oled.show()  # แสดงผลบน OLED
                    sleep(1)  # หน่วงเวลา 1 วินาที
                    monitor = 1  # เปลี่ยนสถานะกลับไปที่ 1
                else:
                    monitor = 4  # เปลี่ยนสถานะเป็น 4
                break  # ออกจากลูป
            sleep(0.5)  # หน่วงเวลา 0.5 วินาที
            oled.show()  # แสดงผลบน OLED
            
    elif monitor == 4:  # ถ้าอยู่ในสถานะ 4
        print("Preparing")  # แสดงข้อความ "Preparing" ใน console
        tim1.init(period=500, mode=Timer.PERIODIC, callback=lambda t: led.value(led.value() ^ 1))  # กระพริบ LED
        while True:  # ลูปไม่สิ้นสุด
            oled.text(status, 25, 20)  # แสดงสถานะ
            oled.show()  # แสดงผลบน OLED
            for x in range(1, 16, 5):  # ลูปเพื่อแสดงจุดโหลด
                oled.text(". ", 95 + x, 20)  # แสดงจุดโหลด
                if uart.any():  # ถ้ามีข้อมูลใน UART
                    monitor = 5  # เปลี่ยนสถานะเป็น 5
                    break  # ออกจากลูป
                sleep(0.5)  # หน่วงเวลา 0.5 วินาที
                oled.show()  # แสดงผลบน OLED
            oled.fill(0)  # ล้างหน้าจอ OLED
            if monitor == 5:  # ถ้าอยู่ในสถานะ 5
                uart.write("Order Finish!!!" + "\n")  # ส่งข้อความเสร็จสิ้นคำสั่งผ่าน UART
                break  # ออกจากลูป
    
    elif monitor == 5:  # ถ้าอยู่ในสถานะ 5
        if uart.any():  # ถ้ามีข้อมูลใน UART
            tim1.deinit()  # หยุด Timer 1
            led.on()  # เปิด LED
            print("Finish")  # แสดงข้อความ "Finish" ใน console
            sleep(0.1)  # หน่วงเวลา 0.1 วินาที
            status = uart.readline()  # อ่านสถานะจาก UART
            status = status.decode('utf-8').strip()  # แปลงข้อมูลเป็น string
            oled.text(status, 8, 20)  # แสดงสถานะ
            oled.text("Hold To Pick", 15, 35)  # แสดงข้อความ "Hold To Pick"
            oled.show()  # แสดงผลบน OLED