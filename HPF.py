import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Arduino과 연결된 시리얼 폴트 설정
ser = serial.Serial('/dev/cu.usbmodem1301', 115200)  # 폴트를 '/dev/cu.usbmodem1401'로 설정
numRows, numCols = 16, 16

# 시간과 설정
plt.style.use('dark_background')
fig, ax = plt.subplots()

# 'inferno' 색상 맵과 bilinear 보간을 사용해 더 불량고 명확하게 표현
img = ax.imshow(np.zeros((numRows, numCols)), cmap='inferno', interpolation='bilinear', vmin=0, vmax=100)
plt.colorbar(img, ax=ax, label="Pressure Intensity")

# HPF 활용 기능을 포함한 데이터 가공 함수
def apply_hpf(data, threshold=30):
    return np.where(data > threshold, data, 0)

def update_data(*args):
    global ser
    pressure_matrix1 = np.zeros((numRows, numCols))
    pressure_matrix2 = np.zeros((numRows, numCols))
    
    sensor1_active = False
    sensor2_active = False
    
    # 데이터 읽기
    for sensor in range(2):  # 0: Sensor 1, 1: Sensor 2
        row = 0
        while row < numRows:
            line = ser.readline().decode().strip()
            # 데이터 시작을 확인하는 문자열에 대한 체크
            if "Pressure Sensor 1 Data:" in line:
                sensor1_active = True
                print("Reading Pressure Sensor 1 Data...")
                continue
            elif "Pressure Sensor 2 Data:" in line:
                sensor2_active = True
                print("Reading Pressure Sensor 2 Data...")
                continue
            
            # 데이터 처리
            if sensor1_active and sensor == 0:
                if line == "END":
                    break
                values = line.split(',')
                if len(values) == numCols:
                    print(f"Sensor 1 Row {row}: {values}")
                    pressure_matrix1[row] = list(map(int, values))
                    row += 1

            elif sensor2_active and sensor == 1:
                if line == "END":
                    break
                values = line.split(',')
                if len(values) == numCols:
                    print(f"Sensor 2 Row {row}: {values}")
                    pressure_matrix2[row] = list(map(int, values))
                    row += 1

    # 실시간 데이터 업데이트
    img.set_data(pressure_matrix1)
    # img2.set_data(pressure_matrix2)
    
    return [img]


# 애니먼이션으로 실시간 업데이트 설정
ani = animation.FuncAnimation(fig, update_data, interval=100, blit=False)  # 딩레이 100ms로 설정
plt.title("Real-Time Pressure Sensor Visualization with HPF (16x16)")
plt.show()
