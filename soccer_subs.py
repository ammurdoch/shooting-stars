from pydantic import BaseModel
from typing import List
import argparse
import json
import random
import os
import shutil

parser = argparse.ArgumentParser(description='Figure our game subs')
parser.add_argument('positions_file', type=str, help='File to store positions in')
parser.add_argument('-g', '--goalie', default=False, action='store_true', help='Should we place the goalie?')
parser.add_argument('-r', '--retry', default=False, action='store_true', help='Try again')
args = parser.parse_args()


positions = [
    'left-forward',
    'right-forward',
    'left-defender',
    'right-defender',
    'center-mid',
    'center-defender',
    'goalie',
]

positions_other_than_goalie = [p for p in positions if p != 'goalie']

class Player(BaseModel):
    name: str
    preferred_positions: List[str]
    possible_positions: List[str]
    play_time: float = 0


players = [
    Player(
        name='Ella',
        preferred_positions=[
            'left-forward',
            'right-forward',
            'left-defender',
            'right-defender',
            'center-defender',
            'goalie',
        ],
        possible_positions=positions_other_than_goalie,
    ),
    Player(
        name='Aymeri',
        preferred_positions=[
            'left-forward',
            'right-forward',
            'left-defender',
            'right-defender',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Evelyn',
        preferred_positions=[
            'center-mid',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Gracelyn',
        preferred_positions=[
            'left-defender',
            'right-defender',
            'center-defender',
            'goalie'
        ],
        possible_positions=positions,
    ),
    Player(
        name='Hartley',
        preferred_positions=[
            'center-mid',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Kara',
        preferred_positions=[
            'left-defender',
            'right-defender',
            'center-defender',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Lacey',
        preferred_positions=[
            'left-forward',
            'right-forward',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Lanae',
        preferred_positions=[
            'left-forward',
            'right-forward',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Stella',
        preferred_positions=[
            'center-defender',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Tegan',
        preferred_positions=[
            'left-defender',
            'right-defender',
        ],
        possible_positions=positions_other_than_goalie
    ),
    Player(
        name='Inara',
        preferred_positions=[
            'left-defender',
            'right-defender',
            'center-defender',
        ],
        possible_positions=positions_other_than_goalie
    ),
]

player_dict = {p.name: p for p in players}

position_slots = None
if os.path.exists(args.positions_file):
    bak_filename = f'{args.positions_file}.bak'
    if args.retry and os.path.exists(bak_filename):
        pos_file = bak_filename
    elif args.retry:
        pos_file = None
    else:
        pos_file = args.positions_file
        shutil.copyfile(pos_file, bak_filename)
    if pos_file is not None:
        with open(pos_file, 'r') as f:
            data = json.loads(f.read())
            position_slots = data['positionSlots']
            play_times = data['playTimes']
            for name, play_time in play_times.items():
                player_dict[name].play_time = play_time
            for pos, name in position_slots.items():
                player_dict[name].play_time += 5
if position_slots is None:
    position_slots = {p: '' for p in positions}


if args.goalie:
    avs = [a for a in players if 'goalie' in a.preferred_positions if a.name != position_slots['goalie']]
    if avs:
        player = random.choice(avs)
        players_current_pos = [pos for pos, name in position_slots.items() if name == player.name]
        print(f"({player.name} --> {position_slots['goalie']})")
        position_slots['goalie'] = player.name
        if players_current_pos:
            players_current_pos = players_current_pos[0]
            if players_current_pos != 'goalie':
                position_slots[players_current_pos] = ''

slots_to_sub = [(pos, name) for pos, name in position_slots.items()]
play_times = {p.name: p.play_time for p in players}
# slots_to_sub.sort(reverse=True, key=lambda x: play_times[x[1]] if x[1] else 1000000)
random.shuffle(slots_to_sub)
available_players = [p for p in players if p.name not in position_slots.values()]
random.shuffle(available_players)
print('available_players', [p.name for p in available_players])
# print('slots_to_sub', json.dumps(slots_to_sub,  indent=2))
not_placed = []
for player in available_players:
    placed = False
    for pos, name in slots_to_sub:
        if pos == 'goalie':
            continue
        current_player = player_dict[name] if name else None
        if pos in player.preferred_positions and (current_player is None or current_player.play_time >= player.play_time):
            print(f"({player.name} --> {position_slots[pos]})")
            position_slots[pos] = player.name
            slots_to_sub.remove((pos, name))
            placed = True
            break
    if not placed:
        not_placed.append(player)

print('not placed', [p.name for p in not_placed])
still_not_placed = []
for player in not_placed:
    placed = False
    for pos, name in slots_to_sub:
        if pos == 'goalie':
            continue
        current_player = player_dict[name] if name else None
        if pos in player.possible_positions and (current_player is None or current_player.play_time >= player.play_time):
            print(f"({player.name} --> {position_slots[pos]})")
            position_slots[pos] = player.name
            slots_to_sub.remove((pos, name))
            placed = True
            break
    if not placed:
        still_not_placed.append(player)

print('still not placed', [p.name for p in still_not_placed])

# random.shuffle(slots_to_sub)
# for slot in slots_to_sub:
#     if slot == 'goalie' and not args.goalie:
#         continue
#     potential_players = [p for p in available_players if slot in p.preferred_positions]
#     if potential_players:
#         player = random.choice(potential_players)
#         position_slots[slot] = player.name
#         available_players = [a for a in available_players if a.name != player.name]

play_times = {p.name: p.play_time for p in players}

# print('positions', position_slots)
# print('play_times', play_times)
print('positions', json.dumps(position_slots,  indent=2))
print('play_times', json.dumps(play_times,  indent=2))

with open(args.positions_file, 'w') as f:
    f.write(json.dumps({
        'positionSlots': position_slots,
        'playTimes': play_times,
    }))
