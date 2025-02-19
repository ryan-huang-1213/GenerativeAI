# GenerativeAI 

## 一般資訊 
姓名：黃國展

系級：資工 115 

課程名稱：生成式AI：文字與圖像生成的原理與實務_國立臺灣師範大學衛星課程

修課學期：113-2

## 使用說明 
 - 為節省時間，建議在 google colab 裡面開啟，以減少架設虛擬系統所需時間
 - 若要在本地進行操作，請先參考 [本地端環境架設](#本地端環境架設)

## 作業

### HW01
1. colab 網址 :
[NTNU_41147047S_CSIE_黃國展_台股每日前十大成交量的擬合曲線.ipynb](https://colab.research.google.com/drive/10wTASH33ZNQgUuLIxnmcH6ymNYb-TrAF?usp=drive_linkLinks)

2. 作業相關重點說明 
 - 主要部分 : 參考每日台股前十大交易量股票，並且進行計算，繪製一個一元三次方程式

 - 額外部分 : 使用繁體中文進行圖表的標註、串接 api 以便獲得運行時當日的股票資訊、使用擬合的方式計算出最接近當日成交量的方程式

3. 以下為運行後的截圖
![HW01_0218](img/HW01/output_0218.png)


## 本地端環境架設
將專案下載至本地端
```bash
# bash
git clone https://github.com/ryan-huang-1213/GenerativeAI.git
cd ./GenerativeAI
```
建立虛擬環境
```bash
# bash 
python -m venv venv
.\venv\bin\activate
pip install -r requirements.txt
source ./venv/bin/activate
```