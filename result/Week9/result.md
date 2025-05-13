# 幾何圖形生成器輸入輸出紀錄

## 0. 題目敘述
畫一個平行四邊形 ABCD
## 1. Constraints JSON
```json
{
  "figure": "平行四邊形",
  "vertices": ["A", "B", "C", "D"],
  "edges": [
    {"start": "A", "end": "B"},
    {"start": "B", "end": "C"},
    {"start": "C", "end": "D"},
    {"start": "D", "end": "A"}
  ],
  "properties": {
    "opposite_sides_parallel": true,
    "opposite_sides_equal": true,
    "opposite_angles_equal": true
  }
}
```
2. Parameters JSON
```json
{
  "points": {
    "A": [0, 0],
    "B": [2, 0],
    "C": [3, 2],
    "D": [1, 2]
  },
  "structure": {
    "type": "平行四邊形",
    "vertices": ["A", "B", "C", "D"],
    "edges": [
      {"start": "A", "end": "B"},
      {"start": "B", "end": "C"},
      {"start": "C", "end": "D"},
      {"start": "D", "end": "A"}
    ]
  }
}
```
3. generated plt 腳本 
``` py
import matplotlib.pyplot as plt
import json

parameters = {
  "points": {
    "A": [0, 0],
    "B": [2, 0],
    "C": [3, 2],
    "D": [1, 2]
  },
  "structure": {
    "type": "平行四邊形",
    "vertices": ["A", "B", "C", "D"],
    "edges": [
      {"start": "A", "end": "B"},
      {"start": "B", "end": "C"},
      {"start": "C", "end": "D"},
      {"start": "D", "end": "A"}
    ]
  }
}

points = parameters["points"]
structure = parameters["structure"]
vertices = structure["vertices"]
edges = structure["edges"]

x = []
y = []
for vertex in vertices:
    x.append(points[vertex][0])
    y.append(points[vertex][1])

x.append(x[0])
y.append(y[0])

plt.figure(figsize=(6,6))
plt.plot(x, y, '-o')

for i, vertex in enumerate(vertices):
    plt.annotate(vertex, (x[i], y[i]))

plt.title(structure["type"])
plt.gca().set_aspect('equal')
plt.savefig('./log/plot.png')
plt.show()
```
4. reflection 建議
```markdown
### 程式碼審閱和優化

以下是對提供的Matplotlib腳本的審閱和優化建議：

#### 1. 引入和命名

*   引入的模組命名良好，但可以考慮使用 `import` 來匯入指定的函式或變數以節省記憶體。
*   變數名稱如 `parameters`、`points`、`structure` 等命名清晰，但若有更多複雜的資料結構，可能需要考慮使用類別或函式來組織。

#### 2. 資料處理

*   現在的程式碼會先將所有頂點的座標抓出來，接著繪製，這是一種有效的方法。
*   考慮到可能會有多種不同的形狀或結構，可能需要設計函式來進行繪製，以增加程式的可重複使用性。

#### 3. Matplotlib 的使用

*   `plt.figure(figsize=(6,6))` 用於設定圖片大小， `-o` 參數用於設定圖型為線段加原點，但這些設定都正確。
*   `plt.title(structure["type"])` 和 `plt.gca().set_aspect('equal')` 正確地設定了圖片的標題和長寬比。
*   考慮到圖片保存，程式碼已經正確地使用 `plt.savefig('./log/plot.png')` 保存圖片。

#### 4. 可讀性和維護性

*   程式碼結構清晰，但在較大的專案中，可能需要考慮如何將不同功能（如資料載入、圖表繪製等）模組化。
*   可以考慮在函式中增加一些錯誤處理機制，例如當輸入資料不正確時的反饋。

#### 優化後的程式碼

以下是一個優化後的版本，其中增加了函式並進行了一些簡單的錯誤處理：

```python
import matplotlib.pyplot as plt
import json

def load_parameters(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("檔案路徑錯誤。")
        return None

def extract_points_and_structure(parameters):
    points = parameters.get("points")
    structure = parameters.get("structure")
    if points is None or structure is None:
        print("參數結構不正確。")
        return None, None
    return points, structure

def plot_shape(points, structure):
    vertices = structure.get("vertices")
    edges = structure.get("edges")
    if vertices is None or edges is None:
        print("結構資料不完整。")
        return

    x = [points[vertex][0] for vertex in vertices]
    y = [points[vertex][1] for vertex in vertices]
    x.append(x[0])
    y.append(y[0])

    plt.figure(figsize=(6,6))
    plt.plot(x, y, '-o')
    for i, vertex in enumerate(vertices):
        plt.annotate(vertex, (x[i], y[i]))
    plt.title(structure["type"])
    plt.gca().set_aspect('equal')
    plt.savefig('./log/plot.png')
    plt.show()

def main():
    parameters_file_path = 'parameters.json'  # 假設有一个json檔案存放parameters
    parameters = load_parameters(parameters_file_path)
    if parameters is not None:
        points, structure = extract_points_and_structure(parameters)
        if points is not None and structure is not None:
            plot_shape(points, structure)

if __name__ == "__main__":
    main()
/```

### 小結

這個優化過的版本透過使用函式、增加錯誤處理和模組化來提高程式碼的可讀性、可維護性和錯誤處理能力。它假設有一個 JSON 檔案包含 `parameters` 的資料結構，並使用此結構繪製圖形。
```