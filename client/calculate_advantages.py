from collections import defaultdict
from encode_state import encode_state
import numpy as np
def calculate_advantages(state, advantage_net):
    """
    Calculate counterfactual advantages for each player's decisions

    Args:
        game_states: List of game states from simulation
        advantage_nets: List of advantage networks for each player
        num_players: Number of players

    Returns:
        dict: Advantages for each player's information sets
    """
    #キーがない場合そのキーを作成する
    advantages = defaultdict(list)

    # Process game trajectory in reverse to calculate counterfactual values
    trajectory_value = 0  # Final game value

    #for state_info in reversed(game_states):

    # game_statesから必要な情報を抽出
    #state = state_info  # state_infoはgame_stateと同じ形式
    # current_playerからplayer番号を抽出
    # player_names = [p.get("name", "") for p in state["log"].get("player_info", [])]  # Use .get to handle potential missing keys
    # player_names = [p.get("name", "") for p in state.get("log", {}).get("player_info", [])]
    # player = player_names.index(state.get("current_player", "")) if state.get("current_player", "") in player_names else 0
    # action_taken = state.get("log", {}).get("turn_info", [])[-1].get("declared_value") if state.get("log", {}).get("turn_info", []) else None
    # print(f"player: {player}, action_taken: {action_taken}")
    player_names = [state["others_info"]]
    current_player_name = state.get("current_player", "")
    try:
        player = player_names.index(current_player_name)
    except ValueError:
        player = 0  # Default to 0 if not found
    if state["log"]:  # Check if log is not empty
        action_taken = state["log"][-1].get("action", -1)  # Get action from the last turn
    else:
        action_taken = -1  # Default to -1 if log is empty

    # Printing the Information
    print(f"player: {player}, action_taken: {action_taken}")


    # Encode state for network input
    encoded_state = encode_state(state)

    # Get current strategy's action values
    action_values = advantage_net[player](np.expand_dims(encoded_state, axis=0)).numpy()[0]

    # Calculate advantages (counterfactual regret)
    # In a real implementation, you would calculate the actual counterfactual values
    # by considering alternative actions' outcomes
    legal_actions = state["legal_action"]

    # For each legal action, estimate its advantage
    for action in legal_actions:
        # This is a simplified advantage calculation
        # In real CFR, you would compute the true counterfactual value
        if action == action_taken:
            advantage = trajectory_value - action_values[action]
        else:
            # Estimate counterfactual value for actions not taken
            # This is a simplified approach; real CFR would simulate alternative outcomes
            advantage = -action_values[action]

        # Store advantage for this information set and action
        info_set_key = f"player{player}_state{hash(str(encoded_state.tobytes()))}"
        advantages[info_set_key].append((action, advantage, encoded_state))

    return advantages