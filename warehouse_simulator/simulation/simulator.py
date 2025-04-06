import random
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from typing import Dict, List, Tuple, Optional, Any

from warehouse_simulator.models.warehouse_map import WarehouseMap
from warehouse_simulator.models.worker import WarehouseWorker
from warehouse_simulator.models.order import Order

matplotlib.rcParams['font.family'] = 'MS Gothic'  # Windows用
# Macの場合は 'Hiragino Sans GB' や 'AppleGothic'、Linuxの場合は 'IPAGothic' などに変更
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

class WarehouseSimulator:
    """
    倉庫シミュレーション全体を管理するクラス
    """
    
    def __init__(self, width: int = 20, height: int = 15, num_workers: int = 3):
        """
        シミュレータを初期化
        
        Args:
            width: 倉庫の幅
            height: 倉庫の高さ
            num_workers: 作業者の数
        """
        self.warehouse_map = WarehouseMap(width, height)
        self.workers: List[WarehouseWorker] = []
        self.orders: List[Order] = []
        self.pending_orders: List[Order] = []
        self.completed_orders: List[Order] = []
        self.current_time: float = 0.0
        self.time_step: float = 1.0  # 1ステップ = 1秒
        
        # 作業者を初期化
        for i in range(num_workers):
            worker = WarehouseWorker(i+1, self.warehouse_map)
            self.workers.append(worker)
        
        # シミュレーション用の統計情報
        self.stats: Dict[str, Any] = {
            'total_orders': 0,
            'completed_orders': 0,
            'total_items_picked': 0,
            'total_distance': 0,
            'avg_order_completion_time': 0,
            'worker_utilization': {},
            'hotspots': {}  # 倉庫内の特に活動が多い場所
        }
    
    def generate_random_order(self, min_items: int = 1, max_items: int = 5) -> Optional[Order]:
        """
        ランダムなオーダーを生成
        
        Args:
            min_items: 最小商品数
            max_items: 最大商品数
            
        Returns:
            生成されたオーダー、または失敗時はNone
        """
        order_id = len(self.orders) + 1
        num_items = random.randint(min_items, max_items)
        
        # ランダムに商品を選択
        available_products = list(self.warehouse_map.storage_locations.keys())
        if not available_products:
            return None
        
        items = random.sample(available_products, min(num_items, len(available_products)))
        priority = random.randint(1, 3)  # 1=高、2=中、3=低
        
        new_order = Order(order_id, items, priority)
        self.orders.append(new_order)
        self.pending_orders.append(new_order)
        self.stats['total_orders'] += 1
        
        return new_order
    
    def assign_orders(self) -> None:
        """保留中のオーダーを作業者に割り当て"""
        # 優先度順にオーダーをソート
        self.pending_orders.sort(key=lambda x: x.priority)
        
        # 空いている作業者を探してオーダーを割り当て
        for order in self.pending_orders[:]:
            for worker in self.workers:
                if not worker.is_busy:
                    worker.assign_order(order)
                    self.pending_orders.remove(order)
                    break
    
    def update(self) -> None:
        """シミュレーションを1ステップ進める"""
        self.current_time += self.time_step
        
        # 作業者の移動を更新
        for worker in self.workers:
            if worker.is_busy:
                worker.move(self.current_time)
                
                # オーダー完了を確認し、完了していれば完了リストに追加
                if worker.current_order is None and worker.is_busy == False:
                    # 直前のオーダーを探す
                    for order in self.orders:
                        if order.assigned_worker == worker.worker_id and order.is_completed():
                            if order not in self.completed_orders:
                                self.completed_orders.append(order)
                                break
        
        # 新しいオーダーを割り当て
        self.assign_orders()
        
        # 統計情報を更新
        self._update_stats()
    
    def _update_stats(self) -> None:
        """統計情報を更新"""
        # 完了したオーダーの数
        self.stats['completed_orders'] = len(self.completed_orders)
        
        # 総ピック数
        total_items = sum(worker.total_items_picked for worker in self.workers)
        self.stats['total_items_picked'] = total_items
        
        # 総移動距離
        total_distance = sum(worker.total_distance for worker in self.workers)
        self.stats['total_distance'] = total_distance
        
        # 平均オーダー完了時間
        if self.completed_orders:
            # 完了したオーダーのみを対象に
            processing_times = [order.get_processing_time() for order in self.completed_orders 
                            if order.completed_time is not None]
            if processing_times:  # 空でないことを確認
                avg_time = sum(processing_times) / len(processing_times)
                self.stats['avg_order_completion_time'] = avg_time
            else:
                self.stats['avg_order_completion_time'] = 0.0
        else:
            self.stats['avg_order_completion_time'] = 0.0
        
        # 作業者の稼働率
        for worker in self.workers:
            self.stats['worker_utilization'][worker.worker_id] = 1.0 if worker.is_busy else 0.0
        
        # ヒートマップ用のデータ収集
        for worker in self.workers:
            for _, x, y in worker.movement_history:
                pos = (x, y)
                self.stats['hotspots'][pos] = self.stats['hotspots'].get(pos, 0) + 1
    
    def run_simulation(self, steps: int = 100, order_frequency: float = 0.1) -> Dict[str, Any]:
        """
        指定したステップ数だけシミュレーションを実行
        
        Args:
            steps: シミュレーションのステップ数
            order_frequency: 各ステップでのオーダー生成確率
            
        Returns:
            シミュレーション結果のサマリー
        """
        for step in range(steps):
            # ランダムにオーダーを生成
            if random.random() < order_frequency:
                self.generate_random_order()
            
            # シミュレーションを1ステップ進める
            self.update()
            
            # 進捗状況を表示
            if step % 10 == 0:
                print(f"シミュレーション進捗: {step}/{steps} ステップ完了")
        
        print("シミュレーション完了")
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        シミュレーション結果のサマリーを生成
        
        Returns:
            結果サマリー
        """
        summary = {
            'simulation_time': self.current_time,
            'total_orders': self.stats['total_orders'],
            'completed_orders': self.stats['completed_orders'],
            'completion_rate': self.stats['completed_orders'] / max(1, self.stats['total_orders']),
            'total_items_picked': self.stats['total_items_picked'],
            'total_distance': self.stats['total_distance'],
            'items_per_distance': self.stats['total_items_picked'] / max(1, self.stats['total_distance']),
            'avg_order_completion_time': self.stats['avg_order_completion_time'],
            'worker_stats': []
        }
        
        # 作業者ごとの統計情報
        for worker in self.workers:
            worker_stats = {
                'worker_id': worker.worker_id,
                'total_items_picked': worker.total_items_picked,
                'total_distance': worker.total_distance,
                'efficiency': worker.total_items_picked / max(1, worker.total_distance),
                'activity_count': len(worker.activity_log)
            }
            summary['worker_stats'].append(worker_stats)
        
        return summary
    
    def visualize_heatmap(self, figsize: Tuple[int, int] = (12, 10)):
        """
        倉庫内の活動ヒートマップを可視化
        
        Args:
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 基本的な倉庫レイアウトを描画
        for y in range(self.warehouse_map.height):
            for x in range(self.warehouse_map.width):
                cell_color = 'white'  # 通路
                if self.warehouse_map.grid[y, x] == 1:
                    cell_color = 'lightgray'  # 棚
                elif self.warehouse_map.grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                        edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # ヒートマップデータを準備
        heatmap_data = np.zeros((self.warehouse_map.height, self.warehouse_map.width))
        max_count = 1  # 0除算を避けるため最小値を1に
        
        for (x, y), count in self.stats['hotspots'].items():
            if 0 <= y < self.warehouse_map.height and 0 <= x < self.warehouse_map.width:
                heatmap_data[y, x] = count
                max_count = max(max_count, count)
        
        # ヒートマップの強度を正規化
        for y in range(self.warehouse_map.height):
            for x in range(self.warehouse_map.width):
                if self.warehouse_map.grid[y, x] != 1:  # 棚以外の場所のみ
                    intensity = heatmap_data[y, x] / max_count
                    if intensity > 0:
                        # 色の強度に応じて赤色を重ねる
                        rect = patches.Rectangle((x, y), 1, 1, linewidth=0, 
                                              facecolor=(1, 0, 0, intensity * 0.7))
                        ax.add_patch(rect)
        
        # 軸の設定
        ax.set_xlim(0, self.warehouse_map.width)
        ax.set_ylim(0, self.warehouse_map.height)
        ax.set_xticks(np.arange(0, self.warehouse_map.width+1, 1))
        ax.set_yticks(np.arange(0, self.warehouse_map.height+1, 1))
        ax.grid(True)
        ax.set_title('倉庫内活動ヒートマップ')
        ax.set_xlabel('X座標')
        ax.set_ylabel('Y座標')
        
        plt.tight_layout()
        return fig, ax
    
    def animate_workers(self, save_path: Optional[str] = None):
        """
        作業者の動きをアニメーション化
        
        Args:
            save_path: アニメーションを保存するパス（拡張子は.gifなど）
            
        Returns:
            アニメーションオブジェクト
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 倉庫レイアウトを描画
        for y in range(self.warehouse_map.height):
            for x in range(self.warehouse_map.width):
                cell_color = 'white'  # 通路
                if self.warehouse_map.grid[y, x] == 1:
                    cell_color = 'lightgray'  # 棚
                elif self.warehouse_map.grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                        edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # 作業者の位置を表す点
        worker_points = []
        for worker in self.workers:
            point, = ax.plot(worker.position[0] + 0.5, worker.position[1] + 0.5, 'o', 
                             markersize=10, color=f'C{worker.worker_id}')
            worker_points.append(point)
        
        # 情報テキスト
        info_text = ax.text(0.5, self.warehouse_map.height + 0.5, '', 
                           horizontalalignment='center', fontsize=12)
        
        # アニメーション更新関数
        def update(frame):
            # フレームごとに各作業者を移動
            for worker_idx, worker in enumerate(self.workers):
                history = worker.movement_history
                if frame < len(history):
                    _, x, y = history[frame]
                    worker_points[worker_idx].set_data(x + 0.5, y + 0.5)
                
            # 情報テキストを更新
            info_text.set_text(f'シミュレーション時間: {frame}秒')
            
            return worker_points + [info_text]
        
        # アニメーションを作成
        max_frames = max(len(worker.movement_history) for worker in self.workers) if self.workers else 0
        if max_frames > 0:
            ani = FuncAnimation(fig, update, frames=max_frames, interval=100, blit=True)
            
            # 軸の設定
            ax.set_xlim(0, self.warehouse_map.width)
            ax.set_ylim(0, self.warehouse_map.height + 1)
            ax.set_xticks(np.arange(0, self.warehouse_map.width+1, 1))
            ax.set_yticks(np.arange(0, self.warehouse_map.height+1, 1))
            ax.grid(True)
            ax.set_title('倉庫内作業者の動き')
            ax.set_xlabel('X座標')
            ax.set_ylabel('Y座標')
            
            # 凡例
            legend_elements = []
            for i, worker in enumerate(self.workers):
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                                markerfacecolor=f'C{worker.worker_id}', 
                                                markersize=10, label=f'作業者 {worker.worker_id}'))
            ax.legend(handles=legend_elements, loc='upper right')
            
            # 保存する場合
            if save_path:
                ani.save(save_path, writer='pillow', fps=10)
            
            plt.tight_layout()
            
            return ani
        else:
            plt.close(fig)
            return None
    
    def analyze_worker_efficiency(self) -> pd.DataFrame:
        """
        作業者の効率性を分析
        
        Returns:
            効率性データのDataFrame
        """
        efficiency_data = []
        
        for worker in self.workers:
            # 効率性指標を計算
            distance_per_item = worker.total_distance / max(1, worker.total_items_picked)
            items_per_second = worker.total_items_picked / max(1, self.current_time)
            
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
    
    def visualize_path_traces(self, figsize: Tuple[int, int] = (12, 10)):
        """
        全作業者の移動経路を可視化
        
        Args:
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 倉庫レイアウトを描画
        for y in range(self.warehouse_map.height):
            for x in range(self.warehouse_map.width):
                cell_color = 'white'  # 通路
                if self.warehouse_map.grid[y, x] == 1:
                    cell_color = 'lightgray'  # 棚
                elif self.warehouse_map.grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                        edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # 各作業者の移動経路を描画
        for worker in self.workers:
            # 移動履歴から座標のリストを抽出
            if not worker.movement_history:
                continue
                
            x_coords = [x + 0.5 for _, x, y in worker.movement_history]
            y_coords = [y + 0.5 for _, x, y in worker.movement_history]
            
            # 線を描画
            ax.plot(x_coords, y_coords, '-', linewidth=2, alpha=0.7, 
                   label=f'作業者 {worker.worker_id}')
            
            # 始点と終点をマーク
            ax.plot(x_coords[0], y_coords[0], 'o', markersize=8)
            ax.plot(x_coords[-1], y_coords[-1], 's', markersize=8)
        
        # 軸の設定
        ax.set_xlim(0, self.warehouse_map.width)
        ax.set_ylim(0, self.warehouse_map.height)
        ax.set_xticks(np.arange(0, self.warehouse_map.width+1, 1))
        ax.set_yticks(np.arange(0, self.warehouse_map.height+1, 1))
        ax.grid(True)
        ax.set_title('作業者の移動経路')
        ax.set_xlabel('X座標')
        ax.set_ylabel('Y座標')
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        return fig, ax