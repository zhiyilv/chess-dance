import itertools
import pandas
import copy
import json

label = ['Q', 'K', 'R', 'N', 'B']  # fix the order of those five pieces
pos0 = [(0, 1), (1, 7), (4, 4), (6, 0), (7, 6)]  # it stores the initial positions

pr = [7, 1890, 8, 10080, 20, 840, 144, 1260]
pc = [2744, 36, 375, 336, 108, 240, 20, 504]
R0 = [(), (), (), (), (), (), (), pr, pc]  # the first 7 tuples to store positions for steps 1~7
# better use list instead of tuples, if you want to store and load data with json
# since json has no structure of tuple, it will automatically convert it to list
# added the function load_var to handle this


def get_board(R):
    """
    transform a list R to a printable chess board
    :param R: the list that stores positions and products
    :return: a pandas.DataFrame, which is clear to see the board
    """
    B = [['--' for j in range(8)] for j in range(8)]  # use '--' for unknown
    B[0][1] = 'Q0'
    B[1][7] = 'K0'
    B[4][4] = 'R0'
    B[6][0] = 'N0'
    B[7][6] = 'B0'

    for step in range(len(R)-2):  # step is used as index, the move number is step+1
        positions = R[step]
        if positions:
            for piece_id in range(5):
                pos = positions[piece_id]
                B[pos[0]][pos[1]] = label[piece_id] + str(step+1)
    return pandas.DataFrame(B, R[-2], R[-1])


def show(R):
    print(get_board(R))


def cal_times_for_val(prod, val):
    """
    calculate prod can be divided by val how many times
    is not suitable when val == 1
    :param prod:
    :param val:
    :return:
    """
    times = 0
    while (prod >= val) and (prod % val == 0):
        times += 1
        prod /= val
    return times


# the following 5 functions to check whether the move is feasible for a single piece
def single_move_feasible_q(cur, nxt):
    return ((nxt[0]-cur[0]) * (nxt[1]-cur[1]) == 0
            or abs(nxt[0]-cur[0]) == abs(nxt[1]-cur[1]))


def single_move_feasible_k(cur, nxt):
    return ((abs(nxt[0]-cur[0]) < 2)
            and (abs(nxt[1]-cur[1]) < 2))


def single_move_feasible_r(cur, nxt):
    return (nxt[0]-cur[0]) * (nxt[1]-cur[1]) == 0


def single_move_feasible_n(cur, nxt):
    return abs(nxt[0] - cur[0]) * abs(nxt[1] - cur[1]) == 2


def single_move_feasible_b(cur, nxt):
    return abs(nxt[0]-cur[0]) == abs(nxt[1]-cur[1])


def move_feasible(cur_pos, nxt_pos):
    """
    check whether the move is feasible for all 5 pieces
    simply check the move, ignore cases of leaping
    :param cur_pos:
    :param nxt_pos:
    :return:
    """
    return single_move_feasible_q(cur_pos[0], nxt_pos[0]) and single_move_feasible_k(cur_pos[1], nxt_pos[1]) \
           and single_move_feasible_r(cur_pos[2], nxt_pos[2]) and single_move_feasible_n(cur_pos[3], nxt_pos[3]) \
           and single_move_feasible_b(cur_pos[4], nxt_pos[4])


def board_feasible(R):
    """
    check whether the board is feasible with current information
    :param R:
    :return:
    """
    cur_pos = [(0, 1), (1, 7), (4, 4), (6, 0), (7, 6)]
    for nxt_pos in R[:-2]:
        if cur_pos and nxt_pos:
            if not move_feasible(cur_pos, nxt_pos):
                return False
        cur_pos = nxt_pos
    return True


def pos_feasible_check(positions, focus, R):
    """
    check whether the positions is suitable for placing the step
    can check step 7~2, not suitable for 1
    :param positions:
    :param focus: the step we are focusing on
    :param R: the board
    :return:
    """
    if focus != 7:  # if we are focusing on step 7, no need to check a higher step
        if R[focus]:  # R[focus] stores positions for step (focus+1), i.e. next positions
            if not move_feasible(positions, R[focus]):
                return False
    if R[focus-2]:  # R[focus-2] stores positions for step (focus-1), i.e. previous positions
        if not move_feasible(R[focus-2], positions):
            return False
    return True


def single_pos_no_conflict_check(position, R):
    """
    check whether the position is vacant
    :param position:
    :param R:
    :return:
    """
    if position in pos0:
        return False
    for step in R[:-2]:
        if position in step:
            return False
    return True


def pos_no_conflict_check(positions, R):
    """
    check the positions are vacant
    :param positions:
    :param R:
    :return:
    """
    for pos in positions:
        if not single_pos_no_conflict_check(pos, R):
            return False
    return True


def reproduce(R, focus):
    """
    generate a list of all feasible boards, filled the step: focus
    :param R:
    :param focus:
    :return:
    """
    row_feasible = []
    col_feasible = []  # to store feasible indexes

    for j in range(8):
        t = cal_times_for_val(R[-2][j], focus)
        if t > 0:
            row_feasible.extend([j] * t)  # insert multiple times for selection
        t = cal_times_for_val(R[-1][j], focus)
        if t > 0:
            col_feasible.extend([j] * t)

    row_feasible_combination_set = set(itertools.combinations(row_feasible, 5))
    col_feasible_permutation_set = set(itertools.permutations(col_feasible, 5))
    # fix the order of row, and permute columns


    result_R_list = []
    for row_index in row_feasible_combination_set:
        for col_index in col_feasible_permutation_set:
            positions = set(zip(row_index, col_index))
            # combine row and column to get position, and eliminate duplicates

            # len(positions) == 5 eliminates those different pieces with the same position
            if len(positions) == 5 and pos_no_conflict_check(positions, R):
                for p in itertools.permutations(positions):  # permute positions for those pieces
                    if pos_feasible_check(p, focus, R):  # if the position combination if feasible, add to the result
                        candidate = copy.deepcopy(R)
                        candidate[focus-1] = p  # update details
                        for pos in p:
                            candidate[-2][pos[0]] /= focus
                            candidate[-1][pos[1]] /= focus
                        result_R_list.append(candidate)
    return result_R_list


def save_to_file(filename, R_list):
    """
    saves the list of boards into two files
    one is the board
    one is the variable
    note that positions (tuples) will be transformed into lists automatically
    :param filename:
    :param R_list:
    :return:
    """
    k = len(R_list)
    with open(filename+'_board', mode='w') as file:
        file.write('There are totally {} candidates\n'.format(k))
        for i in range(k):
            file.write('# {}\n'.format(i+1))
            file.write(str(get_board(R_list[i])) + '\n')

    save_var(filename, R_list)


def save_var(filename, R_list):
    with open(filename+'_var', mode='w') as var:
        json.dump(R_list, var)


def load_var(step):
    """
    load the list of boards from the file
    note that after loading, all positions should be transformed back to tuples
    :param step:
    :return:
    """
    with open(step) as file:
        R_list = json.load(file)
    for i in range(len(R_list)):  # transform
        for j in range(7):
            R_list[i][j] = [tuple(k) for k in R_list[i][j]]
    return R_list


def fill_gap_2_0(R):
    """
    to fill the move 1
    :param R:
    :return:
    """
    suitable_positions = [[], [], [], [], []]  # stores all suitable positions for pieces respectively
    for row_idx in range(8):
        for col_idx in range(8):
            if single_pos_no_conflict_check((row_idx, col_idx), R):  # iterate all vacant positions
                if single_move_feasible_q(pos0[0], (row_idx, col_idx)) \
                        and single_move_feasible_q((row_idx, col_idx), R[1][0]):
                    suitable_positions[0].append((row_idx, col_idx))
                if single_move_feasible_k(pos0[1], (row_idx, col_idx)) \
                        and single_move_feasible_k((row_idx, col_idx), R[1][1]):
                    suitable_positions[1].append((row_idx, col_idx))
                if single_move_feasible_r(pos0[2], (row_idx, col_idx)) \
                        and single_move_feasible_r((row_idx, col_idx), R[1][2]):
                    suitable_positions[2].append((row_idx, col_idx))
                if single_move_feasible_n(pos0[3], (row_idx, col_idx)) \
                        and single_move_feasible_n((row_idx, col_idx), R[1][3]):
                    suitable_positions[3].append((row_idx, col_idx))
                if single_move_feasible_b(pos0[4], (row_idx, col_idx)) \
                        and single_move_feasible_b((row_idx, col_idx), R[1][4]):
                    suitable_positions[4].append((row_idx, col_idx))
    if [] in suitable_positions:
        return []

    result_list = []
    for pos1 in itertools.product(*suitable_positions):  # iterate all combinations
        if len(set(pos1)) == 5:  # eliminate those different pieces with the same position
            tmp = copy.deepcopy(R)
            tmp[0] = pos1
            result_list.append(tmp)
    return result_list


def add_step_8(R):
    """
    fill the board with move 8
    the logic is similar to fill_gap_2_0
    :param R:
    :return:
    """
    suitable_positions = [[], [], [], [], []]
    for row_idx in range(8):
        for col_idx in range(8):
            if single_pos_no_conflict_check((row_idx, col_idx), R):
                if single_move_feasible_q(R[6][0], (row_idx, col_idx)):
                    suitable_positions[0].append((row_idx, col_idx))
                if single_move_feasible_k(R[6][1], (row_idx, col_idx)):
                    suitable_positions[1].append((row_idx, col_idx))
                if single_move_feasible_r(R[6][2], (row_idx, col_idx)):
                    suitable_positions[2].append((row_idx, col_idx))
                if single_move_feasible_n(R[6][3], (row_idx, col_idx)):
                    suitable_positions[3].append((row_idx, col_idx))
                if single_move_feasible_b(R[6][4], (row_idx, col_idx)):
                    suitable_positions[4].append((row_idx, col_idx))
    if [] in suitable_positions:
        return []
    result_list = []
    for pos8 in itertools.product(*suitable_positions):
        if len(set(pos8)) == 5:
            tmp = copy.deepcopy(R)
            tmp.insert(7, pos8)  # insert the positions for label 8
            tmp[-2] = [7, 1890, 8, 10080, 20, 840, 144, 1260]
            tmp[-1] = [2744, 36, 375, 336, 108, 240, 20, 504]  # restore the products
            for pos in pos8:
                tmp[-2][pos[0]] *= 8
                tmp[-1][pos[1]] *= 8  # update the products
            result_list.append(tmp)
    return result_list





















