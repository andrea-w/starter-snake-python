from __future__ import print_function

import json
import os
import random
import bottle


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

    color="#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    flood_fill(data)

    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)

    return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

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
        port=os.getenv('PORT', '18080'),
        debug=os.getenv('DEBUG', True)
    )
