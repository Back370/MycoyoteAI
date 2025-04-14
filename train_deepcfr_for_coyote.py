def train_deepcfr_for_coyote(iterations=1000):
    """deepCFRアルゴリズムでコヨーテ戦略を学習"""
    advantage_net = create_advantage_network()
    strategy_net = create_strategy_network()
    
    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}")
        
        # 外部サンプリングでゲームをシミュレーション
        game_states = sample_game_states()
        
        # 各情報集合での後悔値を計算
        for state in game_states:
            calculate_advantages(state, advantage_net)
        
        # アドバンテージネットワークを更新
        update_advantage_network(advantage_net, game_states)
        
        # 定期的に戦略ネットワークを更新
        if i % 10 == 0:
            update_strategy_network(strategy_net, advantage_net)
    
    return strategy_net