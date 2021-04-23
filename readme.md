Champlify
---
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

[Cha]racter pattern formation generator powered by A[mplify] with [toio](https://toio.io/) execution.

It is written in Python(3.8) with [pipenv](https://github.com/pypa/pipenv), Node.js with [yarn](https://yarnpkg.com/) build, and tested on MacOS 10.15.
The GUI uses [Eel](https://github.com/samuelhwilliams/Eel).
This repository is for the [Fixstars Amplify Hackathon](https://amplify.fixstars.com/hackathon00).

_This is one application of unlabeled-MAPF._

## Demo
![demo](/material/toio.gif)

## Requirement
- [pipenv](https://github.com/pypa/pipenv)
- [yarn](https://yarnpkg.com/)
- [6 toio robots](https://toio.io/)
- access token to amplify library ([link](https://amplify.fixstars.com/user/token))

## Install
1. Cone this repo.
```sh
git clone https://github.com/Kei18/champlify.git
cd champlify
```

2. Register your access token to `.env` file.
```sh
echo TOKEN={YOUR_AMPLIFY_TOKEN} > .env
```

3. Create the python environment.
```sh
pipenv sync
```

4. Install & build toio execution system.
```sh
cd toio-exec
yarn install
yarn build
cd ..
```

## Usage
0. (You may have to adjust coordinates in `toio-exec/map/3x4.json`)
1. Switch on the robots
2. Run
```sh
bash ./run.sh
```
3. After connecting to 6 robots, set the robots to initial positions as follows
```
0, 1, 2
3, 4, 5
```
4. Type [f, j, l, o, t, y] with your keyboard, then the formation of agents/robots will be changed.

## Explanation
See [slides.pdf](/material/slides.pdf)

## Notes
- map format: [Pathfinding Benchmarks](https://movingai.com/benchmarks/)
- Of course, this repo is for *hackathon* (i.e., please do not blame me if bugs exist...)
- `toio-exec` is forked from [toio.js](https://github.com/toio/toio.js). To make the repo private temporarily, I duplicate the original repo

## Licence
This software is released under the MIT License, see [LICENCE.txt](LICENCE.txt).

## Author
[Keisuke Okumura](https://kei18.github.io) is a Ph.D. student at the Tokyo Institute of Technology, interested in controlling multiple moving agents.
