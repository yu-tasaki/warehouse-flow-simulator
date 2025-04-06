import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple, Any

from warehouse_simulator.models.worker import WarehouseWorker


class MovementAnalyzer:
    """
    作業者の移動パターンを分析するクラス
    """
    
    @staticmethod
    def analyze_travel_patterns(workers: List[WarehouseWorker]) -> pd.DataFrame:
        """
        移動パターンを分析
        
        Args:
            workers: 分析対象の作業者リスト
            
        Returns:
            移動パターン分析のDataFrame
        """
        # 作業者ごとの移動パターンを抽出
        patterns = []
        
        for worker in workers:
            # 移動の連続性を分析
            if len(worker.movement_history) < 2:
                continue
                
            for i in range(1, len(worker.movement_history)):
                prev_time, prev_x, prev_y = worker.movement_history[i-1]
                curr_time, curr_x, curr_y = worker.movement_history[i]
                
                # 移動方向を特定
                dx, dy = curr_x - prev_x, curr_y - prev_y
                
                if dx == 1 and dy == 0:
                    direction = '右'
                elif dx == -1 and dy == 0:
                    direction = '左'
                elif dx == 0 and dy == 1:
                    direction = '上'
                elif dx == 0 and dy == -1:
                    direction = '下'
                else:
                    direction = '停止'
                
                # 移動シーケンスを記録
                patterns.append({
                    'worker_id': worker.worker_id,
                    'timestamp': curr_time,
                    'from_x': prev_x,
                    'from_y': prev_y,
                    'to_x': curr_x,
                    'to_y': curr_y,
                    'direction': direction,
                    'travel_time': curr_time - prev_time
                })
        
        return pd.DataFrame(patterns)
    
    @staticmethod
    def identify_congestion_points(workers: List[WarehouseWorker], threshold: int = 2) -> pd.DataFrame:
        """
        混雑ポイントを特定（複数の作業者が同時に同じ場所にいた回数）
        
        Args:
            workers: 分析対象の作業者リスト
            threshold: 混雑とみなす最低作業者数
            
        Returns:
            混雑ポイント分析のDataFrame
        """
        # 時間帯ごとの位置データを集約
        time_location_map: Dict[int, List[Tuple[int, Tuple[int, int]]]] = {}
        
        for worker in workers:
            for time_point, x, y in worker.movement_history:
                # 時間を整数に切り捨て（近い時間をグループ化）
                t = int(time_point)
                if t not in time_location_map:
                    time_location_map[t] = []
                time_location_map[t].append((worker.worker_id, (x, y)))
        
        # 混雑ポイントを特定
        congestion_points: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        
        for t, locations in time_location_map.items():
            # 位置ごとの作業者数をカウント
            location_counts: Dict[Tuple[int, int], int] = {}
            for _, pos in locations:
                location_counts[pos] = location_counts.get(pos, 0) + 1
            
            # しきい値以上の作業者がいる場所を記録
            for pos, count in location_counts.items():
                if count >= threshold:
                    if pos not in congestion_points:
                        congestion_points[pos] = []
                    congestion_points[pos].append((t, count))
        
        # 結果をデータフレームに変換
        congestion_data = []
        for (x, y), occurrences in congestion_points.items():
            for time_point, count in occurrences:
                congestion_data.append({
                    'x': x,
                    'y': y,
                    'timestamp': time_point,
                    'worker_count': count
                })
        
        return pd.DataFrame(congestion_data)
    
    @staticmethod
    def export_movement_data(workers: List[WarehouseWorker], 
                           filename: str = 'worker_movements.csv') -> pd.DataFrame:
        """
        作業者の移動データをCSVファイルにエクスポート
        
        Args:
            workers: 作業者リスト
            filename: 出力ファイル名
            
        Returns:
            移動データのDataFrame
        """
        all_movements = []
        
        for worker in workers:
            for time_point, x, y in worker.movement_history:
                all_movements.append({
                    'worker_id': worker.worker_id,
                    'timestamp': time_point,
                    'x': x,
                    'y': y
                })
        
        # リストをデータフレームに変換
        df = pd.DataFrame(all_movements)
        
        # 時間順にソート
        if not df.empty:
            df = df.sort_values('timestamp')
        
        # CSVに保存
        df.to_csv(filename, index=False)
        print(f"移動データを {filename} に保存しました")
        
        return df
    
    @staticmethod
    def export_activity_log(workers: List[WarehouseWorker], 
                          filename: str = 'activity_log.csv') -> pd.DataFrame:
        """
        活動ログをCSVファイルにエクスポート
        
        Args:
            workers: 作業者リスト
            filename: 出力ファイル名
            
        Returns:
            活動ログのDataFrame
        """
        all_activities = []
        
        for worker in workers:
            for time_point, activity in worker.activity_log:
                all_activities.append({
                    'worker_id': worker.worker_id,
                    'timestamp': time_point,
                    'activity': activity
                })
        
        # リストをデータフレームに変換
        df = pd.DataFrame(all_activities)
        
        # 時間順にソート
        if not df.empty:
            df = df.sort_values('timestamp')
        
        # CSVに保存
        df.to_csv(filename, index=False)
        print(f"活動ログを {filename} に保存しました")
        
        return df
    
    @staticmethod
    def visualize_path_traces(workers: List[WarehouseWorker], warehouse_grid: np.ndarray, 
                              figsize: Tuple[int, int] = (12, 10)):
        """
        作業者の移動経路を可視化
        
        Args:
            workers: 作業者リスト
            warehouse_grid: 倉庫グリッド
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 倉庫レイアウトを描画
        height, width = warehouse_grid.shape
        for y in range(height):
            for x in range(width):
                cell_color = 'white'  # 通路
                if warehouse_grid[y, x] == 1:
                    cell_color = 'lightgray'  # 棚
                elif warehouse_grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = plt.Rectangle((x, y), 1, 1, linewidth=1, 
                                     edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # 各作業者の移動経路を描画
        for worker in workers:
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
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        ax.set_xticks(np.arange(0, width+1, 1))
        ax.set_yticks(np.arange(0, height+1, 1))
        ax.grid(True)
        ax.set_title('作業者の移動経路')
        ax.set_xlabel('X座標')
        ax.set_ylabel('Y座標')
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        return fig, ax