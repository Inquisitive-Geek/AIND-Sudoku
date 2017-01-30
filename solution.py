assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Local copies of the variables are defined here as the unit test code keeps giving error

    # Find all instances of naked twins
    # naked_twins_instances = {}
    naked_twins_instances = []
    # For each unit, first check if a box contains 2 possible values
    for unit in unit_list:
        for box in unit:
            if len(values[box]) == 2:
                # When such a box is found, search the unit for a box with same combination of values
                for box_dup in unit:
                    # Obviously, ignore the same box and don't create a combination like {A1:A2,A2:A1}
                    if values[box] == values[box_dup] and box != box_dup:
#                    if values[box] == values[box_dup] and box != box_dup and \
#                                    box_dup not in naked_twins_instances.keys():
                        # Append the found naked twin match to a list
                        # naked_twins_instances[box] = box_dup
                        naked_twins_instances.append((box,box_dup))
                        # When such a match is found, exit the loop
                        break
    # Eliminate the naked twins as possibilities for their peers
    # The naked twins are to be eliminated from those units which have the twins
    # for naked_twins in naked_twins_instances.keys():
    for naked_twins, naked_twins_dup in naked_twins_instances:
        # for box in peers[naked_twins]:
        for unit in units[naked_twins]:
            if naked_twins_dup in unit:
                for box in unit:
                    # Don't consider the naked twin for removal of characters
                    # if box != naked_twins_instances[naked_twins]:
                    if box != naked_twins_dup:
                        # Check if any of the characters of the naked twin are contained in any of the units' boxes -
                        # The units chosen are such that they should contain both the naked twins
                        if len(values[box]) > 2 and values[box] != values[naked_twins]:
                            if any(s in values[box] for s in values[naked_twins]):
                                # Remove the naked twins characters from each of the peers
                                values[box] = values[box].replace(values[naked_twins][0],'')
                                values[box] = values[box].replace(values[naked_twins][1],'')
    return values

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    for unit in unit_list:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        # Naked Twins Implementation
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion for solving the remaining Sudokus
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Convert the grid string to a grid dictionary representation
    grid_dict = grid_values(grid)
    return search(grid_dict)

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows,cols)
row_units = [cross(r,cols) for r in rows]
column_units = [cross(rows,c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Diagonal Sudoku constraint
diagonal_units = []
# The diagonal units are created which should refer to the diagonal elements - eg. A1, B2, C3.. and A9, B8, ..
diagonal_units.append([cross(rows[i], cols[i])[0] for i in range(0, len(rows))])
diagonal_units.append([cross(rows[i], cols[len(cols)-i-1])[0] for i in range(0, len(rows))])
# Update unit list with diagonal units
unit_list = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
