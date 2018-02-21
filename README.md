# BattleSnake 2018

This is a Snake entry for the [BattleSnake](http://battlesnake.io) programming competition in Victoria BC, written in Python.

Forked from the [Python starter snake](https://github.com/sendwithus/battlesnake-python) provided by [sendwithus](https://www.sendwithus.com).

This AI client uses the [bottle web framework](http://bottlepy.org/docs/dev/index.html) to serve requests and the [gunicorn web server](http://gunicorn.org/) for running bottle on [Heroku](https://heroku.com). Dependencies are listed in [requirements.txt](requirements.txt).

## State of AI

2018/02/17 - Will get an optimal direction from a* for the given target, and then look ahead at that move and the other possible moves to evaluate which is best. It also now tracks the length of other snakes and will eat to try to be largest. Now will properly prioritize head neighbor locations of snakes that are smaller than it when it is near so it can try to eat them. Working on agressive hunting behaviour when it is the largest snake.

2018/02/13 - Switches between following own tail to kill time if health is above threshold and seeking nearest food if health is below threshold.

2018/02/13 - Will seek closest food. Generally will avoid snake bodies and outer wall on each move.

2018/02/10 - Currently runs in a circle. No pathfinding or avoidance behaviour.

## Running the Snake Locally

1) [Fork this repo](https://github.com/tyrelh/battlesnake-python/fork).

2) Clone repo to your development environment:
```
git clone git@github.com:username/battlesnake-python.git
```

3) Install dependencies using [pip](https://pip.pypa.io/en/latest/installing.html):
```
pip install -r requirements.txt
```

4) Run local server:
```
python app/main.py
```

5) Test client in your browser: [http://localhost:8080](http://localhost:8080).

## Deploying to Heroku

1) Create a new Heroku app:
```
heroku create [APP_NAME]
```

2) Deploy code to Heroku servers:
```
git push heroku master
```

3) Open Heroku app in browser:
```
heroku open
```
or visit [http://APP_NAME.herokuapp.com](http://APP_NAME.herokuapp.com).

4) View server logs with the `heroku logs` command:
```
heroku logs --tail
```

## Questions?

Contact me [tyrel.hiebert@gmail.com](mailto:tyrel.hiebert@gmail.com) or contact [sendwithus](https://www.sendwithus.com) [battlesnake@sendwithus.com](mailto:battlesnake@sendwithus.com), [@send_with_us](http://twitter.com/send_with_us).
