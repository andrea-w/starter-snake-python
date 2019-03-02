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

    obstacleFlag = {
        'up': checkForObstacle(data, head_pos['x'], head_pos['y'] - 1),
        'right': checkForObstacle(data, head_pos['x'] + 1, head_pos['y']),
        'down': checkForObstacle(data, head_pos['x'], head_pos['y'] + 1),
        'left': checkForObstacle(data, head_pos['x'] - 1, head_pos['y'])
    }
    direction = 'right'

    if not obstacleFlag['up']:
        direction = 'up'
    if not obstacleFlag['right']:
        direction = 'right'
    if not obstacleFlag['left']:
        direction = 'left'
    if not obstacleFlag['down']:
        direction = 'down'

    print(json.dumps(data, indent=4))

    directions = ['up', 'down', 'left', 'right']

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

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
