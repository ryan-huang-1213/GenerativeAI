# GenerativeAI 

## 一般資訊 
姓名：黃國展

系級：資工 115 

課程名稱：生成式AI：文字與圖像生成的原理與實務_國立臺灣師範大學衛星課程

修課學期：113-2

## 使用說明 
 - 為節省時間，建議在 google colab 裡面開啟，以減少架設虛擬系統所需時間

## 作業

### HW01
**1. colab 網址 :**
[NTNU_41147047S_CSIE_黃國展_台股每日前十大成交量的擬合曲線.ipynb](https://colab.research.google.com/drive/10wTASH33ZNQgUuLIxnmcH6ymNYb-TrAF?usp=drive_linkLinks)

**2. 作業相關重點說明**
 - 主要部分 : 參考每日台股前十大交易量股票，並且進行計算，繪製一個一元三次方程式

 - 額外部分 : 使用繁體中文進行圖表的標註、串接 api 以便獲得運行時當日的股票資訊、使用擬合的方式計算出最接近當日成交量的方程式

**3. 以下為運行後的截圖**
![HW01_0218](img/HW01/output_0218.png)

### HW02 
**1. colab 網址 :**
[NTNU_41147047S_CSIE_黃國展_第一個神經網路.ipynb](https://colab.research.google.com/drive/1BpF-ga4kQRrdqR6OyWO_Aq1ITk7iB7vQ#scrollTo=FWK0fgKgCHa7)
**2. 主題與額外內容**
該作業主要是訓練出一個可以辨識 0~9 的神經網路，以下為有更改的內容

 - 修改神經元參數 => [16,16,16]
 - 利用 ReduceLROnPlateau 以及 SGD 動態調整 learning rate
 - model.fit 部分呼叫函式，當 loss 多次未改善時，減少 learning rate
 - 針對圖形前處理進行改進，避免文字過小縮小後細節缺失等問題

**3. 重要截圖**

圖片前處理調整比較圖

![before](img/HW02/before.webp)
![after](img/HW02/after.webp)

運行結果
![result](img/HW02/result.png)


## HW03 

**1. colab 網址 : **
[連結](https://colab.research.google.com/drive/16C-mYX6QEWY4Z9uek8rVzwRYj06-tBVX?hl=zh-tw#scrollTo=lZ9E9HZSpfHF)
