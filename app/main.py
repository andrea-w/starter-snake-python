import json
import os
import random
import bottle
from scipy.spatial import distance
import numpy

from api import ping_response, start_response, move_response, end_response

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    return {'color': '#736CCB', 'headType': 'bendr', 'tailType': 'skinny'}


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    #print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']

    head_pos = get_position_of_my_head(data)
    optimal_node = {}
    if (check_for_head_on_collision(data) != None):
        print("\n\n\n head on collision points:")
        print(str(check_for_head_on_collision(data)))
        optimal_node = random.choice(check_for_head_on_collision(data))
    else:
        goal_node = look_for_food(head_pos, data)
        optimal_node = find_next_step_in_route(head_pos, goal_node, data)
    print("optimal node: " + str(optimal_node))
    optimal_direction = get_string_direction(optimal_node, head_pos)

    return move_response(optimal_direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

def get_position_of_my_head(data):
    return data['you']['body'][0]

def get_point_to_left(pos):
    return {"x": int(pos.get("x")) - 1, "y": int(pos.get("y"))}

def get_point_to_right(pos):
    return {"x": int(pos.get("x")) + 1, "y": int(pos.get("y"))}

def get_point_upward(pos):
    return {"x": int(pos.get("x")), "y": int(pos.get("y")) - 1}

def get_point_downward(pos):
    return {"x": int(pos.get("x")), "y": int(pos.get("y")) + 1}

def get_all_4_points(pos):
    coords = []
    coords.append(get_point_to_left(pos))
    coords.append(get_point_to_right(pos))
    coords.append(get_point_upward(pos))
    coords.append(get_point_downward(pos))
    return coords

# coords is list (len 4) of (x,y) coordinates of 4 possible points to move to
def check_for_walls(coords, data):
    ok_coords = []
    # check left
    if int(coords[0].get('x')) > -1:
        ok_coords.append(coords[0])
    # check right
    if int(coords[1].get('x')) < data['board']['width']:
        ok_coords.append(coords[1])
    # check up
    if int(coords[2].get('y')) > -1:
        ok_coords.append(coords[2])
    # check down
    if int(coords[3].get('y')) < data['board']['height']:
        ok_coords.append(coords[3])

    return ok_coords

def check_own_body(coords, data):
    ok_coords = coords
    for point in coords:
        if point in data['you']['body']:
            ok_coords.remove(point)
            print("avoided collision with self at " + str(point))

    return ok_coords

def check_for_other_snakes(coords, data):
    ok_coords = coords
    for point in coords:
        for snake in data['board']['snakes']:
            if point in snake['body']:
                ok_coords.remove(point)
                print("avoided collision with another snake at " + str(point))
    return ok_coords

def check_if_next_to_food(coords, data):
    for food in data['board']['food']:
        if food in coords:
            return food
    return False

def look_for_food(head_pos, data):
    min_dist = 99
    nearest_food_loc = {}
    for food in data['board']['food']:
        dist = distance.cityblock([int(food.get("y")), int(food.get("x"))], [int(head_pos.get("y")), int(head_pos.get("x"))])
        if (dist < min_dist):
            min_dist = dist
            nearest_food_loc = food
    return nearest_food_loc

def find_next_step_in_route(current_pos, dest_pos, data):
    adj_points = get_all_4_points(current_pos)
    options = check_for_walls(adj_points, data)
    options = check_for_other_snakes(options, data)
    options = check_own_body(options, data)
    distances = []
    for pt in options:
        distances.append(distance.cityblock([int(pt.get("x")), int(pt.get("y"))], [int(dest_pos.get("x")), int(dest_pos.get("y"))]))
    index_of_min = numpy.argmin(distances)
    return options[index_of_min]

def get_name_of_direction(dest, src):
    if (int(dest.get('x')) < int(src.get('x'))):
        return 'left'
    elif (int(dest.get('x')) > int(src.get('x'))):
        return 'right'
    elif (int(dest.get('y') < src.get('y'))):
        return 'up'
    else:
        return 'down'

def flood_fill(data):
    h = data['board']['height']
    w = data['board']['width']
    board = numpy.zeros(h*w).reshape((h,w))

    # populate the board
    """
    0 = empty node
    -1 = food
    2 = myself
    3 = other snake
    """
    for f in data['board']['food']:
        board[f.get("y")][f.get("x")] = -1
    for snake in data['board']['snakes']:
        for snake_body in snake['body']:
            board[snake_body.get("y")][snake_body.get("x")] = 3
    for my_body in data['you']['body']:
        board[my_body.get("y")][my_body.get("x")] = 2

    node = data['you']['body'][0] #head position
    adj_nodes = {"left": {"x": node.get("x") -1, "y": node.get("y")},
                "right": {"x": node.get("x") + 1, "y": node.get("y")},
                "up": {"x": node.get("x"), "y": node.get("y") - 1},
                "down": {"x": node.get("x"), "y": node.get("y") + 1}}
    examined_nodes = [] # keep track of nodes that have already been flood filled
    # space_counts is dictionary to count number of valid positions in particular direction
    space_counts = {"left": 0, "right": 0, "up": 0, "down": 0}
    # buffet_score is dictionary to count number of food items in particular direction
    #buffet_score = {"left": 0, "right": 0, "up": 0, "down": 0}
    optimal_node = None
    if (node.get("x") - 1 >= 0):
        left, buffet, examined_nodes = sub_flood_fill({"x": node.get("x") -1, "y": node.get("y")}, board, examined_nodes, 0, 0)
        space_counts['left'] = left
       # buffet_score['left'] = buffet
    if (node.get("x") + 1 < w):
        right, buffet, examined_nodes = sub_flood_fill({"x": node.get("x") + 1, "y": node.get("y")}, board, examined_nodes, 0, 0)
        space_counts['right'] = right
        #buffet_score['right'] = buffet
    if (node.get("y") - 1 >= 0):
        up, buffet, examined_nodes = sub_flood_fill({"x": node.get("x"), "y": node.get("y") - 1}, board, examined_nodes, 0, 0)
        space_counts['up'] = up
        #buffet_score['up'] = buffet
    if (node.get("y") + 1 < h):
        down, buffet, examined_nodes = sub_flood_fill({"x": node.get("x"), "y": node.get("y") + 1}, board, examined_nodes, 0, 0)
        space_counts['down'] = down
        #buffet_score['down'] = buffet

    """
    # compute ratio of food:space
    for k in space_counts.iterkeys():
        if space_counts.get(k) > 0:
            space_counts[k] = float(buffet_score.get(k) / space_counts.get(k))

    # find highest ratio of food:space
    best_dir = max(space_counts, key=lambda key: space_counts[key])
    print("best direction: " + best_dir + ", " + str(space_counts.get(best_dir)))
    optimal_node = adj_nodes.get(best_dir)
    """
    best_dir = max(space_counts, key=lambda key: space_counts[key])
    print("best direction: " + best_dir)
    optimal_node = adj_nodes.get(best_dir)

    return optimal_node


def sub_flood_fill(node, board, examined_nodes, count, buffet_score):
    if ( (board[node.get("y")][node.get("x")] < 1) and (node not in examined_nodes)):
        count += 1
        examined_nodes.append(node)
        if (board[node.get("y")][node.get("x")] == -1):
            buffet_score += 1
        # left
        if (node.get("x") - 1 >= 0):
            count, buffet_score, examined_nodes = sub_flood_fill({"x": node.get("x") -1, "y": node.get("y")}, board, examined_nodes, count, buffet_score)
        # right
        if (node.get("x") + 1 < board.shape[1]):
            count, buffet_score, examined_nodes = sub_flood_fill({"x": node.get("x") + 1, "y": node.get("y")}, board, examined_nodes, count, buffet_score)
        # up
        if (node.get("y") - 1 >= 0):
            count, buffet_score, examined_nodes = sub_flood_fill({"x": node.get("x"), "y": node.get("y") - 1}, board, examined_nodes, count, buffet_score)
        # down
        if (node.get("y") + 1 < board.shape[0]):
            count, buffet_score, examined_nodes = sub_flood_fill({"x": node.get("x"), "y": node.get("y") + 1}, board, examined_nodes, count, buffet_score)
    #print("count: " + str(count) + ", examined_nodes: " + str(examined_nodes))
    return count, buffet_score, examined_nodes

def get_string_direction(dest, head_pos):
    if (dest.get("x") < head_pos.get("x")):
        return 'left'
    elif (dest.get("x") > head_pos.get("x")):
        return 'right'
    elif (dest.get("y") < head_pos.get("y")):
        return 'up'
    else:
        return 'down'

# if head of another snake is 2 points away in any cityblock direction,
# this function returns list of node(s) to go towards
# if this snake is bigger than the enemy snake, it will attempt to collide 
# with the smaller snake in order to kill it
# if this snake is the same size or smaller than the enemy snake, it will
# attempt to avoid a collision
# functions returns None if snake is not in a head-on collision situation
def check_for_head_on_collision(data):
    head_pos = data['you']['body'][0]
    head_pos_vector = [head_pos.get("y"), head_pos.get("x")]

    for snake in data['board']['snakes']:
        head_of_enemy_snake = snake['body'][0]
        if head_of_enemy_snake == head_pos:
            # it's not an enemy, it's me
            continue
        else:
            head_of_enemy_vector = [head_of_enemy_snake.get("y"), head_of_enemy_snake.get("x")]
            if ( distance.cityblock(head_pos_vector, head_of_enemy_vector) == 2 ):
                # determine snake lengths
                my_length = len(data['you']['body'])
                enemy_length = len(snake['body'])
                
                # determine if straight-on or corner
                if (head_pos.get("x") == head_of_enemy_snake.get("x")):
                    # it's straight on vertically
                    return find_escape_points(data, head_pos, head_of_enemy_snake)
                elif (head_pos.get("y") == head_of_enemy_snake.get("y")):
                    return find_escape_points(data, head_pos, head_of_enemy_snake)
                else:
                    return find_escape_points(data, head_pos, head_of_enemy_snake)
    return None

def find_escape_points(data, head_pos, head_of_enemy_snake):
    # if the potential HOC is straight horizontally
    if (head_pos.get("y") == head_of_enemy_snake.get("y")):
        up_pt = get_point_upward(head_pos)
        down_pt = get_point_downward(head_pos)
        options = [up_pt, down_pt]
        #options = check_for_walls(options, data)
        options = check_for_other_snakes(options, data)
        options = check_own_body(options, data)
        return options
    # else if the potential HOC is straight vertically
    elif (head_pos.get("x") == head_of_enemy_snake.get("x")):
        left_pt = get_point_to_left(head_pos)
        right_pt = get_point_to_right(head_pos)
        options = [left_pt, right_pt]
        #options = check_for_walls(options, data)
        options = check_for_other_snakes(options, data)
        options = check_own_body(options, data)
        return options
    # else the potential HOC is on a corner
    else:
        all_adj_points = get_all_4_points(head_pos)
        adj_points_to_head = get_all_4_points(head_of_enemy_snake)
        #options = check_for_walls(all_adj_points, data)
        options = check_for_other_snakes(options, data)
        options = check_own_body(options, data)
        for pt in options:
            if pt in adj_points_to_head:
                options.remove(pt)
        return options

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '3440'),
        debug=os.getenv('DEBUG', True)
    )
