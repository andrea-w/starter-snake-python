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

    #flood_fill(data)

    if (data["you"]["health"] < 20):
        my_head = data["you"]["body"]
        destination = find_food(my_head,data)
        direction = issue_direction(my_head, destination, data)

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
    """
    for y in range(h):
        for x in range(w):
            #print(current_arena[x][y], end=' ')
        print('\n')
    """        
    return

def find_food(my_head, data):
    head_x = my_head["x"]
    head_y = my_head["y"]

    food_distances = []

    food_items = data["board"]["food"]
    for f in food_items:
        f_x = food["x"]
        f_y = food["y"]
        food_distances.append(distance.cityblock([head_x, head_y],[f_x, f_y]))

    for i in food_distances:
        if i == min(food_distances):
            target_food_index = i

    target_food = data["board"]["food"][target_food_index]
    print("target_food")
    print(target_food)
    return (target_food["x"], target_food["y"])

def issue_direction(current_pos, destination, data):
    board = get_map_of_board(data)

    # want to move right
    if (current_pos.get("x") < destination.get("x")):
        if (board[current_pos.get("y"),current_pos.get("x")+1] == 0) or (board[current_pos.get("y"),current_pos.get("x")+1] == 3):
            return 'right'
    # want to move left
    if (current_pos.get("x") > destination.get("x")):
        if (board[current_pos.get("y"), current_post.get("x")-1] == 0) or (board[current_pos.get("y"), current_post.get("x")-1] == 3):
            return 'left'
    # want to move up
    if (current_pos.get("y") > destination.get("y")):
        if (board[current_pos.get("y")-1, current_pos.get("x")] == 0) or (board[current_pos.get("y")-1, current_pos.get("x")] == 3):
            return 'up'
    # want to move down
    if (current_pos.get("y") < destination.get("y")):
        if (board[current_pos.get("y")+1, current_pos.get("y")] == 0) or (board[current_pos.get("y")+1, current_pos.get("y")] == 3):
            return 'down' 
       
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
