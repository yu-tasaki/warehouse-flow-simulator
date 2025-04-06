import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Optional, Any

from warehouse_simulator.models.warehouse_map import WarehouseMap

if 'font.family' not in matplotlib.rcParams or matplotlib.rcParams['font.family'] == 'sans-serif':
    matplotlib.rcParams['font.family'] = 'MS Gothic'  # Windows用
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42


class HotspotAnalyzer:
    """
    倉庫内のホットスポット（混雑箇所）を分析するクラス
    """
    
    @staticmethod
    def analyze_hotspots(hotspot_data: Dict[Tuple[int, int], int]) -> pd.DataFrame:
        """
        倉庫内のホットスポットを分析
        
        Args:
            hotspot_data: 位置ごとの訪問回数 {(x, y): count}
            
        Returns:
            ホットスポットデータのDataFrame
        """
        # ホットスポットデータを準備
        hotspot_list = []
        
        for (x, y), count in hotspot_data.items():
            hotspot_list.append({
                'x': x,
                'y': y,
                'visit_count': count
            })
        
        # データフレームに変換
        df = pd.DataFrame(hotspot_list)
        
        # 訪問回数順に並べ替え
        if not df.empty:
            df = df.sort_values('visit_count', ascending=False)
        
        return df
    
    @staticmethod
    def visualize_heatmap(hotspot_data: Dict[Tuple[int, int], int], warehouse_map: WarehouseMap, 
                          figsize: Tuple[int, int] = (12, 10)):
        """
        倉庫内の活動ヒートマップを可視化
        
        Args:
            hotspot_data: 位置ごとの訪問回数 {(x, y): count}
            warehouse_map: 倉庫マップ
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # 基本的な倉庫レイアウトを描画
        for y in range(warehouse_map.height):
            for x in range(warehouse_map.width):
                cell_color = 'white'  # 通路
                if warehouse_map.grid[y, x] == 1:
                    cell_color = 'lightgray'  # 棚
                elif warehouse_map.grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                        edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # ヒートマップデータを準備
        heatmap_data = np.zeros((warehouse_map.height, warehouse_map.width))
        max_count = 1  # 0除算を避けるため最小値を1に
        
        for (x, y), count in hotspot_data.items():
            if 0 <= y < warehouse_map.height and 0 <= x < warehouse_map.width:
                heatmap_data[y, x] = count
                max_count = max(max_count, count)
        
        # ヒートマップの強度を正規化
        for y in range(warehouse_map.height):
            for x in range(warehouse_map.width):
                if warehouse_map.grid[y, x] != 1:  # 棚以外の場所のみ
                    intensity = heatmap_data[y, x] / max_count
                    if intensity > 0:
                        # 色の強度に応じて赤色を重ねる
                        rect = patches.Rectangle((x, y), 1, 1, linewidth=0, 
                                              facecolor=(1, 0, 0, intensity * 0.7))
                        ax.add_patch(rect)
        
        # 軸の設定
        ax.set_xlim(0, warehouse_map.width)
        ax.set_ylim(0, warehouse_map.height)
        ax.set_xticks(np.arange(0, warehouse_map.width+1, 1))
        ax.set_yticks(np.arange(0, warehouse_map.height+1, 1))
        ax.grid(True)
        ax.set_title('倉庫内活動ヒートマップ')
        ax.set_xlabel('X座標')
        ax.set_ylabel('Y座標')
        
        plt.tight_layout()
        return fig, ax
