# CheeseChase

*CheeseChase* is a fun, lightweight arcade game inspired by Pac-Man, built with *Python* and *Pygame*.  
Play as Jerry the Mouse, collect cheese pieces, and avoid the cats - unless you find the special cheese that turns the tables!

---

## Project structure 

Overview:
```bash
artifact
├── CheeseChase/            # main package 
│   ├── __init__.py         # python package marker
│   ├── __main__.py         # application entry point
│   ├── model/              # Game modelling
│   ├── view/               # Sprites and rendering
│   ├── controller/         # Game control and flow
│   └── resources/          
├── test/                   # unittests - not all listed here
│   ├── test_game_controller.py 
│   ├── test_mouse.py         
│   ├── ...  
├── .github/                # configuration of GitHub CI
│   └── workflows/          # configuration of GitHub Workflows
│       ├── check.yml       # runs tests on multiple OS and versions of Python
│       └── deploy.yml      # if check succeeds, and the current branch is one of {main, master}, triggers automatic releas on PyPi
├── MANIFEST.in             # file stating what to include/exclude in releases 
├── LICENSE                 # license file (Apache 2.0)
├── pyproject.toml          # declares build dependencies
├── renovate.json           # configuration of Renovate bot, for automatic dependency updates
├── requirements-dev.txt    # declares development dependencies
├── requirements.txt        # declares runtime dependencies
├── setup.py                # configuration of the package to be released on Pypi
└── CHANGELOG.md            # history of project's changes for each version
```

## How to install the game

You can install *CheeseChase* either from *PyPI* or directly from *GitHub*.

### From PyPI

```bash
pip install CheeseChase
```

If you’ve already installed CheeseChase and a new version has been released, update it with:

```bash
pip install --upgrade CheeseChase
```

### From GitHub

#### Clone the repository locally: 

```bash
git clone https://github.com/unibo-dtm-se-2425-CheeseChase/artifact.git
```     
#### Go into artifact:
```bash
cd artifact
```
#### Install the required dependencies:
```bash
pip install -r requirements.txt
```
For developmental purposes use:
```bash
pip install -r requirements-dev.txt
```
## How to launch the application:

```bash
python -m CheeseChase
```
This will execute the file CheeseChase/__main__.py

## Controls

| Key / Button | Action |
|--------------|--------|
| ⬆ *Arrow Up*    | Move Up |
| ⬇ *Arrow Down*  | Move Down |
| ⬅ *Arrow Left*  | Move Left |
| ➡ *Arrow Right* | Move Right |
| *Spacebar*       | Pause / Resume game |
| *X (Close Button)* | Exit the game |

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Authors

- **Francesca Folli**  – [francesca-folli](https://github.com/frafo227295)
- **Gaia Bellachioma** – [gaia-bellachioma](https://github.com/gaia-bellachioma)

## License

[Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html)