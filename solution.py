from chess2 import *

print('start...')
R7 = reproduce(R0, 7)
R_pool_list = [R7]  # it stores a list of pools, each pool is a list of boards, move 7~2

for piece_step in range(6, 1, -1):
    pool_index = 6 - piece_step

    # store the pool for further possible use, delete for faster computing
    save_var(str(piece_step+1), R_pool_list[pool_index])

    R_pool_list.append([])  # a new pool for storing a new move
    print('There are {} candidates in pool {}'.format(len(R_pool_list[pool_index]), piece_step + 1))
    while R_pool_list[pool_index]:
        print('pop #{} from the pool {}...'.format(len(R_pool_list[pool_index]), piece_step + 1))
        last_one = R_pool_list[pool_index].pop()

        tmp = reproduce(last_one, piece_step)
        print('get {} feasible candidates, totally {}\n'.format(len(tmp), len(R_pool_list[pool_index+1])))

        R_pool_list[pool_index+1].extend(tmp)
    # remove duplicates
    R_pool_list[pool_index+1].sort()
    R_pool_list[pool_index+1] = [i for i, _ in itertools.groupby(R_pool_list[pool_index+1])]

# save the last pool, which stores all feasible boards with labels 2~7
save_to_file('2', R_pool_list[5])

# complete the board by filling the label 1
board_complete = []
for R2 in R_pool_list[5]:
    board_complete.extend(fill_gap_2_0(R2))

save_to_file('complete', board_complete)

# generate all feasible boards with label 8
R8_list = []
for board in board_complete:
    R8_list.extend(add_step_8(board))
# eliminate duplicates
R8_list.sort()
R8_list = [i for i, _ in itertools.groupby(R8_list)]

# compute sum for all those boards
R8_sum_list = []
for R8 in R8_list:
    R8_sum_list.append(sum(R8[-2]) + sum(R8[-1]))

# get the max value and show the board
max_value = max(R8_sum_list)
idx_max = [i for i, val in enumerate(R8_sum_list) if val == max_value]
for i in idx_max:
    show(R8_list[i])

print('\nall those instances with the max value {}'.format(max_value))

















