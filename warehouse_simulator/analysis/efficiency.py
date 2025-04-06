import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Any, Optional

from warehouse_simulator.models.worker import WarehouseWorker
from warehouse_simulator.models.order import Order


class EfficiencyAnalyzer:
    """
    作業効率を分析するクラス
    """
    
    @staticmethod
    def analyze_worker_efficiency(workers: List[WarehouseWorker], 
                                 current_time: float) -> pd.DataFrame:
        """
        作業者の効率性を分析
        
        Args:
            workers: 作業者リスト
            current_time: 現在のシミュレーション時間
            
        Returns:
            効率性データのDataFrame
        """
        efficiency_data = []
        
        for worker in workers:
            # 効率性指標を計算
            distance_per_item = worker.total_distance / max(1, worker.total_items_picked)
            items_per_second = worker.total_items_picked / max(1, current_time)
            
            # 結果を追加
            efficiency_data.append({
                'worker_id': worker.worker_id,
                'total_distance': worker.total_distance,
                'total_items_picked': worker.total_items_picked,
                'distance_per_item': distance_per_item,
                'items_per_second': items_per_second,
                'efficiency_score': (1 / distance_per_item) * items_per_second  # 総合効率スコア
            })
        
        return pd.DataFrame(efficiency_data)
    
    @staticmethod
    def analyze_order_processing(orders: List[Order]) -> pd.DataFrame:
        """
        オーダー処理の効率性を分析
        
        Args:
            orders: オーダーリスト
            
        Returns:
            オーダー分析のDataFrame
        """
        order_data = []
        
        for order in orders:
            # 処理時間を計算
            processing_time = order.get_processing_time()
            
            # オーダーの元の商品数を推定（ピック済み + 残り）
            original_items = len(order.items)
            if order.is_completed():
                original_items = 0  # 完了済みの場合は残りはゼロ
            
            # 結果を追加
            order_data.append({
                'order_id': order.order_id,
                'priority': order.priority,
                'original_items': original_items,
                'remaining_items': len(order.items),
                'created_time': order.created_time,
                'completed_time': order.completed_time,
                'processing_time': processing_time,
                'is_completed': order.is_completed(),
                'assigned_worker': order.assigned_worker
            })
        
        return pd.DataFrame(order_data)
    
    @staticmethod
    def visualize_worker_efficiency(efficiency_df: pd.DataFrame, figsize: Tuple[int, int] = (10, 6)):
        """
        作業者の効率性を可視化
        
        Args:
            efficiency_df: 効率性データのDataFrame
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 作業者IDをインデックスに設定
        if not efficiency_df.empty:
            efficiency_df = efficiency_df.set_index('worker_id')
            
            # 効率性指標を棒グラフで表示
            efficiency_df[['distance_per_item', 'items_per_second', 'efficiency_score']].plot(
                kind='bar', ax=ax)
            
            ax.set_title('作業者の効率性比較')
            ax.set_xlabel('作業者ID')
            ax.set_ylabel('効率性指標')
            ax.legend(loc='best')
        
        plt.tight_layout()
        return fig, ax
