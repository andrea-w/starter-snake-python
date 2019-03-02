# from __future__ import print_function

import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

def checkForObstacle(data, x, y):

    walls = {
        'up': 0,
        'right': data['board']['width']-1,
        'down': data['board']['height']-1,
        'left': 0
    }

    for snake in data['board']['snakes']:
        for piece in snake['body']:
            if piece['x'] == x and piece['y'] == y:
                print("snake found at ", x, y)
                return True

    if walls["up"] == y or walls["down"] == y or walls["left"] == x or walls["right"] == x:
        print("wall found at ", x, y)
        return True

    return False

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
    such as Heroku,  from sleeping the application instance.
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

    food_initial = data["board"]["food"]

    print(json.dumps(data, indent=4))

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    head_pos = {
        'x': data['you']['body'][0]['x'], 
        'y': data['you']['body'][0]['y']
    }

    # walls = {
    #     'up': 0,
    #     'right': data['board']['width']-1,
    #     'down': data['board']['height']-1,
    #     'left': 0
    # }

    # wallFlag = {
    #     'up': head_pos['y'] <= walls['up'],
    #     'right': head_pos['x'] >= walls['right'],
    #     'down': head_pos['y'] >= walls['down'],
    #     'left': head_pos['x'] <= walls['left']
    # }

    obstacleFlag = {
        'up': checkForObstacle(data, head_pos['x'], head_pos['y'] - 1),
        'right': checkForObstacle(data, head_pos['x'] + 1, head_pos['y']),
        'down': checkForObstacle(data, head_pos['x'], head_pos['y'] + 1),
        'left': checkForObstacle(data, head_pos['x'] - 1, head_pos['y'])
    }
    direction = 'right'

    # if all(value == False for value in wallFlag.values()):
    #     direction = "right"
    #     print("NOT NEAR ANY WALLS")

    # if wallFlag['up'] or wallFlag['down']:
    #     if wallFlag['right'] and not bodyFlag['left']:
    #         direction = 'left'
    #     if wallFlag['left'] and not bodyFlag['right']:
    #         direction = 'right'

    # elif wallFlag['right'] or wallFlag['left']:
    #     direction = "up"
    #     if wallFlag['up'] and not bodyFlag['down']:
    #         direction = 'down'
    #     if wallFlag['down']and not bodyFlag['up']:
    #         direction = 'up'

    if not obstacleFlag['up']:
        direction = 'up'
    if not obstacleFlag['right']:
        direction = 'right'
    if not obstacleFlag['left']:
        direction = 'left'
    if not obstacleFlag['down']:
        direction = 'down'

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data, indent=4))

    flood_fill(data)

    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)

    # print("WALL FLAG = " + str(wallFlag))
    # print("DIRECTION = " + direction)

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data, indent=4))

    return end_response()

# returns 2D matrix of board
# 0 indicates empty space
# 1 indicates our snake body
# 2 indicates food
# 3 indicates enemy snake body
def get_map_of_board(data):
    w = data["board"]["width"]
    h = data["board"]["height"]
    current_arena = [[0 for x in range(w)] for y in range(h)]
    enemy_snakes = [data["board"]["snakes"]] 

    # find own body
    me = data["you"]["body"]
    for pos in me:
        current_arena[pos["y"]][pos["x"]] = 1

    # find food
    food = data["board"]["food"]
    for i in food:
        current_arena[i["y"]][i["x"]] = 2

    # find enemy snakes
    for snake in enemy_snakes:
        body = snake[0]["body"]
        for pos in body:
            current_arena[pos["y"]][pos["x"]] = 3

    print_board(w,h,current_arena)
    return current_arena

def print_board(w,h,current_arena):
    for y in range(h):
        for x in range(w):
            print(current_arena[x][y], end=' ')
        print('\n')    
        
def flood_fill(data):
    get_map_of_board(data)
     

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
