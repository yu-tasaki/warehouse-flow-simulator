import os
import sys
import matplotlib.pyplot as plt

# モジュールのインポートパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from warehouse_simulator.models.warehouse_map import WarehouseMap
from warehouse_simulator.simulation.simulator import WarehouseSimulator
from warehouse_simulator.analysis.efficiency import EfficiencyAnalyzer
from warehouse_simulator.analysis.movement import MovementAnalyzer
from warehouse_simulator.analysis.hotspot import HotspotAnalyzer
from warehouse_simulator.utils.data_export import DataExporter


def run_basic_simulation():
    """基本的なシミュレーションを実行"""
    print("=== 基本的な倉庫シミュレーションを開始 ===")
    
    # 倉庫シミュレータを初期化
    simulator = WarehouseSimulator(width=20, height=15, num_workers=3)
    
    # 倉庫マップを表示
    fig, ax = simulator.warehouse_map.plot()
    plt.savefig('output/warehouse_layout.png')
    plt.close(fig)
    print("倉庫レイアウトを保存しました: output/warehouse_layout.png")
    
    # 数件のオーダーを生成
    for _ in range(5):
        simulator.generate_random_order(min_items=2, max_items=4)
    
    print(f"オーダーを生成しました: {len(simulator.orders)} 件")
    
    # シミュレーションを実行
    summary = simulator.run_simulation(steps=100, order_frequency=0.1)
    
    # 結果を表示
    print("\n=== シミュレーション結果サマリー ===")
    for key, value in summary.items():
        if key != 'worker_stats':
            print(f"{key}: {value}")
    
    print("\n=== 作業者ごとの統計 ===")
    for worker_stat in summary['worker_stats']:
        print(f"作業者 {worker_stat['worker_id']}:")
        print(f"  ピック数: {worker_stat['total_items_picked']}")
        print(f"  移動距離: {worker_stat['total_distance']:.2f}")
        print(f"  効率: {worker_stat['efficiency']:.4f} (ピック/距離)")
    
    # 分析と可視化
    efficiency_df = simulator.analyze_worker_efficiency()
    print("\n=== 作業者効率分析 ===")
    print(efficiency_df)
    
    # ヒートマップを表示
    fig, ax = simulator.visualize_heatmap()
    plt.savefig('output/warehouse_heatmap.png')
    plt.close(fig)
    print("ヒートマップを保存しました: output/warehouse_heatmap.png")
    
    # 移動経路を可視化
    fig, ax = simulator.visualize_path_traces()
    plt.savefig('output/worker_path_traces.png')
    plt.close(fig)
    print("移動経路を保存しました: output/worker_path_traces.png")
    
    # データエクスポート
    data_exporter = DataExporter()
    result_files = data_exporter.export_all_data(simulator, 'output')
    print("\n=== エクスポートしたファイル ===")
    for key, filepath in result_files.items():
        print(f"{key}: {filepath}")
    
    # レポート生成
    data_exporter.create_report(simulator, 'output/simulation_report.md')
    
    print("\nシミュレーションを完了しました。")


if __name__ == "__main__":
    # 出力ディレクトリの作成
    os.makedirs('output', exist_ok=True)
    
    # シミュレーションを実行
    run_basic_simulation()
