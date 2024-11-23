from machine import UART, Pin, SoftI2C, Timer  # นำเข้าโมดูลที่จำเป็นสำหรับการควบคุม UART, GPIO, I2C และ Timer
from time import sleep  # นำเข้า sleep สำหรับการหน่วงเวลา
import ssd1306, framebuf  # นำเข้าไลบรารีสำหรับควบคุมจอ OLED และจัดการ frame buffer

# สร้าง UART ที่พอร์ต 1 โดยใช้ TX = GPIO17, RX = GPIO16
uart = UART(1, baudrate=115200, tx=17, rx=16)  # กำหนดการตั้งค่า UART สำหรับการสื่อสาร
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))  # ตั้งค่า I2C โดยใช้ Pin 22 เป็น SCL และ Pin 21 เป็น SDA

# กำหนดขนาดของหน้าจอ OLED
width: int = 128  # ความกว้างของ OLED
height: int = 64  # ความสูงของ OLED
led = Pin(2, Pin.OUT)  # กำหนด LED ที่ Pin 2 ให้เป็น OUTPUT
oled = ssd1306.SSD1306_I2C(width, height, i2c)  # สร้างวัตถุ OLED โดยใช้ I2C
buttn = Pin(13, Pin.IN, Pin.PULL_UP)  # ปุ่มที่ Pin 13 ถูกตั้งเป็น INPUT พร้อม Pull-Up
flag: int = 0  # ตัวแปรสถานะสำหรับการติดตามการกดปุ่ม
state: int = 0  # ตัวแปรสถานะสำหรับติดตามสถานะการทำงาน
monitor: int = 1  # ตัวแปรสำหรับติดตามสถานะปัจจุบัน
flagMonitor: int = 0  # ตัวแปรติดตามสถานะการทำงานของ monitor
tim0 = Timer(0)  # สร้าง Timer 0 สำหรับการทำงานที่เกี่ยวข้องกับปุ่ม
tim1 = Timer(1)  # สร้าง Timer 1 สำหรับการกระพริบ LED
led.off()  # ปิด LED โดยเริ่มต้น

# ฟังก์ชันสำหรับจัดการการกดปุ่ม
def showPush(Pin):
    global chooseMenu, buttn, state, flag, monitor  # ใช้ตัวแปร global
    if buttn.value() == 0 and state == 0:  # ถ้าปุ่มถูกกดและสถานะเป็น 0
        state = 1  # เปลี่ยนสถานะเป็น 1
        if monitor == 1:  # ถ้าอยู่ในสถานะ 1
            tim0.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t: action())  # เริ่ม Timer เพื่อเรียกฟังก์ชัน action
        elif monitor == 2:  # ถ้าอยู่ในสถานะ 2
            uart.write("Order Finish!!!" + '\n')  # ส่งข้อความ "Order Finish!!!" ผ่าน UART
            monitor = 3  # เปลี่ยนสถานะเป็น 3
    else:
        state = 0  # เปลี่ยนสถานะกลับเป็น 0

# ฟังก์ชันสำหรับการจัดการสถานะต่างๆ
def action():
    global buttn, flag, uart, monitor, led  # ใช้ตัวแปร global
    if buttn.value() == 1:  # ถ้าปุ่มถูกปล่อย
        tim1.init(period=500, mode=Timer.PERIODIC, callback=lambda t: led.value(led.value() ^ 1))  # เริ่ม Timer เพื่อกระพริบ LED
        monitor += 1  # เปลี่ยนสถานะ monitor ขึ้น 1
        uart.write("Preparing" + '\n')  # ส่งข้อความ "Preparing" ผ่าน UART
        sleep(0.3)  # หน่วงเวลา 0.3 วินาที
        
    elif buttn.value() == 0:  # ถ้าปุ่มถูกกด
        if flag == 0:  # ถ้า flag ยังไม่ถูกตั้ง
            tim0.init(period=1000, mode=Timer.ONE_SHOT, callback=lambda t: action())  # เริ่ม Timer ใหม่
            flag = 1  # ตั้ง flag เป็น 1
        else:
            flag = 0  # รีเซ็ต flag เป็น 0
            monitor = 1  # เปลี่ยนสถานะกลับเป็น 1
            oled.fill(0)  # ล้างหน้าจอ OLED
            led.off()  # ปิด LED
            uart.write("cancel" + '\n')  # ส่งข้อความ "cancel" ผ่าน UART
            tim1.deinit()  # หยุด Timer 1
            led.off()  # ปิด LED

# ติดตั้ง interrupt สำหรับปุ่ม
buttn.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=showPush)  # ตั้งค่า interrupt สำหรับการกดปุ่ม

while(1):  # ลูปไม่สิ้นสุด
    if monitor == 1:  # ถ้าอยู่ในสถานะ 1
        oled.text("Order", 43, 5)  # แสดงข้อความ "Order" บน OLED
        oled.show()  # แสดงผลบน OLED
        if uart.any():  # ตรวจสอบว่ามีข้อมูลเข้ามาหรือไม่
            sleep(0.3)  # หน่วงเวลา 0.3 วินาที
            status = uart.readline()  # อ่านข้อมูลจาก UART
            status = status.decode('utf-8').strip()   # แปลงข้อมูลจาก bytes เป็น string
            print(status)  # แสดงข้อมูลใน console
            if flag == 0:  # ถ้า flag เป็น 0
                tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: led.value(led.value() ^ 1))  # กระพริบ LED
                flag = 1  # ตั้ง flag เป็น 1
                oled.fill(0)  # ล้างหน้าจอ OLED
                oled.text(status, 2, 20)  # แสดงสถานะที่ได้รับบน OLED
            elif flag == 1:  # ถ้า flag เป็น 1
                flag = 0  # รีเซ็ต flag
                oled.text(status, 110, 20)  # แสดงสถานะที่ได้รับในตำแหน่งที่ต่างออกไป
            oled.show()  # แสดงผลบน OLED
    elif monitor == 2:  # ถ้าอยู่ในสถานะ 2
        print("Preparing")  # แสดงข้อความ "Preparing" ใน console
        oled.fill(0)  # ล้างหน้าจอ OLED
        oled.text("Preparing", 25, 20)  # แสดงข้อความ "Preparing" บน OLED
        oled.text("Press To Confirm", 2, 35)  # แสดงข้อความ "Press To Confirm" บน OLED
        oled.show()  # แสดงผลบน OLED
        for x in range(1, 16, 5):  # ลูปเพื่อแสดงจุดโหลด
            oled.text(". ", 95 + x, 20)  # แสดงจุดโหลด
            if uart.any():  # ถ้ามีข้อมูลเข้ามาใน UART
                print("Here")  # แสดงข้อความ "Here" ใน console
                break  # ออกจากลูป
            sleep(0.5)  # หน่วงเวลา 0.5 วินาที
            oled.show()  # แสดงผลบน OLED
    elif monitor == 3:  # ถ้าอยู่ในสถานะ 3
        if uart.any():  # ถ้ามีข้อมูลเข้ามาใน UART
            print("Finish")  # แสดงข้อความ "Finish" ใน console
            tim1.deinit()  # หยุด Timer 1
            led.on()  # เปิด LED
            sleep(0.3)
            status = uart.readline()  # อ่านข้อมูลจาก UART
            status = status.decode('utf-8').strip()  # แปลงข้อมูลเป็น string
            oled.fill(0)  # ล้างหน้าจอ OLED
            oled.text(status, 6, 20)  # แสดงสถานะที่ได้รับบน OLED
            oled.show()  # แสดงผลบน OLED
            sleep(2)  # หน่วงเวลา 2 วินาที
            monitor = 1  # เปลี่ยนสถานะกลับไปที่ 1
            oled.fill(0)  # ล้างหน้าจอ OLED
            tim1.deinit()  # หยุด Timer 1
            led.off()  # ปิด LED
