# 倉庫内人流解析シミュレータ (Warehouse Flow Simulator)

倉庫内での作業者の動きをシミュレーションし、効率的なピッキング作業の分析と最適化を支援するPythonライブラリです。

## 特徴

- 2D倉庫レイアウトの表現とカスタマイズ
- 複数作業者の同時シミュレーション
- A*アルゴリズムによる最短経路探索
- リアルタイムの人流データ収集
- ヒートマップや移動パターンの可視化
- 効率性分析とボトルネック検出
- アニメーションによる直感的な理解

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/warehouse-flow-simulator.git
cd warehouse-flow-simulator

# 依存パッケージのインストール
pip install -r requirements.txt

# インストール
pip install -e .
```

## 使用例

基本的なシミュレーションの実行:

```python
from warehouse_simulator.models.warehouse_map import WarehouseMap
from warehouse_simulator.models.worker import WarehouseWorker
from warehouse_simulator.simulation.simulator import WarehouseSimulator

# シミュレータの初期化
simulator = WarehouseSimulator(width=20, height=15, num_workers=3)

# オーダーの生成
for _ in range(5):
    simulator.generate_random_order()

# シミュレーションの実行
summary = simulator.run_simulation(steps=100)

# 結果の分析
simulator.visualize_heatmap()
efficiency_df = simulator.analyze_worker_efficiency()
```

より詳細な使用例は `examples` ディレクトリを参照してください。

## 要件

- Python 3.7+
- NumPy
- Pandas
- Matplotlib
- NetworkX

## ドキュメント

詳細なドキュメントは [ドキュメントサイト](https://yourusername.github.io/warehouse-flow-simulator) を参照してください。

## ライセンス

MIT License

## 貢献

貢献は歓迎します！バグ報告、機能リクエスト、プルリクエストなどはGitHubの[Issues](https://github.com/yourusername/warehouse-flow-simulator/issues)にお願いします。
