from server.arena import Arena
from client.sample_arena_client import SampleClient as SampleClient
from client.not_websocket_client import Client
import random

class Deck:
    def __init__(self):
        #初期条件
        #?→ max→0→×2:103,102,101,100に対応
        self.cards = [-10, -5, -5, 0, 0, 0,
                      1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
                      4, 4, 4, 4, 5, 5, 5, 5,
                      10, 10, 10, 15, 15, 20,
                      100, 101, 102, 103]

        #self.cashed_cards = [] #山札に戻すカードを格納するリスト

    def shuffle(self):
        print ("Deck shuffled.")
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            print("No card left in the deck.")
            #random.shuffle(self.cashed_cards) #山札に戻すカードをシャッフルする
            #山札が空になったら、捨て札を山札に追加する
           # self.cards = self.cashed_cards.copy()
           # self.cashed_cards = []
            self.reset()
            return self.cards.pop()

    def top_show_card(self):
        if len(self.cards) > 0:
            return self.cards[-1]
        return None

    def reset(self):
        self.cards = [-10, -5, -5, 0, 0, 0,
                      1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
                      4, 4, 4, 4, 5, 5, 5, 5,
                      10, 10, 10, 15, 15, 20,
                      100, 101, 102, 103]
        self.shuffle()


class SampleClient(Client):
    def __init__(self, player_name=None, is_ai=False):
        super().__init__(player_name, is_ai)
        self.mycard = None
        self.others_expect_sum = 0
        self.expect_cards = []
        self.deck = Deck()
        self.players_life = {} #{"player_name": life}
        self.previous_round_num = -1
        self.expect_sum = 0
        self.is_double_card = False #二倍するかどうか
        self.is_shuffle_card = True

    #場のカードの合計値を計算する
    def calc_card_sum(self, true_cards):
        card_sum = 0 #初期化
        for card in true_cards:
            card_sum += card
        if(self.is_double_card):
            card_sum *= 2
            self.is_double_card = False
        print(f"gamesum is {card_sum}")
        return card_sum
    def convert_card(self, cards, Is_othersum, deck):
        print (f"cards: {cards}")
        true_cards = sorted(cards, reverse = True)
        index = 0
        print(f"Initial true_cards: {true_cards}")
        while index < len(true_cards):
            card = true_cards[index]
            print(f"Card drawn: {card}")

            #?を引いたら次のカードを引き、出た番号のカードと交換する
            #全体の数の計算はラウンドにつき一回

            if(card == 103):
                if Is_othersum:
                    new_card = 0  #他プレイヤーの合計値を計算する場合
                else :
                    new_card = deck.draw()
                    #deck.cashed_cards.append(103) #103を山札に戻す
                #print(f"Drawn new card: {deck.cashed_cards}")
                print(f"Drawn new card: {new_card}")
                if new_card != None: #103を引いた時にNoneがcardsに含まれていたから
                   true_cards[index] = new_card
                   true_cards = sorted(true_cards,reverse=True)
                   #もし特殊カードを引いてしまったら処理をもう一度行う
                   continue
                else:
                    self.deck.reset()
                    print("No card left in the deck.")
                    continue

            #maxを引いたら、最も大きいカードを0にする
            elif(card == 102):
                normal_cards = [c for c in true_cards if c < 100] #通常カードを取得
                if len(normal_cards) != 0:
                    max_card = max(c for c in true_cards if c < 100) #最大値を取得
                    max_index = true_cards.index(max_card) #最大値のインデックスを取得
                    true_cards[max_index] = 0 #最大値を0にする
                true_cards[true_cards.index(102)] = 0

            #0(黒背景)を引いたら、ラウンド終了後山札をリセットする
            elif(card == 101):
                true_cards[index] = 0
                #true_cards = sorted(( card for card in true_cards),reverse=True)
                self.is_shuffle_card = True
            elif(card == 100):
                true_cards[index] = 0
                #true_cards = sorted(( card for card in true_cards),reverse=True)
                self.is_double_card = True

            index += 1

        return self.calc_card_sum(true_cards)   #関数の外に合計値を返す

    def ai_turn(self, others_info, sum, action,round_num):

        # AIの行動を決定するロジックを実装する
        # 全員の手札を配列に格納する
        now_round_num = round_num
        if now_round_num != self.previous_round_num:
            self.previous_round_num = now_round_num

            #　黒背景の０を引いたときに山札をリセットする
            if(self.is_shuffle_card):
                self.deck.reset()
               # self.deck.cashed_cards = [] #山札に戻すカードをリセットする
                self.is_shuffle_card = False

            self.expect_cards = [player["card_info"] for player in others_info] # 他プレイヤーの手札を格納する
            for card in self.expect_cards:
                print(f"deck {self.deck.cards} ")
                print(f"expect_cards {self.expect_cards}")
                if len(self.deck.cards) > 0:
                  if card in self.deck.cards:
                     self.deck.cards.remove(card) # 場のカードを山札から削除する
                  else:
                     self.deck.reset()
                     #self.deck.cashed_cards = [] #山札に戻すカードをリセットする
                     self.deck.cards.remove(card) # 場のカードを山札から削除する
                else:
                    self.deck.reset()
                    # random.shuffle(self.deck.cashed_cards) #山札に戻すカードをシャッフルする
                    # #山札が空になったら、捨て札を山札に追加する
                    # self.deck.cards = self.deck.cashed_cards.copy()
                    # self.deck.cashed_cards = []

            #self.deck.cashed_cards.append(card)
            self.mycard = self.deck.top_show_card() # 自分の手札を引く
            self.expect_cards.append(self.mycard) # 自分の手札を格納する
            sorted(self.expect_cards, reverse=True) # 降順にソートする
            self.expect_sum = self.convert_card(self.expect_cards, False, self.deck)  # 場のカードの合計値を計算する
            #もし宣言できる数が予測値を超えないなら,その幅でランダムに選ぶ
            if self.expect_sum in action:
              if self.expect_sum - action[1] > 5:
               expect_index = action.index(action[1] + 5) # 予測値のインデックスを取得する
              else:
               expect_index = action.index(self.expect_sum)
            else:
               expect_index = action[1]
            RED = '\033[31m'
            END = '\033[0m'
            print(RED  + str(expect_index) +  END)
            if len(action[1:expect_index]) > 0:
                return random.choice(action[1:expect_index])
            else:
                return -1

        else:
            #もし宣言できる数が予測値を超えないなら,その幅でランダムに選ぶ
            if self.expect_sum in action:
               expect_index = action.index(self.expect_sum) # 予測値のインデックスを取得する
            else:
               expect_index = 1
            RED = '\033[31m'
            END = '\033[0m'
            print(RED  + str(expect_index) +  END)
            if len(action[1:expect_index]) > 0:
                return random.choice(action[1:expect_index])
            else:
                return -1

    def AI_player_action(self,others_info, sum, log, actions, round_num):
        # カスタムロジックを実装
        print(f"[SampleClient] AI deciding action based on sum: {sum}, log: {log}, actions: {actions},others_info: {others_info}, round_num: {round_num}")
        # 例: ランダムにアクションを
        select_action = self.ai_turn(others_info, sum, actions, round_num)
        RED = '\033[31m'
        END = '\033[0m'
        print(RED  + str(select_action) +  END)
        return  select_action




if __name__ == "__main__":

    predefs = [
        [SampleClient(player_name="PreAI1", is_ai=True), "PreAI1"],
        [SampleClient(player_name="PreAI2", is_ai=True), "PreAI2"],
        [SampleClient(player_name="PreAI3", is_ai=True), "PreAI3"],
        [SampleClient(player_name="PreAI4", is_ai=True), "PreAI4"],
        [SampleClient(player_name="PreAI5", is_ai=True), "PreAI5"]
    ]

    arena = Arena(total_matches=5, predefined_clients=predefs)
    arena.run()