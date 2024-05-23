from pettingzoo.classic import hanabi_v5

class EnvWrapper(hanabi_v5.raw_env):
    def __init__(self, **kwargs):
        self.action_history = []
        self.errors = {}
        self.errors["player_0"] = 0
        self.errors["player_1"] = 0
        self.seed = None
        super().__init__(**kwargs)
    
    def reset(self, seed=None, options=None):
        self.action_history = []
        self.errors = {}
        self.errors["player_0"] = 0
        self.errors["player_1"] = 0
        self.seed = seed
        return super().reset(seed, options)

    def step(self, action):
        # self.action_history.append(action) # for performance sake,
        # update action history manually where needed
        return super().step(action)


#################### HELPER FUNCTIONS ############################

def print_random_ascii_art():
    print(
"""
                             ...,?77??!~~~~!???77?<~.... 
                        ..?7`                           `7!.. 
                    .,=`          ..~7^`   I                  ?1. 
       ........  ..^            ?`  ..?7!1 .               ...??7 
      .        .7`        .,777.. .I.    . .!          .,7! 
      ..     .?         .^      .l   ?i. . .`       .,^ 
       b    .!        .= .?7???7~.     .>r .      .= 
       .,.?4         , .^         1        `     4... 
        J   ^         ,            5       `         ?<. 
       .%.7;         .`     .,     .;                   .=. 
       .+^ .,       .%      MML     F       .,             ?, 
        P   ,,      J      .MMN     F        6               4. 
        l    d,    ,       .MMM!   .t        ..               ,, 
        ,    JMa..`         MMM`   .         .!                .; 
         r   .M#            .M#   .%  .      .~                 ., 
       dMMMNJ..!                 .P7!  .>    .         .         ,, 
       .WMMMMMm  ?^..       ..,?! ..    ..   ,  Z7`        `?^..  ,, 
          ?THB3       ?77?!        .Yr  .   .!   ?,              ?^C 
            ?,                   .,^.` .%  .^      5. 
              7,          .....?7     .^  ,`        ?. 
                `<.                 .= .`'           1 
                ....dn... ... ...,7..J=!7,           ., 
             ..=     G.,7  ..,o..  .?    J.           F 
           .J.  .^ ,,,t  ,^        ?^.  .^  `?~.      F 
          r %J. $    5r J             ,r.1      .=.  .% 
          r .77=?4.    ``,     l ., 1  .. <.       4., 
          .$..    .X..   .n..  ., J. r .`  J.       `' 
        .?`  .5        `` .%   .% .' L.'    t 
        ,. ..1JL          .,   J .$.?`      . 
                1.          .=` ` .J7??7<.. .; 
                 JS..    ..^      L        7.: 
                   `> ..       J.  4. 
                    +   r `t   r ~=..G. 
                    =   $  ,.  J 
                    2   r   t  .; 
              .,7!  r   t`7~..  j.. 
              j   7~L...$=.?7r   r ;?1. 
               8.      .=    j ..,^   .. 
              r        G              . 
            .,7,        j,           .>=. 
         .J??,  `T....... %             .. 
      ..^     <.  ~.    ,.             .D 
    .?`        1   L     .7.........?Ti..l 
   ,`           L  .    .%    .`!       `j, 
 .^             .  ..   .`   .^  .?7!?7+. 1 
.`              .  .`..`7.  .^  ,`      .i.; 
.7<..........~<<3?7!`    4. r  `          G% 
                          J.` .!           % 
                            JiJ           .` 
                              .1.         J 
                                 ?1.     .'         
                                     7<..%
"""
    )

def update_card_age(card_age, action: int):
    # increment all elements by 1
    card_age = [x + 1 for x in card_age]

    if action < 5:
        # it's a discard action
        # they map from 0 to 4 to the cards from left to right
        card_age[action] = 0
    elif 5 < action < 10:
        # it's a play action
        # they map from 5 to 9 to the cards from left to right
        card_age[action - 5] = 0
    else:
        # we can ignore tell actions
        pass

    return card_age

def update_errors(player_cards, fireworks, action):
    # turn np arrays to lists to use python native methods
    fireworks = fireworks.tolist()
    player_cards = player_cards.tolist()

    # split fireworks and player_cards
    fireworks = [fireworks[0:5], fireworks[5:10], fireworks[10:15], fireworks[15:20], fireworks[20:25]]
    player_cards = [player_cards[0:25], player_cards[25:50], player_cards[50:75], player_cards[75:100], player_cards[100:125]]

    # check if discard results in an error
    if 0 <= action < 5:
        player_card = player_cards[action]
        color_infos = [player_card[0:5], player_card[5:10], player_card[10:15], player_card[15:20], player_card[20:25]]
        for color_info, firework in zip(color_infos, fireworks):
            if 1 not in color_info:
                continue
            card_rank = color_info.index(1) + 1
            current_firework = sum(firework)
            if card_rank > current_firework:
                return 1
            
    # check if play results in an error
    if 5 <= action < 10:
        player_card = player_cards[action - 5]
        color_infos = [player_card[0:5], player_card[5:10], player_card[10:15], player_card[15:20], player_card[20:25]]
        for color_info, firework in zip(color_infos, fireworks):
            if 1 not in color_info:
                continue
            card_rank = color_info.index(1) + 1
            current_firework = sum(firework)
            if card_rank != current_firework + 1:
                return 1

    return 0
