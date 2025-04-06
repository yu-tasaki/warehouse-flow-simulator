import time
from typing import List, Optional


class Order:
    """
    倉庫のオーダーを表すクラス
    """
    
    def __init__(self, order_id: int, items: Optional[List[int]] = None, priority: int = 1):
        """
        オーダーを初期化
        
        Args:
            order_id: オーダーID
            items: 商品IDのリスト（指定がない場合は空リスト）
            priority: 優先度（1が最高）
        """
        self.order_id = order_id
        self.items = items if items is not None else []
        self.priority = priority
        self.created_time = time.time()
        self.completed_time: Optional[float] = None
        self.assigned_worker: Optional[int] = None
    
    def add_item(self, item_id: int) -> None:
        """
        オーダーに商品を追加
        
        Args:
            item_id: 追加する商品のID
        """
        self.items.append(item_id)
    
    def is_completed(self) -> bool:
        """
        オーダーが完了したかどうかを確認
        
        Returns:
            完了している場合はTrue
        """
        return len(self.items) == 0 and self.completed_time is not None
    
    def mark_as_completed(self, completion_time: float) -> None:
        """
        オーダーを完了としてマーク
        
        Args:
            completion_time: 完了時間
        """
        self.completed_time = completion_time
    
    def get_processing_time(self) -> float:
        """
        オーダーの処理時間を取得
        
        Returns:
            処理時間（秒）。未完了の場合は現在までの時間
        """
        current_time = time.time()
        if self.completed_time:
            # 完了時間が設定されている場合のみ計算
            return max(0, self.completed_time - self.created_time)  # 負の値を防止
        # 未完了の場合は現在までの経過時間
        return max(0, current_time - self.created_time)  # 負の値を防止
    
    def __str__(self) -> str:
        """オーダーの文字列表現"""
        status = "完了" if self.is_completed() else "処理中" if self.assigned_worker else "未割当"
        return (f"オーダー #{self.order_id}: 状態={status}, "
                f"商品数={len(self.items)}, 優先度={self.priority}")
