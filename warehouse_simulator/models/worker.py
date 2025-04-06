import time
from typing import Dict, List, Tuple, Optional, Any

from warehouse_simulator.models.warehouse_map import WarehouseMap
from warehouse_simulator.models.order import Order


class WarehouseWorker:
    """
    倉庫内の作業者を表すクラス
    """
    
    def __init__(self, worker_id: int, warehouse_map: WarehouseMap, start_pos: Optional[Tuple[int, int]] = None):
        """
        作業者を初期化
        
        Args:
            worker_id: 作業者ID
            warehouse_map: 倉庫マップ
            start_pos: 開始位置 (指定がない場合はピッキングステーション)
        """
        self.worker_id = worker_id
        self.warehouse_map = warehouse_map
        
        # 開始位置（指定がない場合はピッキングステーション）
        if start_pos is None:
            self.position = warehouse_map.picking_station
        else:
            self.position = start_pos
        
        # 作業者の状態を管理
        self.current_order: Optional[Order] = None
        self.path: List[Tuple[int, int]] = []
        self.path_index: int = 0
        self.picked_items: List[int] = []
        self.is_busy: bool = False
        self.movement_speed: float = 1.0
        
        # 統計情報
        self.total_distance: float = 0.0
        self.total_items_picked: int = 0
        self.start_time: Optional[float] = None
        self.movement_history: List[Tuple[float, int, int]] = []
        self.activity_log: List[Tuple[float, str]] = []
    
    def assign_order(self, order: Order) -> None:
        """
        オーダーを割り当てる
        
        Args:
            order: 割り当てるオーダー
        """
        self.current_order = order
        self.is_busy = True
        self.start_time = time.time()
        
        # オーダーに作業者情報を設定
        order.assigned_worker = self.worker_id
        
        # 活動ログに記録
        self.activity_log.append((time.time(), f"オーダー {order.order_id} を受け取りました。商品数: {len(order.items)}"))
        
        # 最初の商品へのパスを計画
        self._plan_path_to_next_item()
    
    def _plan_path_to_next_item(self) -> None:
        """次の商品へのパスを計画"""
        if not self.current_order or not self.current_order.items:
            # 全ての商品を取得したらピッキングステーションに戻る
            self.path = self.warehouse_map.find_shortest_path(
                self.position, self.warehouse_map.picking_station)
            self.activity_log.append((time.time(), "全商品のピック完了。ピッキングステーションに戻ります。"))
        else:
            # 次の商品の位置を取得
            next_item = self.current_order.items[0]
            item_location = self.warehouse_map.storage_locations.get(next_item)
            
            if item_location:
                # 商品への経路を探索
                self.path = self.warehouse_map.find_shortest_path(self.position, item_location)
                self.activity_log.append((time.time(), f"商品 {next_item} への経路を計画しました。"))
            else:
                # 商品が見つからない場合
                self.activity_log.append((time.time(), f"商品 {next_item} の位置が見つかりません。"))
                # 次の商品に進む
                self.current_order.items.pop(0)
                self._plan_path_to_next_item()
                return
        
        self.path_index = 0
    
    def move(self, current_time: float) -> bool:
        """
        作業者を移動させる
        
        Args:
            current_time: 現在の時間
            
        Returns:
            移動が成功したかどうか
        """
        if not self.is_busy or not self.path or self.path_index >= len(self.path):
            return False
        
        # 次の位置に移動
        next_position = self.path[self.path_index]
        
        # 現在位置と次の位置の距離
        distance = abs(next_position[0] - self.position[0]) + abs(next_position[1] - self.position[1])
        self.total_distance += distance
        
        # 位置を更新
        self.position = next_position
        self.path_index += 1
        
        # 移動履歴に記録
        self.movement_history.append((current_time, self.position[0], self.position[1]))
        
        # パスの終点に到達したら
        if self.path_index >= len(self.path):
            # 商品のピックアップまたは納品が完了したことを確認
            if self.current_order and self.current_order.items:
                # 商品をピックアップ
                item = self.current_order.items.pop(0)
                self.picked_items.append(item)
                self.total_items_picked += 1
                self.activity_log.append((current_time, f"商品 {item} をピックしました。"))
                
                # 次の商品へのパスを計画
                self._plan_path_to_next_item()
            elif self.position == self.warehouse_map.picking_station:
                # ピッキングステーションに戻ってきたらオーダー完了
                if self.current_order:
                    order = self.current_order
                    self.activity_log.append((current_time, f"オーダー {order.order_id} を完了しました。"))
                    order.mark_as_completed(current_time)
                    self.current_order = None
                    self.is_busy = False
                    self.picked_items = []
        
        return True
    
    def get_current_info(self) -> Dict[str, Any]:
        """
        現在の作業者情報を取得
        
        Returns:
            作業者の現在の状態情報
        """
        return {
            'worker_id': self.worker_id,
            'position': self.position,
            'is_busy': self.is_busy,
            'current_order': self.current_order.order_id if self.current_order else None,
            'picked_items': len(self.picked_items),
            'remaining_items': len(self.current_order.items) if self.current_order else 0,
            'total_distance': self.total_distance,
            'total_items_picked': self.total_items_picked
        }
