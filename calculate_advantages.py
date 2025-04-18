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
    advantages = defaultdict(list)
    
    # Process game trajectory in reverse to calculate counterfactual values
    trajectory_value = 0  # Final game value
    
    for state_info in reversed(game_states):
        state = state_info["state"]
        action_taken = state_info["action"]
        player = state_info["player"]
        
        # Encode state for network input
        encoded_state = es.encode_state(state)
        
        # Get current strategy's action values
        action_values = advantage_nets[player](np.expand_dims(encoded_state, axis=0)).numpy()[0]
        
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