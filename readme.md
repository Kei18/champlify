Charmplify
---
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

[Char]acter pattern formation generator powered by Am[plify].

It is written in Python(3.8) with [pipenv](https://github.com/pypa/pipenv) and tested on MacOS 10.15.
This repository is for the [Fixstars Amplify Hackathon](https://amplify.fixstars.com/hackathon00).

_This is one application of unlabeled-MAPF._

## Demo
![demo](/material/amplify.gif)

## Requirement
- [pipenv](https://github.com/pypa/pipenv)
- access token to amplify library ([link](https://amplify.fixstars.com/user/token))

## Install
First, clone this repo.
```sh
https://github.com/Kei18/champlify.git
```

Next, register your access token to `.env` file.
```sh
echo TOKEN={YOUR_AMPLIFY_TOKEN} > .env
```

Finally, create the environment.
```sh
pipenv sync
```

## Usage
```sh
pipenv run app
```

Type [a-z] with your keyboard, then the formation of agents will be changed.

## Explanation
See [slides.pdf](/material/slides.pdf)

## Notes
- map format: [Pathfinding Benchmarks](https://movingai.com/benchmarks/)
- instance format: see [example.txt](/instance/example.txt)
- Of course, this repo is for *hackathon* (i.e., please do not blame me if bugs exist...)

## Licence
This software is released under the MIT License, see [LICENCE.txt](LICENCE.txt).

## Author
[Keisuke Okumura](https://kei18.github.io) is a Ph.D. student at the Tokyo Institute of Technology, interested in controlling multiple moving agents.
