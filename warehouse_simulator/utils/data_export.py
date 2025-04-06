import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional

from warehouse_simulator.simulation.simulator import WarehouseSimulator
from warehouse_simulator.analysis.movement import MovementAnalyzer
from warehouse_simulator.analysis.efficiency import EfficiencyAnalyzer
from warehouse_simulator.analysis.hotspot import HotspotAnalyzer


class DataExporter:
    """
    シミュレーションデータをエクスポートするクラス
    """
    
    @staticmethod
    def export_all_data(simulator: WarehouseSimulator, 
                       output_dir: str = 'output', 
                       create_visualizations: bool = True) -> Dict[str, Any]:
        """
        すべてのシミュレーションデータをエクスポート
        
        Args:
            simulator: WarehouseSimulatorインスタンス
            output_dir: 出力ディレクトリ
            create_visualizations: 可視化グラフも生成するかどうか
            
        Returns:
            出力されたファイルパスの辞書
        """
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 結果を格納する辞書
        result_files = {}
        
        # 移動データをエクスポート
        movement_analyzer = MovementAnalyzer()
        movement_file = os.path.join(output_dir, 'worker_movements.csv')
        movement_df = movement_analyzer.export_movement_data(simulator.workers, movement_file)
        result_files['movement_data'] = movement_file
        
        # 活動ログをエクスポート
        activity_file = os.path.join(output_dir, 'activity_log.csv')
        activity_df = movement_analyzer.export_activity_log(simulator.workers, activity_file)
        result_files['activity_log'] = activity_file
        
        # 効率性分析
        efficiency_analyzer = EfficiencyAnalyzer()
        efficiency_df = simulator.analyze_worker_efficiency()
        efficiency_file = os.path.join(output_dir, 'worker_efficiency.csv')
        efficiency_df.to_csv(efficiency_file)
        result_files['efficiency_data'] = efficiency_file
        
        # オーダー分析
        order_df = efficiency_analyzer.analyze_order_processing(simulator.orders)
        order_file = os.path.join(output_dir, 'order_analysis.csv')
        order_df.to_csv(order_file)
        result_files['order_analysis'] = order_file
        
        # ホットスポット分析
        hotspot_analyzer = HotspotAnalyzer()
        hotspot_df = hotspot_analyzer.analyze_hotspots(simulator.stats['hotspots'])
        hotspot_file = os.path.join(output_dir, 'hotspots.csv')
        hotspot_df.to_csv(hotspot_file)
        result_files['hotspot_data'] = hotspot_file
        
        # シミュレーション結果サマリー
        summary = simulator.generate_summary()
        summary_df = pd.DataFrame([{k: v for k, v in summary.items() if k != 'worker_stats'}])
        summary_file = os.path.join(output_dir, 'simulation_summary.csv')
        summary_df.to_csv(summary_file, index=False)
        result_files['simulation_summary'] = summary_file
        
        # 作業者統計
        worker_stats_df = pd.DataFrame(summary['worker_stats'])
        worker_stats_file = os.path.join(output_dir, 'worker_stats.csv')
        worker_stats_df.to_csv(worker_stats_file, index=False)
        result_files['worker_stats'] = worker_stats_file
        
        # 可視化グラフの生成
        if create_visualizations:
            # 倉庫マップ
            fig, ax = simulator.warehouse_map.plot()
            map_file = os.path.join(output_dir, 'warehouse_layout.png')
            fig.savefig(map_file)
            plt.close(fig)
            result_files['warehouse_map'] = map_file
            
            # ヒートマップ
            fig, ax = simulator.visualize_heatmap()
            heatmap_file = os.path.join(output_dir, 'heatmap.png')
            fig.savefig(heatmap_file)
            plt.close(fig)
            result_files['heatmap'] = heatmap_file
            
            # 移動経路
            fig, ax = simulator.visualize_path_traces()
            path_file = os.path.join(output_dir, 'path_traces.png')
            fig.savefig(path_file)
            plt.close(fig)
            result_files['path_traces'] = path_file
            
            # 効率性可視化
            fig, ax = efficiency_analyzer.visualize_worker_efficiency(efficiency_df)
            if fig:
                efficiency_vis_file = os.path.join(output_dir, 'efficiency_visualization.png')
                fig.savefig(efficiency_vis_file)
                plt.close(fig)
                result_files['efficiency_visualization'] = efficiency_vis_file
        
        return result_files
    
    @staticmethod
    def create_report(simulator: WarehouseSimulator, output_file: str = 'simulation_report.md') -> None:
        """
        シミュレーション結果のMarkdownレポートを生成
        
        Args:
            simulator: WarehouseSimulatorインスタンス
            output_file: 出力ファイル名
        """
        summary = simulator.generate_summary()
        efficiency_df = simulator.analyze_worker_efficiency()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # ヘッダー
            f.write("# 倉庫内人流シミュレーション結果レポート\n\n")
            f.write(f"シミュレーション時間: {summary['simulation_time']:.1f}秒\n\n")
            
            # 概要
            f.write("## シミュレーション概要\n\n")
            f.write(f"- 総オーダー数: {summary['total_orders']}\n")
            f.write(f"- 完了オーダー数: {summary['completed_orders']}\n")
            f.write(f"- 完了率: {summary['completion_rate']*100:.1f}%\n")
            f.write(f"- 総ピック商品数: {summary['total_items_picked']}\n")
            f.write(f"- 総移動距離: {summary['total_distance']:.1f}\n")
            f.write(f"- 単位距離あたりのピック数: {summary['items_per_distance']:.3f}\n")
            f.write(f"- 平均オーダー完了時間: {summary['avg_order_completion_time']:.1f}秒\n\n")
            
            # 作業者統計
            f.write("## 作業者統計\n\n")
            f.write("| 作業者ID | ピック数 | 移動距離 | 効率(ピック/距離) |\n")
            f.write("|----------|----------|----------|------------------|\n")
            for worker_stat in summary['worker_stats']:
                f.write(f"| {worker_stat['worker_id']} | {worker_stat['total_items_picked']} | {worker_stat['total_distance']:.1f} | {worker_stat['efficiency']:.3f} |\n")
            
            f.write("\n## 効率性分析\n\n")
            f.write("作業者の効率性指標：\n\n")
            f.write("```\n")
            f.write(str(efficiency_df))
            f.write("\n```\n\n")
            
            # 改善提案
            f.write("## 改善提案\n\n")
            f.write("1. 最も頻繁に訪問される通路を広げ、混雑を減らすことを検討\n")
            f.write("2. 高頻度でピックされる商品をピッキングステーションに近い場所に配置\n")
            f.write("3. 効率の低い作業者に対してトレーニングを実施\n")
            f.write("4. オーダーのバッチ処理を最適化し、類似したピック場所のオーダーをグループ化\n")
            
            print(f"レポートを {output_file} に保存しました")
