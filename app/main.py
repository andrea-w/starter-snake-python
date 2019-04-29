import json
import os
import random
import bottle
import scipy

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

    color = "#00FF99"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)
    direction = 'right'

    head_pos = get_position_of_my_head(data)
    adj_points = get_all_4_points(head_pos)
    no_walls = check_for_walls(adj_points, data)
    avoid_me = check_own_body(no_walls, data)
    avoid_others = check_for_other_snakes(avoid_me, data)

    next_to_food = check_if_next_to_food(avoid_others, data)
    if (next_to_food != False):
        del avoid_others[:]
        avoid_others.append(next_to_food)

    possible_directions = []
    for point in avoid_others:
        possible_directions.append(get_name_of_direction(point,head_pos))

    return move_response(random.choice(possible_directions))


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
        dist = scipy.spatial.distance.cityblock(food, head_pos)
        if (dist < min_dist):
            min_dist = dist
            nearest_food_loc = food
    return nearest_food_loc

def get_name_of_direction(dest, src):
    if (int(dest.get('x')) < int(src.get('x'))):
        return 'left'
    elif (int(dest.get('x')) > int(src.get('x'))):
        return 'right'
    elif (int(dest.get('y') < src.get('y'))):
        return 'up'
    else:
        return 'down'


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '3200'),
        debug=os.getenv('DEBUG', True)
    )
