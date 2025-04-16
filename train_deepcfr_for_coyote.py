def train_deepcfr_for_coyote(iterations=1000):
    """
    Train Deep CFR for Coyote game
    
    Args:
        iterations: Number of training iterations
        num_players: Number of players in the game
        
    Returns:
        list: Trained strategy networks for each player
    """
    # Create networks for each player
    advantage_nets = [create_advantage_network() for _ in range(num_players)]
    strategy_nets = [StrategyNetwork(1000, 141) for _ in range(num_players)]
    
    # Create reservoir buffers for each player
    advantage_buffers = [ReservoirBuffer() for _ in range(num_players)]
    strategy_buffer = ReservoirBuffer()
    
    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        
        # Simulate games using current strategy
        game_states = simulate_coyote_game(strategy_nets, num_players)
        
        # Calculate advantages for all players
        advantages = calculate_advantages(game_states, advantage_nets, num_players)
        
        # Update advantage networks for each player
        for player in range(num_players):
            update_advantage_network(
                advantage_nets[player], 
                advantages, 
                player, 
                advantage_buffers[player]
            )
        
        # Periodically update strategy networks
        if i % 10 == 0:
            for player in range(num_players):
                update_strategy_network(
                    strategy_nets[player],
                    advantage_nets[player],
                    advantage_buffers[player]
                )
            
            # Save models
            for player in range(num_players):
                strategy_nets[player].model.save(f"models/coyote_strategy_player{player}")
    
    return strategy_nets