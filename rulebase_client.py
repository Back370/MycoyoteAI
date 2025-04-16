import random
import time

class Deck:
    def __init__(self):
        #初期条件
        #?→ max→0→×2:103,102,101,100に対応
        self.cards = [-10, -5, -5, 0, 0, 0,
                      1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3,
                      4, 4, 4, 4, 5, 5, 5, 5, 
                      10, 10, 10, 15, 15, 20, 
                      100, 101, 102, 103]
        
        self.cashed_cards = [] #山札に戻すカードを格納するリスト
    
    def shuffle(self):
        print ("Deck shuffled.")
        random.shuffle(self.cards)
    
    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            print("No card left in the deck.")
            random.shuffle(self.cashed_cards) #山札に戻すカードをシャッフルする
            #山札が空になったら、捨て札を山札に追加する
            self.cards = self.cashed_cards.copy()
            self.cashed_cards = []
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
                    new_card = self.deck.draw()
                    deck.cashed_cards.append(new_card) #103を山札に戻す
                print(f"Drawn new card: {deck.cashed_cards}")    
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


class Player:
    def __init__(self):
        self.card = None
        self.score = 0
        self.visible = 0
        self.expect_card = None
        self.expect = 0

    def play_turn(self, game_state):
        return self.ai_turn(game_state)


    def ai_turn(self, game_state):
        if self.visible > game_state["call"]:
            raise_num = random.randint(1, self.visible - game_state["call"])
            return True, raise_num
        else:
            if self.expect > game_state["call"]:
                raise_num = random.randint(1, self.expect - game_state["call"])
                return True, raise_num
            else:
                # 初手でコールストップはできない
                if game_state["call"] == 0:
                    return True, 1
                return False, 0

    # プレイヤーに見えている数だけ計算
    def calc_visible(self, players):
        Ace_count_each = 0
        for other in players:
            if self != other:
                self.visible += get_card_value(other.card)
                if other.card.value == "A":
                    Ace_count_each += 1
        self.visible *= 2**Ace_count_each

    # プレイヤーの予想値を計算
    def calc_expect(self, players, deck):
        self.expect_card = random.choice(
            deck.cards + [self.card]
        )  # 完全に残りのデッキを覚えている
        Ace_count_each = 0
        self.expect += get_card_value(self.expect_card)
        if self.expect_card.value == "A":
            Ace_count_each += 1
        for other in players:
            if self != other:
                self.expect += get_card_value(other.card)
                if other.card.value == "A":
                    Ace_count_each += 1
        self.expect *= 2**Ace_count_each

def display_cards_except_you(players):
    card_displays = []
    for player in players:
        if player.name != "You":
            card_displays.append(player.card.ascii_rep())
    for i in range(7):
        print(" ".join(card[i] for card in card_displays))
    for player in players:
        if player.name != "You":
            print(f"{player.name:^9}", end=" ")
    print()


def display_cards(players):
    card_displays = [
        player.card.ascii_rep() if player.card else [" " * 9] * 7 for player in players
    ]
    for i in range(7):
        print(" ".join(card[i] for card in card_displays))
    for player in players:
        print(f"{player.name:^9}", end=" ")
    print()


def play_round(players, deck, start_index):
    while len(players) > 1:
        print(
            f"\n{Fore.MAGENTA}***********************New Game!!***********************"
        )
        game_state = {"sum": 0, "call": 0, "Ace_count": 0}

        for player in players:
            player.visible = 0
            player.expect = 0
            player.draw_card(deck)

        # 各プレイヤーの値を計算
        for i in players:
            i.calc_visible(players)
            i.calc_expect(players, deck)

        # フィールドの合計値を計算
        for i in players:
            game_state["sum"] += get_card_value(i.card)
            if i.card.value == "A":
                game_state["Ace_count"] += 1
        game_state["sum"] *= 2 ** game_state["Ace_count"]

        time.sleep(2)

        display_cards_except_you(players)
        time.sleep(4)
        stopper = None
        while True:
            for i in range(len(players)):
                index = (i + start_index) % len(players)
                player = players[index]
                print(f"\n{Fore.CYAN}**********************************************")
                print(f"{Fore.YELLOW}It's {player.name}'s turn!")
                continue_call, raise_amount = player.play_turn(game_state)
                if continue_call:
                    game_state["call"] += raise_amount
                    print(f"{Fore.GREEN}Call is now {game_state['call']}")
                    time.sleep(2)
                else:
                    stopper = player
                    break
            if stopper:
                break

        print(
            f"\n{Fore.MAGENTA}*********************** Result !! ***********************"
        )
        display_cards(players)
        print(f"{Fore.CYAN}Field sum is {game_state['sum']}")
        print(f"{Fore.CYAN}Final call number is {game_state['call']}")
        time.sleep(4)

        stopper_index = players.index(stopper)
        previous_player = players[stopper_index - 1]

        if game_state["call"] > game_state["sum"]:
            print(f"{Fore.RED}{previous_player.name} drops out!")
            players.remove(previous_player)
            if stopper_index == 0:
                start_index = stopper_index
            else:
                start_index = stopper_index - 1
        else:
            print(f"{Fore.RED}{stopper.name} drops out!")
            players.remove(stopper)
            start_index = stopper_index - 1

        time.sleep(1.5)

    print(f"\n{Fore.MAGENTA}**********************************************")
    print(f"{Fore.YELLOW}The winner is {players[0].name}!!!")
    print(f"{Fore.MAGENTA}**********************************************")



