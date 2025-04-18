import numpy as np
import json
from typing import Dict, List, Union, Any

# jsonファイルを文字列として読み込む関数
# 辞書のリストを返す
def load_game_states_from_json(json_file_path: str) -> List[Dict[str, Any]]:
    """
    JSONファイルからゲーム状態のリストを読み込む
    
    Args:
        json_file_path: ゲーム状態を含むJSONファイルのパス
    
    Returns:
        List[Dict]: ゲーム状態のリスト
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            game_logs = json.load(f)
        
        print(f"Successfully loaded {len(game_logs)} game states from {json_file_path}")
        return game_logs
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []

def encode_state(state: Union[Dict[str, Any], str]) -> np.ndarray:
    """
    ゲーム状態をdeepCFRのニューラルネットワーク入力形式に変換
    
    Args:
        state: ゲーム状態（辞書形式またはJSONファイルパス）
            - others_info: 他プレイヤーの情報
            - sum: 他プレイヤーのカード合計
            - log: ゲームログ情報
            - legal_action: 可能な行動リスト
    
    Returns:
        np.array: エンコードされた状態ベクトル
    """
    # 文字列の場合はJSONファイルとして読み込む
    if isinstance(state, str):
        state_data = load_game_states_from_json(state)
        if not state_data:
            raise ValueError(f"Could not load game state from {state}")
        # 最初の状態を使用
        state = state_data[0]["state"] if "state" in state_data[0] else state_data[0]
    
    # 辞書からキーを取得
    others_info = state.get("others_info", [])
    sum_val = state.get("sum", 0)
    log_info = state.get("log", {"round_count": 0, "turn_info": [], "player_info": []})
    legal_action = state.get("legal_action", [])
    
    # 1. 他プレイヤー情報のエンコード
    player_features = []
    for player in others_info:
        # 特殊カード番号（100-103）を含めたエンコーディング
        card_value = player.get("card_info", 0)
        
        # カード値のone-hotエンコーディング（-10から20までの通常カードと特殊カード）
        # 通常カードの値: -10, -5, 0, 1, 2, 3, 4, 5, 10, 15, 20
        # 特殊カード値: 100(×2), 101(max→0), 102(?), 103(黒背景0)
        card_values = [-10, -5, 0, 1, 2, 3, 4, 5, 10, 15, 20, 100, 101, 102, 103]
        card_encoding = [0] * len(card_values)
        
        if card_value in card_values:
            card_idx = card_values.index(card_value)
            card_encoding[card_idx] = 1
        
        # プレイヤーの位置関係（次のプレイヤーか前のプレイヤーか）
        position_encoding = [
            1 if player.get("is_next", False) else 0,
            1 if player.get("is_prev", False) else 0
        ]
        
        # ライフ情報（正規化）
        life_normalized = player.get("life", 0) / 3  # 一般的な最大ライフ
        
        # このプレイヤーの特徴をまとめる
        player_features.extend(card_encoding + position_encoding + [life_normalized])
    
    # プレイヤー数が変わる可能性があるため、常に5人分の情報を確保（6人対戦で自分を除く）
    # 足りない場合は0パディング
    max_players = 5
    padding_size = max_players * (len(card_values) + 2 + 1) - len(player_features)
    if padding_size > 0:
        player_features.extend([0] * padding_size)
    
    # 2. 合計値の正規化
    theoretical_max_sum = 140  # 適切な値に調整（ゲーム状況による）
    sum_normalized = sum_val / theoretical_max_sum
    
    # 3. ゲームログの処理
    # ラウンド数の正規化
    round_normalized = log_info.get("round_count", 0) / 10  # 想定最大ラウンド数で正規化
    
    # ターン情報のエンコード（最新の10ターン分）
    max_turns = 10
    turn_features = []
    
    recent_turns = log_info.get("turn_info", [])[-max_turns:] if "turn_info" in log_info else []
    for turn in recent_turns:
        # プレイヤー名をIDに変換（簡易的な実装）
        player_names = [p.get("name", "") for p in log_info.get("player_info", [])]
        player_id = player_names.index(turn.get("turn_player", "")) if turn.get("turn_player", "") in player_names else 0
        
        # プレイヤーIDをone-hot
        player_one_hot = [0] * 6  # 6人プレイヤー
        if 0 <= player_id < 6:
            player_one_hot[player_id] = 1
        
        # 宣言値の正規化
        declared_value = turn.get("declared_value", 0) / 140  # 想定最大宣言値
        
        turn_features.extend(player_one_hot + [declared_value])
    
    # 履歴が足りない場合はパディング
    padding_size = max_turns * 7 - len(turn_features)  # 7 = 6(プレイヤーID) + 1(宣言値)
    if padding_size > 0:
        turn_features.extend([0] * padding_size)
    
    # 4. 可能なアクション（legal_action）のマスク
    max_action_value = 140  # 想定される最大宣言値
    action_mask = [0] * (max_action_value + 1)
    
    for action in legal_action:
        if 0 <= action <= max_action_value:
            action_mask[action] = 1
    
    # すべての特徴を連結
    features = player_features + [sum_normalized, round_normalized] + turn_features + action_mask
    
    return np.array(features, dtype=np.float32)

def encode_batch_from_json(json_file_path: str) -> np.ndarray:
    """
    JSONファイルから複数のゲーム状態を読み込んでバッチエンコードする
    
    Args:
        json_file_path: ゲーム状態を含むJSONファイルのパス
        
    Returns:
        np.ndarray: エンコードされた状態のバッチ
    """
    game_states = load_game_states_from_json(json_file_path)
    
    # 各状態をエンコード
    encoded_states = []
    for log_entry in game_states:
        # logエントリから状態を取得
        state = log_entry.get("state", log_entry)
        encoded_state = encode_state(state)
        encoded_states.append(encoded_state)
    
    return np.array(encoded_states)

def save_game_states_to_json(game_states: List[Dict[str, Any]], output_file: str) -> None:
    """
    ゲーム状態のリストをJSONファイルに保存
    
    Args:
        game_states: 保存するゲーム状態のリスト
        output_file: 出力JSONファイルのパス
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(game_states, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved {len(game_states)} game states to {output_file}")
    except Exception as e:
        print(f"Error saving game states to JSON: {e}")

# 使用例
if __name__ == "__main__":
    # JSONファイルからゲーム状態を読み込む例
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        print(f"Encoding game states from {json_file}")
        
        # 単一状態のエンコード
        try:
            encoded_state = encode_state(json_file)
            print(f"Encoded state shape: {encoded_state.shape}")
            print(f"First 10 values: {encoded_state[:10]}")
        except Exception as e:
            print(f"Error encoding single state: {e}")
        
        # バッチエンコードの例
        try:
            encoded_batch = encode_batch_from_json(json_file)
            print(f"Encoded batch shape: {encoded_batch.shape}")
        except Exception as e:
            print(f"Error encoding batch: {e}")
    else:
        print("Usage: python encode_state.py <json_file_path>")
        
        # テスト用のサンプルゲーム状態
        sample_state = {
            "others_info": [
                {"card_info": 5, "is_next": True, "is_prev": False, "life": 3},
                {"card_info": 10, "is_next": False, "is_prev": True, "life": 2}
            ],
            "sum": 30,
            "log": {
                "round_count": 2,
                "turn_info": [
                    {"turn_player": "Player1", "declared_value": 25},
                    {"turn_player": "Player2", "declared_value": 30}
                ],
                "player_info": [
                    {"name": "Player1"},
                    {"name": "Player2"},
                    {"name": "Player3"}
                ]
            },
            "legal_action": [31, 32, 33, 34, 35]
        }
        
        # サンプル状態のエンコード
        encoded = encode_state(sample_state)
        print(f"Sample state encoded shape: {encoded.shape}")
        
        # サンプルをJSONに保存
        save_game_states_to_json([{"state": sample_state, "action": 31, "player_id": 0}], "sample_game_state.json")
        print("Saved sample game state to sample_game_state.json")