class StrategyNetwork:
    def __init__(self, input_size, output_size=141):  # 0〜140までの141通りの宣言値
        """
        deepCFRの戦略ネットワークを初期化
        
        Args:
            input_size: 入力特徴の次元数
            output_size: 出力（行動）の次元数
        """
        self.input_size = input_size
        self.output_size = output_size
        self.model = self._build_model()
        
    def _build_model(self):
        """ニューラルネットワークモデルを構築"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(self.input_size,)),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(self.output_size)  # 出力層はロジット（未正規化の確率）
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy']
        )
        return model
    
    def predict(self, state, legal_actions=None):
        """
        戦略ネットワークを使用して、各行動の確率分布を予測する
        
        Args:
            state: エンコードされたゲーム状態（np.array）
            legal_actions: 可能な行動のリスト（指定がない場合はすべての行動から選択）
        
        Returns:
            dict: 行動をキー、選択確率を値とする辞書
        """
        # バッチ次元を追加
        state_batch = np.expand_dims(state, axis=0)
        
        # ニューラルネットワークで予測
        logits = self.model(state_batch, training=False).numpy()[0]
        
        # 可能な行動のみに制限
        if legal_actions is not None:
            mask = np.ones_like(logits) * -1e9
            for action in legal_actions:
                if 0 <= action < len(mask):
                    mask[action] = 0
            logits = logits + mask
        
        # ソフトマックスで確率分布に変換
        probabilities = np.exp(logits) / np.sum(np.exp(logits))
        
        # 結果を辞書形式で返す
        action_probs = {}
        for i in range(len(probabilities)):
            if legal_actions is None or i in legal_actions:
                if probabilities[i] > 0:
                    action_probs[i] = float(probabilities[i])
        
        return action_probs
