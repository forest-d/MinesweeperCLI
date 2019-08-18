import os
import click
import random
from dataclasses import dataclass


TILE_TYPES = {
    'unknown': '?',
    'empty': ' ',
    'mine': '!',
}

DIFFICULTY_MAPPING = {
    'easy': 0.1,
    'medium': 0.2,
    'hard': 0.3,
    'insane': 0.5
}


@dataclass
class Tile:
    tile_type: str
    revealed: bool = False

    x: int = None
    y: int = None

    n_adjacent_mines: int = 0

    def __repr__(self):
        if self.n_adjacent_mines > 0:
            return str(self.n_adjacent_mines)
        if self.revealed:
            return TILE_TYPES[self.tile_type]
        else:
            return TILE_TYPES['unknown']


@dataclass
class MinesweeperBoard:
    size: int
    difficulty: str

    # Populated in __post_init__
    board: list = None
    n_total_mines: int = 0

    def __post_init__(self):
        # Create board
        self.board = self.board_init(size=self.size)

        # Figure out how many mines to lay
        self.n_total_mines = self.set_number_of_mines()

    def populate_board_with_mines(self):
        # Generate x, y coords * n_total_mines
        mine_x_coords = [random.randint(0, self.size - 1) for x in range(self.n_total_mines)]
        mine_y_coords = [random.randint(0, self.size - 1) for x in range(self.n_total_mines)]
        coords = list(set(zip(mine_x_coords, mine_y_coords)))
        # print(f"Mine coordinates: {coords}")
        self.n_total_mines = len(coords)

        # Set the tile type to 'mine' for each coordinate
        for x, y in coords:
            tile = self.get_tile(x, y)
            tile.tile_type = 'mine'

    def check_if_mine(self, tile: Tile):
        if tile.tile_type == 'mine':
            tile.revealed = True
            # Game over
            print(f"{tile.x},{tile.y} is a mine! You lose!")
            for row in self.board:
                for tile in row:
                    tile.revealed = True
            self.display_board()
            return False
        return True

    def evaluate_tile(self, tile: Tile) -> bool:
        # Get adjacent tiles
        x, y = tile.x, tile.y

        """
        Need to grab these tiles (if they exist)
        x-1,y-1     x-1,y       x-1,y+1
        x,y-1       x,y         x,y+1
        x+1,y-1     x+1,y       x+1,y+1
        """

        # List of adjacent tiles
        adjacent_tiles = [
            self.get_tile(x - 1, y - 1),
            self.get_tile(x - 1, y),
            self.get_tile(x - 1, y+1),
            self.get_tile(x, y - 1),
            self.get_tile(x, y + 1),
            self.get_tile(x + 1, y - 1),
            self.get_tile(x + 1, y),
            self.get_tile(x + 1, y + 1),
        ]
        # Get rid of None tiles and tiles that have already been revealed
        adjacent_tiles = [x for x in adjacent_tiles if x is not None and x.revealed is False]

        # Check to see if any of the adjacent tiles are mines
        mine_counter = 0
        for t in adjacent_tiles:
            if t.tile_type == 'mine':
                mine_counter += 1

        # If this tile is surrounded by any mines, we need to store how many, reveal it and stop evaluating
        if mine_counter > 0:
            tile.revealed = True
            tile.tile_type = 'empty'
            tile.n_adjacent_mines = mine_counter
            return False

        # If the tile is not surrounded by any mines, it's a blank and we can call evaluate_tile
        # on each of the surrounding tiles
        tile.revealed = True
        tile.tile_type = 'empty'
        tile.n_adjacent_mines = mine_counter  # n_adjacent_mines is 0 in this case

        # Now we need to call this method on each of the surrounding tiles
        for t in adjacent_tiles:
            self.evaluate_tile(t)

    def get_tile(self, x, y):
        if x < 0 or x > self.size:
            return None
        if y < 0 or y > self.size:
            return None

        try:
            tile = self.board[x][y]
        except IndexError:
            return None
        return tile

    def display_board(self):
        col_labels = [str(x).ljust(2) for x in list(range(self.size))]
        col_labels = " ".join(col_labels)
        header = f"\t {col_labels}"
        print(header)
        print("\t " + "-" * (len(header) - 2))
        for i, row in enumerate(self.board):
            row = [str(x) + " " for x in row]
            row.insert(0, f"{str(i)}|\t")
            print(" ".join(row))

    def set_number_of_mines(self):
        # Given n elements, sets y of them to mines according to proportion defined by difficulty variable
        n_mines = int((self.size * self.size) * DIFFICULTY_MAPPING[self.difficulty])
        return n_mines

    @staticmethod
    def board_init(size: int) -> [list]:
        board = []
        for i in range(size):
            board.append([Tile(tile_type='empty', revealed=False, x=i, y=y) for y in range(size)])
        return board


@click.command(help="CLI Minesweeper")
@click.option('-s', '--size',
              default=15,
              type=click.INT,
              prompt="Enter board size:",
              help="Enter an integer to set the size of your board. e.g. '8' will generate a 8x8 board.")
@click.option('-d', '--difficulty',
              type=click.Choice(['easy', 'medium', 'hard', 'insane']),
              prompt="Enter difficulty:",
              default='easy',
              help="Choose between [easy, medium, hard, insane] difficulties.")
def minesweeper(size: int, difficulty: str):
    board = MinesweeperBoard(size=size, difficulty=difficulty)
    board.populate_board_with_mines()
    print(f"Planted {board.n_total_mines} mines on the board")

    keep_playing = True
    while keep_playing:
        os.system('cls' if os.name == 'nt' else 'clear')  # Inadequate hack to clear the screen
        board.display_board()
        x = int(input("Enter row: "))
        y = int(input("Enter column: "))
        tile = board.get_tile(x, y)
        if tile.revealed is True:
            print("Error: please select an unknown tile")
            continue
        tile.revealed = True

        # See if we hit a mine or not - if so, the game will end
        keep_playing = board.check_if_mine(tile)

        # Evaluate the tile if it wasn't a mine
        board.evaluate_tile(tile)


if __name__ == "__main__":
    minesweeper()
