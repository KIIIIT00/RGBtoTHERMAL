import cv2

cap = cv2.VideoCapture(1)
cap_thermal = cv2.VideoCapture(0, cv2.CAP_MSMF)
#print(type(cap))
print(type(cap_thermal))
#print(cap.isOpened())
print(cap_thermal.isOpened())
while True:
  # 1フレームずつ取得する。
  ret, frame = cap.read()
  ret1, frame2 = cap_thermal.read()
  print(ret1)
  #print(ret1)
  #フレームが取得できなかった場合は、画面を閉じる
  #if not ret:
  #  break
    
  # ウィンドウに出力
  cv2.imshow("Frame", frame)
  cv2.imshow("Thermal", frame2)
  key = cv2.waitKey(0)
  # Escキーを入力されたら画面を閉じる
  if key == 27:
    break
cap.release()
cap_thermal.release()
cv2.destroyAllWindows()