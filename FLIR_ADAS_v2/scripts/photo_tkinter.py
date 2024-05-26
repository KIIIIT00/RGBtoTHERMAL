# -*- coding: utf-8 -*-
"""
Created on Mon May 20 14:51:46 2024

@author: Kawahara
"""

### インポート
import tkinter
import tkinter.filedialog
from PIL import Image,ImageTk,ImageOps
import os
 
### 定数
WIDTH  = 640        # 幅
HEIGHT = 512        # 高さ
global TARGET_FILE_PATH
TARGET_FILE_PATH =""
### 関数(開く)
def f_open():
 
    ### グローバル変数
    global image
    global name
 
    ### ファイルダイアログ
    name = tkinter.filedialog.askopenfilename(title="ファイル選択", initialdir="./", filetypes=[("Image File","*.png;*.jpg")])
    TARGET_FILE_PATH = name
    ### 画像ロード
    image = Image.open(name)
    image = ImageOps.pad(image, (WIDTH,HEIGHT))
    image = ImageTk.PhotoImage(image=image)
 
    ### キャンバスに表示
    canvas.create_image(WIDTH/2, HEIGHT/2, image=image)

 
### 関数(閉じる)
def f_close():
 
    ### キャンバスクリア
    canvas.delete("all")
def get_name():
    TARGET_FILE = os.path.basename(TARGET_FILE_PATH)
    print(TARGET_FILE)
# Maine関数
if __name__ == '__main__':
    ### メイン画面作成
    main = tkinter.Tk()
     
    ### 画面サイズ設定
    main.geometry("640x512")
     
    ### メニューバー作成
    menubar = tkinter.Menu(main)
     
    ### ファイルメニュー作成
    filemenu = tkinter.Menu(menubar, tearoff=0)
    filemenu.add_command(label="開く", command=f_open)
    filemenu.add_command(label="閉じる", command=f_close)
    filemenu.add_separator()
    filemenu.add_command(label="終了", command=main.quit)
    get_name()
     
    ### メニュー設定
    menubar.add_cascade(label="ファイル", menu=filemenu)
     
    ### メニューバー配置
    main.config(menu=menubar)
     
    ### キャンバス作成・配置
    canvas = tkinter.Canvas(main, width=WIDTH, height=HEIGHT)
    canvas.pack()
     
    ### イベントループ
    main.mainloop()