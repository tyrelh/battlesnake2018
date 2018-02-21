import bottle
import os
import time

debug = False
status = False
theme = 'orange' # blue or orange
# board variables
SPACE = 0
KILL_ZONE = 1
FOOD = 2
#MY_HEAD = 3
DANGER = 
SNAKE_BODY = 4
ENEMY_HEAD = 5
#WALL = 7
directions = ['up', 'left', 'down', 'right']
UP = 0
LEFT = 1
DOWN = 2
RIGHT = 3
# general variables
game_id = ''
board_width = 0
board_height = 0
# my snake variables
direction = 0
health = 100
turn = 0
survival_min = 50
my_id = ''
INITIAL_FEEDING = 3


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


# respond on /start
@bottle.post('/start')
def start():
    global game_id, board_width, board_height, survival_min
    data = bottle.request.json
    print('STARTING NEW GAME.')
    # get theme info
    # default theme blue
    primary_color = '#27cbf0'
    secondary_color = '#f0f0fd'
    head_url = '%s://%s/static/snake_profile_blue.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )
    if theme == 'orange':
        primary_color = '#ffaf65'
        secondary_color = '#f08c41'
        head_url = '%s://%s/static/snake_profile_orange.png' % (
            bottle.request.urlparts.scheme,
            bottle.request.urlparts.netloc
        )
    return {
        'color': primary_color,
        'secondary_color': secondary_color,
        'head_url': head_url,
        'name': 'Zero_Cool',
        'taunt': 'So cool fam.',
        #'head_type': 'bender',
        #'tail_type': 'freckled'
    }


# respond on /move
@bottle.post('/move')
def move():
    global direction, directions, board_height, board_width, game_id, health, turn, my_id
    data = bottle.request.json
    start_time = time.time()
    board_width = data['width']
    board_height = data['height']
    my_id = data['you']['id']
    health = data['you']['health']
    turn = data['turn']
    taunt = 'Super cool.'
    survival_min = set_health_min(data)
    # if health is below set threshold
    if health < survival_min:
        taunt = 'Its cool.'
        direction = hungry(data)
    # if not the biggest snake
    elif not biggest(data):
        taunt = 'Not cool.'
        direction = hungry(data)
    # if you are the biggest snake
    elif biggest(data):
        taunt = 'Youre cool.'
        direction = hunt(data)
    # if all is well
    else:
        taunt = 'Super cool.'
        direction = kill_time(data)
    # print data for debugging
    if status:
        print('REMAINING HEALTH IS ' + str(health) + ' ON TURN ' + str(turn) + '.')
        print('SENDING MOVE: ' + str(directions[direction]))
    end_time = time.time(
    print('Time for move was ' + str((end_time - start_time) * 1000.0) + 'ms')
    # return next move
    return {
        'move': directions[direction],
        'taunt': taunt
    }


# seek closest food
def hungry(data):
    if status: print('HUNGRY! SEEKING FOOD.')
    grid = build_map(data)
    target = closest_food(grid, data)
    # if there are no food
    if not target:
        target = get_tail(data)
    move = astar(data, grid, target, 'food')
    return move


# follow own tail to kill time
def kill_time(data):
    if status: print('COOL. KILLING TIME.')
    grid = build_map(data)
    tail = get_tail(data)
    move = astar(data, grid, tail, 'my_tail')
    return move


# target edible enemy head
def hunt(data):
    if status: print('ON THE HUNT! SEEKING ENEMY HEAD.')
    grid = build_map(data)
    target = get_enemy_head(grid, data)
    # if there are no kill zones
    if not target:
        target = get_tail(data)
    move = astar(data, grid, target, 'enemy_head')
    return move


# return map array
def build_map(data):
    global my_id, board_height, board_width
    if status: print('BUILDING MAP...')
    my_length = data['you']['length']
    # create map and fill with SPACEs
    grid = [ [SPACE for col in range(data['height'])] for row in range(data['width'])]
    turn = data['turn']
    # fill in food locations
    for food in data['food']['data']:
        grid[food['x']][food['y']] = FOOD
    # fill in snake locations
    for snake in data['snakes']['data']:
        for segment in snake['body']['data']:
            # get each segment from data {snakes, data, body, data}
            grid[segment['x']][segment['y']] = SNAKE_BODY
        # mark snake head locations
        #if debug: print('Snake id = ' + str(snake['id']))
        #if debug: print('My id = ' + str(my_id))
        # mark tails as empty spaces only after turn 3
        if debug:
            if snake['id'] == my_id:
                print('-1 body seg: ' + str(snake['body']['data'][-1]['x']) + ',' + str(snake['body']['data'][-1]['y']))
                print('-2 body seg: ' + str(snake['body']['data'][-2]['x']) + ',' + str(snake['body']['data'][-2]['y']))
        #if turn > 3:
        if snake['body']['data'][-1] != snake['body']['data'][-2]:
            tempX = snake['body']['data'][-1]['x']
            tempY = snake['body']['data'][-1]['y']
            grid[tempX][tempY] = SPACE
        # dont mark own head or own danger zones
        if snake['id'] == my_id: continue
        head = get_coords(snake['body']['data'][0])
        grid[head[0]][head[1]] = ENEMY_HEAD
        # mark danger locations around enemy head
        # check down from head
        head_zone = DANGER
        if snake['length'] < my_length:
            head_zone = KILL_ZONE
        if (head[1] + 1 < board_height):
            if grid[head[0]][head[1] + 1] < head_zone:
                grid[head[0]][head[1] + 1] = head_zone
        # check up from head
        if (head[1] - 1 > 0):
            if grid[head[0]][head[1] - 1] < head_zone:
                grid[head[0]][head[1] - 1] = head_zone
        # check left from head
        if (head[0] - 1 > 0):
            if grid[head[0] - 1][head[1]] < head_zone:
                grid[head[0] - 1][head[1]] = head_zone
        # check right from head
        if (head[0] + 1 < board_width):
            if grid[head[0] + 1][head[1]] < head_zone:
                grid[head[0] + 1][head[1]] = head_zone
    # mark my head location
    #grid[data['you']['body']['data'][0]['x']][data['you']['body']['data'][0]['y']] = 1
    #if debug: print_map(grid)
    return grid


# astar search, returns move that moves closest to destination
def astar(data, grid, destination, mode):
    global debug
    if debug:
        print("map:")
        print_map(grid)
    if status: print('MAP BUILT! CALCULATING PATH...')
    #destination = get_coords(destination)
    search_scores = build_astar_grid(data, grid)
    open_set = []
    closed_set = []
    # set start location to current head location
    start = current_location(data)
    # on first 3 moves, point to closest food
    if data['turn'] < INITIAL_FEEDING:
        destination = closest_food(grid, data)
    if debug:
        print('astar destination: ' + str(destination))
        # print("astar grid before search:")
        # print_f_scores(search_scores)
    open_set.append(start)
    # while openset is NOT empty keep searching
    while open_set:
        lowest_cell = [9999, 9999] # x, y
        lowest_f = 9999
        # find cell with lowest f score
        for cell in open_set:
            if search_scores[cell[0]][cell[1]].f < lowest_f: # CONSIDER CHANGING TO <= AND THEN ALSO COMPARING G SCORES
                lowest_f = search_scores[cell[0]][cell[1]].f
                lowest_cell = cell
        # found path to destination
        if lowest_cell[0] == destination[0] and lowest_cell[1] == destination[1]:
            if status: print('FOUND A PATH!')
            if debug:
                print("astar grid after search success:")
                print_f_scores(search_scores)
            # retrace path back to origin to find optimal next move
            temp = lowest_cell
            if debug:
                print('astar start pos: ' + str(start))
            while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                temp = search_scores[temp[0]][temp[1]].previous
            # get direction of next optimal move
            if debug: print('astar next move: ' + str(temp))
            next_move = calculate_direction(start, temp, grid, data)
            return next_move
        # else continue searching
        current = lowest_cell
        current_cell = search_scores[current[0]][current[1]]
        # update sets
        open_set.remove(lowest_cell)
        closed_set.append(current)
        # check every viable neighbor to current cell
        for neighbor in search_scores[current[0]][current[1]].neighbors:
            neighbor_cell = search_scores[neighbor[0]][neighbor[1]]
            if neighbor[0] == destination[0] and neighbor[1] == destination[1]:
                if status: print('FOUND A PATH! (neighbor)')
                neighbor_cell.previous = current
                if debug:
                    print("astar grid after search success:")
                    print_f_scores(search_scores)
                # retrace path back to origin to find optimal next move
                temp = neighbor
                if debug:
                    print('astar start pos: ' + str(start))
                while search_scores[temp[0]][temp[1]].previous[0] != start[0] or search_scores[temp[0]][temp[1]].previous[1] != start[1]:
                    temp = search_scores[temp[0]][temp[1]].previous
                # get direction of next optimal move
                if debug: print('astar next move: ' + str(temp))
                next_move = calculate_direction(start, temp, grid, data)
                return best_move(next_move, data, grid)
            # check if neighbor can be moved to
            if neighbor_cell.state < SNAKE_BODY:
                # check if neighbor has already been evaluated
                if neighbor not in closed_set:# and grid[neighbor[0]][neighbor[1]] <= FOOD:
                    temp_g = current_cell.g + 1
                    shorter = True
                    # check if already evaluated with lower g score
                    if neighbor in open_set:
                        if temp_g > neighbor_cell.g: # CHANGE TO >= ??
                            shorter = False
                    # if not in either set, add to open set
                    else:
                        #if debug: print('neighbor: ' + str(grid[neighbor[0]][neighbor[1]]))
                        open_set.append(neighbor)
                    # this is the current best path, record it
                    if shorter:
                        neighbor_cell.g = temp_g
                        neighbor_cell.h = get_distance(neighbor, destination)
                        neighbor_cell.f = neighbor_cell.g + neighbor_cell.h
                        neighbor_cell.previous = current
        # inside for neighbor
    # inside while open_set
    # if reach this point and open set is empty, no path
    if not open_set:
        if status: print('COULD NOT FIND PATH!')
        if debug:
            print("astar grid after search failure:")
            print_f_scores(search_scores)

        move = 2
        if mode == 'food' or mode == 'enemy_head':
            tail = get_tail(data)
            move = astar(data, grid, tail, 'my_tail')
        
        return best_move(move, data, grid)


# return direction from a to b
def calculate_direction(a, b, grid, data):
    if status: print('CALCULATING NEXT MOVE...')
    x = a[0] - b[0]
    y = a[1] - b[1]
    direction = 0
    # directions = ['up', 'left', 'down', 'right']
    if x < 0:
        direction = 3
    elif x > 0:
        direction = 1
    elif y < 0:
        direction = 2
    count = 0
    if not valid_move(direction, grid, data):
        if count == 3:
            if status:
                print('DEAD END, NO VALID MOVE REMAINING!')
                print('GAME OVER')
            return direction
        count += 1
        direction += 1
        if direction == 4:
            direction = 0
    return direction


# out of the 3 possible moves, return the best one
def best_move(reccommended_move, data, grid):
    global board_height, board_width
    if status: print('CHECKING FOR BEST MOVE...')
    # directions = ['up', 'left', 'down', 'right']
    # check reccommended move first
    # snake_length = data['you']['length']
    # if valid_move(reccommended_move, grid, data):
    #     area = look_ahead(reccommended_move, grid, data)
    #     if debug: print('Length: ' + str(snake_length) + '. Area: ' + str(area))
        
    #     # if move_contains_tail
    #     if snake_length <= area or move_contains_tail(reccommended_move, grid, data):
    #         return reccommended_move

    reg_moves = []
    danger_moves = []
    kill_moves = []
    current = current_location(data)
    best_move = []
    # check UP move
    if current[1] - 1 >= 0 and grid[current[0]][current[1] - 1] <= DANGER:
        if debug: print('move UP is viable')
        reg_moves.append(UP)
    # check DOWN move
    if current[1] + 1 < board_height and grid[current[0]][current[1] + 1] <= DANGER:
        if debug: print('move DOWN is viable')
        reg_moves.append(DOWN)
    # check LEFT move
    if current[0] - 1 >= 0 and grid[current[0] - 1][current[1]] <= DANGER:
        if debug: print('move LEFT is viable')
        reg_moves.append(LEFT)
    # check RIGHT move
    if current[0] + 1 < board_width and grid[current[0] + 1][current[1]] <= DANGER:
        if debug: print('move RIGHT is viable')
        reg_moves.append(RIGHT)
    # check viable moves for a move better than DANGER
    if reg_moves:
        for move in reg_moves:
            # UP
            if move == UP:
                if grid[current[0]][current[1] - 1] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0]][current[1] - 1] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # DOWN
            elif move == DOWN:
                if grid[current[0]][current[1] + 1] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0]][current[1] + 1] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # LEFT
            elif move == LEFT:
                if grid[current[0] - 1][current[1]] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0] - 1][current[1]] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
            # RIGHT
            elif move == RIGHT:
                if grid[current[0] + 1][current[1]] == DANGER:
                    reg_moves.remove(move)
                    danger_moves.append(move)
                elif grid[current[0] + 1][current[1]] == KILL_ZONE:
                    reg_moves.remove(move)
                    kill_moves.append(move)
    else: # NO MOVE AT ALL
        if status:
            print('DEAD END, NO VALID MOVE REMAINING! (none at all)')
            print('GAME OVER')
        return reccommended_move # suicide

    # if a kill move exists, pick the best one
    if kill_moves:
        # if all moves are kill moves, take reccommended move
        if len(kill_moves) >= 3 and reccommended_move in kill_moves:
            if debug: print('ALL MOVES ARE KILL MOVES, TAKING RECCOMMENDED MOVE!')
            return reccommended_move
        # otherwise calculate best kill move
        if status: print('KILL move exists!')
        best_move = reccommended_move
        best_area = 0
        # check reccommended_move first
        if valid_move(reccommended_move, grid, data):
            best_move = reccommended_move
            best_area = look_ahead(reccommended_move, grid, data)
        # check every other kill move
        for move in kill_moves:
            # if the move contains your tail, its probably a pretty good move
            if move_contains_tail(move, grid, data):
                return move
            # check available area of move
            new_area = look_ahead(move, grid, data)
            if new_area > best_area:
                best_area = new_area
                best_move = move
        return best_move

    # if a non-DANGER move exists, calculate the best one
    elif reg_moves:
        # if ALL moves are reg, take reccommended move
        if status: print(str(len(reg_moves)) + ' VIABLE move(s) exist!')
        if len(reg_moves) >= 3 and reccommended_move in reg_moves:
            if debug: print('ALL MOVES VALID, TAKING RECCOMMENDED MOVE!')
            return reccommended_move
        # otherwise calulate the best reg move
        best_move = reccommended_move
        best_area = 0
        # check reccommended move first
        if valid_move(reccommended_move, grid, data):
            best_move = reccommended_move
            best_area = look_ahead(reccommended_move, grid, data)
        # check every other reg move
        for move in reg_moves:
            # if the move contains your tail, its probably a pretty good move
            #if move_contains_tail(move, grid, data):
                #return move
            # check available area of move
            new_area = look_ahead(move, grid, data)

            if new_area > best_area:
                best_area = new_area
                best_move = move

        return best_move

    # if only DANGER moves exist, calculate best one
    elif danger_moves:
        # if ALL moves are DANGER, take reccommended_move
        if len(danger_moves) >= 3: return reccommended_move
        if status: print('No VIABLE move, only DANGER moves exist!')
        best_move = reccommended_move
        best_area = 0
        # check reccommended move first
        if valid_move(reccommended_move, grid, data):
            best_move = reccommended_move
            best_area = look_ahead(reccommended_move, grid, data)
        for move in danger_moves:
            # check available area of move
            new_area = look_ahead(move, grid, data)
            if new_area > best_area:
                best_area = new_area
                best_move = move
        return best_move
    else: # NO MOVE AT ALL
        if status:
            print('DEAD END, NO VALID MOVE REMAINING! (bottom)')
            print('GAME OVER')
        return reccommended_move # suicide


# calculates number of cells accessable given a move
def look_ahead(move, grid, data):
    # directions = ['up', 'left', 'down', 'right']
    # test_grid = None
    # if debug:
    #     w = len(grid)
    #     h = len(grid[0])
    #     test_grid = [ [0 for col in range(h)] for row in range(w)]
    #     for i in range(w):
    #         for j in range(h):
    #             test_grid[i][j] = grid[i][j]
    #     print('test grid before traversal:')
    #     print_map(test_grid)
    area = 0
    current = current_location(data)
    # get move coords
    given_move_coords = current
    if move == UP:
        given_move_coords = [current[0], current[1] - 1]
    elif move == DOWN:
        given_move_coords = [current[0], current[1] + 1]
    elif move == LEFT:
        given_move_coords = [current[0] - 1, current[1]]
    elif move == RIGHT:
        given_move_coords = [current[0] + 1, current[1]]
    move_queue = []
    checked_moves = []
    # start with given move
    move_queue.append(given_move_coords)
    # mark current as checked
    checked_moves.append(current)
    # iterate over all possible moves given initial move
    while move_queue:
        for next_move in move_queue:
            # next move is assessed
            area += 1
            #if debug: test_grid[next_move[0]][next_move[1]] = 7 #<##
            move_queue.remove(next_move)
            checked_moves.append(next_move)
            # check neighbors
            # check UP move
            neighbor_up = [next_move[0], next_move[1] - 1]
            # if not already checked, or queued to be checked
            if neighbor_up != current and neighbor_up not in checked_moves and neighbor_up not in move_queue:
                # if move on board
                if neighbor_up[1] >= 0:
                    # if move is valid
                        if grid[neighbor_up[0]][neighbor_up[1]] <= DANGER:
                            move_queue.append(neighbor_up)
            # check DOWN move
            neighbor_down = [next_move[0], next_move[1] + 1]
            # if not already checked, or queued to be checked
            if neighbor_down != current and neighbor_down not in checked_moves and neighbor_down not in move_queue:
                # if move on board
                if neighbor_down[1] < board_height:
                    # if move is valid
                        if grid[neighbor_down[0]][neighbor_down[1]] <= DANGER:
                            move_queue.append(neighbor_down)
            # check LEFT move
            neighbor_left = [next_move[0] - 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_left != current and neighbor_left not in checked_moves and neighbor_left not in move_queue:
                # if move on board
                if neighbor_left[0] >= 0:
                    # if move is valid
                        if grid[neighbor_left[0]][neighbor_left[1]] <= DANGER:
                            move_queue.append(neighbor_left)
            # check RIGHT move
            neighbor_right = [next_move[0] + 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_right != current and neighbor_right not in checked_moves and neighbor_right not in move_queue:
                # if move on board
                if neighbor_right[0] < board_width:
                    # if move is valid
                        if grid[neighbor_right[0]][neighbor_right[1]] <= DANGER: # <<<<<<<< failing
                            move_queue.append(neighbor_right)
    # if debug:
    #     print('test grid after traversal:')
    #     print_map(test_grid)
    return area


# return if the area enclosed by the given move includes own tail
# function copied from look_ahead. May contain erroneous comments
def move_contains_tail(move, grid, data):
    # directions = ['up', 'left', 'down', 'right']
    if status: print('CHECKING IF MOVE CONTAINS TAIL...')
    tail = get_coords(data['you']['body']['data'][-1])
    current = current_location(data)
    contains_tail = False
    # get move coords
    given_move_coords = current
    if move == UP:
        given_move_coords = [current[0], current[1] - 1]
    elif move == DOWN:
        given_move_coords = [current[0], current[1] + 1]
    elif move == LEFT:
        given_move_coords = [current[0] - 1, current[1]]
    elif move == RIGHT:
        given_move_coords = [current[0] + 1, current[1]]
    move_queue = []
    checked_moves = []
    # start with given move
    move_queue.append(given_move_coords)
    # mark current as checked
    checked_moves.append(current)
    # iterate over all possible moves given initial move
    while move_queue:
        for next_move in move_queue:
            # next move is assessed
            if tail[0] == next_move[0] and tail[1] == next_move[1]:
                contains_tail = True
            move_queue.remove(next_move)
            checked_moves.append(next_move)
            # check neighbors
            # check UP move
            neighbor_up = [next_move[0], next_move[1] - 1]
            # if not already checked, or queued to be checked
            if neighbor_up != current and neighbor_up not in checked_moves and neighbor_up not in move_queue:
                # if move on board
                if neighbor_up[1] >= 0:
                    # if move is valid
                        if grid[neighbor_up[0]][neighbor_up[1]] <= DANGER:
                            move_queue.append(neighbor_up)
            # check DOWN move
            neighbor_down = [next_move[0], next_move[1] + 1]
            # if not already checked, or queued to be checked
            if neighbor_down != current and neighbor_down not in checked_moves and neighbor_down not in move_queue:
                # if move on board
                if neighbor_down[1] < board_height:
                    # if move is valid
                        if grid[neighbor_down[0]][neighbor_down[1]] <= DANGER:
                            move_queue.append(neighbor_down)
            # check LEFT move
            neighbor_left = [next_move[0] - 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_left != current and neighbor_left not in checked_moves and neighbor_left not in move_queue:
                # if move on board
                if neighbor_left[0] >= 0:
                    # if move is valid
                        if grid[neighbor_left[0]][neighbor_left[1]] <= DANGER:
                            move_queue.append(neighbor_left)
            # check RIGHT move
            neighbor_right = [next_move[0] + 1, next_move[1]]
            # if not already checked, or queued to be checked
            if neighbor_right != current and neighbor_right not in checked_moves and neighbor_right not in move_queue:
                # if move on board
                if neighbor_right[0] < board_width:
                    # if move is valid
                        if grid[neighbor_right[0]][neighbor_right[1]] <= DANGER:
                            move_queue.append(neighbor_right)
    if contains_tail:
        if debug: print('move contains tail!')
    else:
        if debug: print('move DOESNT contain tail')
    return contains_tail


# check if move in direction will kill you
# return True if valid
# return False if it will kill you
def valid_move(d, grid, data):
    global board_height, board_width
    current = current_location(data)
    if status: print('CHECKING IF MOVE IS VALID!')
    # directions = ['up', 'left', 'down', 'right']
    # check up direction
    if d == 0:
        if current[1] - 1 < 0:
            if debug: print('Up move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] - 1] <= DANGER:
            if debug: print('Up move is VALID.')
            return True
        else:
            if debug: print('Up move is FATAL!')
            return False
    #check left direction
    if d == 1:
        if current[0] - 1 < 0:
            if debug: print('Left move is OFF THE MAP!')
            return False
        if grid[current[0] - 1][current[1]] <= DANGER:
            if debug: print('Left move is VALID.')
            return True
        else:
            if debug: print('Left move is FATAL!')
            return False
    # check down direction
    if d == 2:
        if current[1] + 1 > board_height - 1:
            if debug: print('Down move is OFF THE MAP!')
            return False
        if grid[current[0]][current[1] + 1] <= DANGER:
            if debug: print('Down move is VALID.')
            return True
        else:
            if debug: print('Down move is FATAL!')
            return False
    # check right direction
    if d == 3:
        if current[0] + 1 > board_width - 1:
            if debug: print('Right move is OFF THE MAP!')
            return False
        if grid[current[0] + 1][current[1]] <= DANGER:
            if debug: print('Right move is VALID.')
            return True
        else:
            if debug: print('Right move is FATAL!')
            return False
    # failsafe
    if d > 3 and status: print('valid_move FAILED! direction IS NOT ONE OF FOUR POSSIBLE MOVES!')
    return True


# return manhattan distance between a and b
def get_distance(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]))


# convert object yx to list yx
def get_coords (o):
    return (o['x'], o['y'])


# return x,y coords of current head location
def current_location(data):
    return (data['you']['body']['data'][0]['x'], data['you']['body']['data'][0]['y'])


# return coords of closest food to head
# def closest_food(data):
#     current = current_location(data)
#     shortest_distance = -1
#     closest_food = None
#     foods = data['food']['data']
#     # iterate over each piece of food
#     for food in foods:
#         food = get_coords(food)
#         distance = get_distance(current, food)
#         if shortest_distance < 0:
#             shortest_distance = distance
#             closest_food = food
#         else:
#             if distance < shortest_distance:
#                 shortest_distance = distance
#                 closest_food = food
#     return closest_food

# return coords of closest food to head, using grid
def closest_food(grid, data):
    my_location = current_location(data)
    close_food = None
    close_distance = 9999
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == FOOD:
                food = [i, j]
                distance = get_distance(my_location, food)
                if distance < close_distance:
                    close_food = food
                    close_distance = distance
    return close_food


def get_enemy_head(grid, data):
    my_location = current_location(data)
    close_kill_zone = None
    close_kill_distance = 9999
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == KILL_ZONE:
                kill_zone = [i, j]
                distance = get_distance(my_location, kill_zone)
                if distance < close_kill_distance:
                    close_kill_zone = kill_zone
                    close_kill_distance = distance
    return close_kill_zone


# return coords to own tail
def get_tail(data):
    body = data['you']['body']['data']
    tail = current_location(data)
    for segment in body:
        tail = get_coords(segment)
    return tail


# return grid of empty Cells for astar search data
def build_astar_grid(data, grid):
    w = data['width']
    h = data['height']
    astar_grid = [ [Cell(row, col) for col in range(h)] for row in range(w)]
    for i in range(w):
        for j in range(h):
            astar_grid[i][j].state = grid[i][j]
    return astar_grid


# the cell class for storing a* search information
class Cell:
    global board_height, board_width
    def __init__(self, x, y):
        self.f = 0
        self.g = 0
        self.h = 0
        self.x = x
        self.y = y
        self.state = 0;
        self.neighbors = []
        self.previous = None
        if self.x < board_width - 1:
            self.neighbors.append([self.x + 1, self.y])
        if self.x > 0:
            self.neighbors.append([self.x - 1, self.y])
        if self.y < board_height - 1:
            self.neighbors.append([self.x, self.y + 1])
        if self.y > 0:
            self.neighbors.append([self.x, self.y - 1])


# print whole map
def print_map(grid):
    #global board_height, board_width
    w = len(grid)
    h = len(grid[0])
    for i in range(h):
        line = ''
        for j in range(w):
            line += str(grid[j][i])
        print(line)


# will print f scores of the astar grid of cell data
def print_f_scores(astar_grid):
    w = len(astar_grid)
    h = len(astar_grid[0])
    for i in range(h):
        line = ''
        for j in range(w):
            line += str(astar_grid[j][i].f)
        print(line)


# returns if you are not the biggest snake
def biggest(data):
    my_id = data['you']['id']
    my_length = data['you']['length']
    longest_length = 0
    for snake in data['snakes']['data']:
        if my_id != snake['id']:
            if snake['length'] > longest_length:
                longest_length = snake['length']
    if longest_length >= my_length:
        return False
    return True


# will return the minimum health required to keep alive
def set_health_min(data):
    health_board = max(board_height, board_width) * 2
    health_length = data['you']['length']
    if health_length > health_board:
        return health_length
    return health_board


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))