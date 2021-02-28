app
---
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
This repository is for the [Fixstars Amplify Hackathon](https://amplify.fixstars.com/hackathon00).

## Demo

## Description

## Requirement
- [pipenv](https://github.com/pypa/pipenv)
- access token to amplify library ([link](https://amplify.fixstars.com/user/token))

## Install
First, clone this repo.
```sh
git clone
```

Next, register your access token to `.env` file.
```sh
echo TOKEN={YOUR_AMPLIFY_TOKEN} > .env
```

Finally, create the environment.
```sh
sudo pipenv sync
```

## Usage
```sh
pipenv run app
```

## Notes
- map format: [Pathfinding Benchmarks](https://movingai.com/benchmarks/)
- Of course, this repo is for *hackathon* (i.e., please do not blame me if bugs exist, I actually skip tests)

## Licence
This software is released under the MIT License, see [LICENCE.txt](LICENCE.txt).

## Author
[Keisuke Okumura](https://kei18.github.io) is a Ph.D. student at the Tokyo Institute of Technology, interested in controlling multiple moving agents.
