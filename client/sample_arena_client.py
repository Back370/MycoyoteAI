from .not_websocket_client import Client
from .train_deepcfr_for_coyote import train_deepcfr_for_coyote
from .make_decision import make_decision
import random

class SampleClient(Client):
    def AI_player_action(self,others_info, player_card, sum, log, actions, round_num):
        # カスタムロジックを実装
        print(f"[SampleClient] AI deciding action based on sum: {sum}, player_card {player_card} log: {log}, actions: {actions},others_info: {others_info}, round_num: {round_num}" )
        # 例: ランダムにアクションを選択
        action = random.choice(actions)
        print(f"[SampleClient] AI selected action: {action}")
        state = {
            "others_info": others_info,
            "player_card": player_card,
            "sum": sum,
            "legal_action": actions,
            "log": log  # 既存のlog情報を使用
        }
        strategy_nets = train_deepcfr_for_coyote(iterations=1000, current_state = state)

        select_action = make_decision(state, strategy_nets)
        RED = '\033[31m'
        END = '\033[0m'
        print(RED  + str(select_action) +  END)
        return  select_action
        return action