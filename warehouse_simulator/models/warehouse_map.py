import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx
from typing import Dict, List, Tuple, Optional


class WarehouseMap:
    """
    倉庫のレイアウトと商品の配置を管理するクラス
    """
    
    def __init__(self, width: int = 20, height: int = 15):
        """
        倉庫マップを初期化
        
        Args:
            width: 倉庫の幅
            height: 倉庫の高さ
        """
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.storage_locations: Dict[int, Tuple[int, int]] = {}
        self.walkable_paths: List[Tuple[int, int]] = []
        self.picking_station: Tuple[int, int] = (0, 0)
        self.adjacency_list: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
        
        # 倉庫レイアウトの初期化
        self._initialize_layout()
    
    def _initialize_layout(self) -> None:
        """
        デフォルトの倉庫レイアウトを初期化する
        棚、通路、ピッキングステーションを配置
        """
        # まず全体を通路にする
        self.grid.fill(0)
        
        # 棚を配置する（縦方向の棚を何列か作成）
        for x in range(2, self.width-2, 3):
            for y in range(1, self.height-1):
                if y % 4 != 0:  # 4行おきに通路を空ける
                    self.grid[y, x] = 1  # 棚を設置
        
        # ピッキングステーションを設置（左下）
        self.picking_station = (1, self.height-2)
        self.grid[self.picking_station[1], self.picking_station[0]] = 2
        
        # 歩行可能な通路を記録
        self._update_walkable_paths()
        
        # 商品をランダムに配置（棚の位置に配置）
        product_id = 1
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == 1:  # 棚の位置
                    self.storage_locations[product_id] = (x, y)
                    product_id += 1
        
        # 経路探索用のグラフを構築
        self._build_navigation_graph()
    
    def _update_walkable_paths(self) -> None:
        """歩行可能な通路のリストを更新"""
        self.walkable_paths = []
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == 0 or self.grid[y, x] == 2:
                    self.walkable_paths.append((x, y))
    
    def _build_navigation_graph(self) -> None:
        """
        ナビゲーション用のグラフを構築
        歩行可能な場所間の接続関係を隣接リストとして表現
        """
        self.adjacency_list = {}
        
        # 歩行可能な各位置について
        for x, y in self.walkable_paths:
            neighbors = []
            # 上下左右の移動を確認
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                # マップ内かつ歩行可能な場所であれば
                if (0 <= nx < self.width and 0 <= ny < self.height and 
                    (self.grid[ny, nx] == 0 or self.grid[ny, nx] == 2)):
                    neighbors.append((nx, ny))
            
            self.adjacency_list[(x, y)] = neighbors
    
    def get_nearest_walkable(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        指定された位置から最も近い歩行可能な場所を取得
        
        Args:
            pos: 位置 (x, y)
            
        Returns:
            最も近い歩行可能な位置
        """
        x, y = pos
        # 同じ場所が歩行可能なら
        if (x, y) in self.walkable_paths:
            return (x, y)
        
        # 最も近い歩行可能な場所を探す
        min_dist = float('inf')
        nearest_pos = None
        
        for wx, wy in self.walkable_paths:
            dist = abs(wx - x) + abs(wy - y)  # マンハッタン距離
            if dist < min_dist:
                min_dist = dist
                nearest_pos = (wx, wy)
        
        return nearest_pos
    
    def find_shortest_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        A*アルゴリズムで最短経路を探索
        
        Args:
            start: 開始位置 (x, y)
            end: 終了位置 (x, y)
            
        Returns:
            最短経路の位置リスト [(x1, y1), (x2, y2), ...]
        """
        # NetworkXを使用してA*最短経路を計算
        graph = nx.Graph()
        
        # ノードとエッジを追加
        for node, neighbors in self.adjacency_list.items():
            for neighbor in neighbors:
                graph.add_edge(node, neighbor, weight=1)
        
        # 歩行可能な位置に変換
        start_walkable = self.get_nearest_walkable(start)
        end_walkable = self.get_nearest_walkable(end)
        
        # 経路が存在するか確認
        if not nx.has_path(graph, start_walkable, end_walkable):
            return []
        
        # A*でパスを計算（ヒューリスティックはマンハッタン距離）
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        try:
            path = nx.astar_path(graph, start_walkable, end_walkable, 
                                heuristic=heuristic, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return []
    
    def plot(self, figsize: Tuple[int, int] = (10, 8)):
        """
        倉庫マップを可視化
        
        Args:
            figsize: 図のサイズ
            
        Returns:
            図とaxesオブジェクト
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # グリッドを描画
        for y in range(self.height):
            for x in range(self.width):
                cell_color = 'white'  # 通路
                if self.grid[y, x] == 1:
                    cell_color = 'gray'  # 棚
                elif self.grid[y, x] == 2:
                    cell_color = 'green'  # ピッキングステーション
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                        edgecolor='black', facecolor=cell_color)
                ax.add_patch(rect)
        
        # 軸の設定
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.set_xticks(np.arange(0, self.width+1, 1))
        ax.set_yticks(np.arange(0, self.height+1, 1))
        ax.grid(True)
        ax.set_title('倉庫レイアウト')
        ax.set_xlabel('X座標')
        ax.set_ylabel('Y座標')
        
        # ピッキングステーションを明示
        ax.text(self.picking_station[0] + 0.5, self.picking_station[1] + 0.5, 'P', 
                ha='center', va='center', fontsize=12, color='black')
        
        # いくつかの商品の位置を表示
        shown_products = list(self.storage_locations.items())[:5]
        for product_id, (x, y) in shown_products:
            ax.text(x + 0.5, y + 0.5, f'#{product_id}', 
                    ha='center', va='center', fontsize=8, color='black')
        
        plt.tight_layout()
        return fig, ax
