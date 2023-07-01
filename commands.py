# / IMPORTS \
import shlex, json, time, sys, os, discord, hashlib, re, textwrap, datetime     # External
import pastee, database, secret                                                 # Internal

# "From" imports
from discord import Member, Message, TextChannel  
from database import Database, ElementStat
from collections.abc import Iterable
from typing import Callable
from io import TextIOWrapper

# true rivals, rune factory frontier - autumn theme
# TODO: implement typedyno data

# / GLOBALS & CONSTANTS \

# Load all jumps
with open("data/jumps/jump_data.json") as f:
    JUMP_DATA = json.load(f)

# Newline for some f-strings
NL = "\n"

# Discord input
PREFIX = '!'

MAX_JUMP_NAME_LENGTH = 100
CHANNEL_TYPES_FILE = "data/channels/channel_types.json"

# Attributes users can enter that mean the same thing (e.g. input "n" means "name")
USER_ATTRIBUTES = (("name",     "n"),
                   ("location", "kingdom", "loc", "k"),
                   ("diff",     "difficulty", "d"),
                   ("tier",     "t"),
                   ("type",     "ty"),
                   ("finder",   "find", "founder", "found", "f"),
                   ("taser",    "tased", "tas"),
                   ("prover",   "proved", "p"),
                   ("server",   "s"),
                   ("extra",    "desc", "description", "ex", "e", "info", "i", "rules", "rule", "r"),
                   ("links",    "link", "l"))

# > First element of every USER_ATTRIBUTES tuple
# > USER_ATTRIBUTES get converted to these
# > Actual ATTRIBUTES used in the code and the jump_data
ATTRIBUTES = tuple(tpl[0] if tpl else None for tpl in USER_ATTRIBUTES)

PERSONAL_ATTRIBUTES = ("proof", "time_given")

ATTRIBUTES_LISTABLE = ('location', 'type', 'finder', 'taser', 'prover', 'extra', 'links')

ATTRIBUTES_REQUIRED = ('name', 'location', 'diff', 'server', 'links')

# Servers users can enter that mean the same thing (e.g input "main" -> "SMO Trickjump Server")
USER_SERVERS = (("SMO Trickjumping Server", "Main Trickjumping Server", "Main Trickjump Server", "Main Server"),
                ("Database", "The Trickjump Database", "Database Server", "DB"),
                ("Extra Elite Server", "ees"),
                ("Obscure Server", "os"),
                ("2P Server", "2s", "2ps"),
                ("Community Server",),
                ("Collection Server",),
                ("Yellow Dram Server", "yds", "ys", "ys"),
                ("Sky Dram Server", "sds", "sd")
                )


# Special orders when sorting, instead of just sorting by name
# +------------------------+

LOCATION_ORDER = ('Mushroom Kingdom', 'Cap Kingdom', 'Cascade Kingdom',
             'Sand Kingdom', 'Lake Kingdom', 'Wooded Kingdom', 'Cloud Kingdom',
             'Lost Kingdom', 'Metro Kingdom', 'Snow Kingdom',
             'Seaside Kingdom', 'Luncheon Kingdom', 'Ruined Kingdom',
             "Bowser's Kingdom", 'Moon Kingdom', 'Dark Side', 'Darker Side',
             'Odyssey')

TIER_ORDER = "Practice Tier", "Beginner", "Intermediate", "Advanced", "Expert", "Master", "Low Elite", "Mid Elite", "High Elite", "Insanity Elite", "God Tier", "Hell Tier", "Unproven"

# 0/10, 0.5/10, 1/10, ... , 9.5/10, 10/10, Low Elite, ... , Hell Tier, Unproven
DIFF_ORDER = tuple([str(int(x / 2)) + "/10" if x % 2 == 0 else f"{x/2}/10" for x in range(0, 21)] + list(TIER_ORDER[6:]))

# +------------------------+



# / COMMANDS \
# > Functions with no leading "_" are the discord command's functions

def _join_embed(iterable: Iterable[str]) -> str:
    return f"`{'`, `'.join(iterable)}`"

BACKUP_NAME_EXTENSION = "_backup"
JSON_EXT = ".json"
def _write_to_json_safely(main_file_path: str, data, indent: int = 4) -> None:
    """
    First writes data to a backup file, then to the main file given. If the program were to interrupt in any case,
    the data will always be recoverable!
    """
    with open(main_file_path.removesuffix(JSON_EXT) + BACKUP_NAME_EXTENSION + JSON_EXT, "w") as bf:
        json.dump(data, bf, indent=indent if indent else 0)
    with open(main_file_path, "w") as of:
        json.dump(data, of, indent=indent if indent else 0)


def _fix_corrupted_json(path_json_to_fix: str) -> str:
    """
    Fixes the file given via its backup file, created with the function ``_write_to_json_safely``.
    """
    with open(path_json_to_fix.removesuffix(JSON_EXT) + BACKUP_NAME_EXTENSION + JSON_EXT) as bf:
        backup = json.load(bf)
    with open(path_json_to_fix, "w") as cf:
        json.dump(backup, cf)

def _read_from_json_safely(main_file_path: str):
    """
    Loads the data from the file given, but calls ``_fix_corruputed_json`` if file were to be corrupted,
    to fix the file again via its backup file.
    """
    with open(main_file_path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            _fix_corrupted_json(main_file_path)
            return json.load(f)

def _time_to_str() -> str:
    """
    Turns the exact time at function call into a neat string of date and time according to the UTC timezone.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S (UTC)", time.gmtime())


USER_JUMP_DATA_DIR = "data/users/jumps/"
_get_user_jump_data_path = lambda id: f"{USER_JUMP_DATA_DIR}{id}.json"

_get_user_rate_data_path = lambda jump_name: f"data/users/ratings/{jump_name}.json"

BATCHES_DIR = "data/batches/"
_get_batch_data_path = lambda batch_hash: f"{BATCHES_DIR}{batch_hash}.json"


def _get_channel_type(channel_id: int | str) -> int:
    """
    Returns the channeltype of a channel via the channel's ``id``.

    Channel types: 0 -> Normal, 1 -> Commands, 2 -> Moderation
    """
    return _read_from_json_safely(CHANNEL_TYPES_FILE).get(str(channel_id), 0)
        


def _format_table(list_of_rows: Iterable[list[str | Iterable[str]]], title_row: list[str | Iterable[str]] = None, title_delim: str = ">", spaces_bef_delim: int = 2, spaces_aft_delim: int = 1, delim: str = '|', stringification: Callable = lambda iterable: " - ".join(iterable)) -> str:
    """
    Turns 2-dimensional information into a spreadsheet-like string.
    An example for such a structure would be if ``list_of_rows`` was a list of objects, where each
    object itself contains multiple informations, such as 'name', 'creation_time', 'hash'...

    The string will probably only look good in a monospaced preview!

    Newline characters aren't supported and their usage in strings will likely lead to unwanted formatting!

    Example title_row:
    ["NAME",    "INFO",     "DATE",     "AUTHOR"]

    Example list_of_rows:
    [
        ["name1",   "info1",    "date1",    "author1"],
        ["name2",   "info2",    "date2",    "author2"],
        ...
    ]
    """
    
    if not title_delim: title_delim = " "
    if not delim: delim = " "
    
    # Adjust delimiters to be same length
    if len(delim) != len(title_delim):
        max_length = max(len(delim), len(title_delim))
        delim += ' ' * (max_length - len(delim))
        title_delim += ' ' * (max_length - len(title_delim))
        
    # Find longest row for the length of list of column lengths
    longest_row_length = 0
    for row in list_of_rows:
        if (length := len(row)) > longest_row_length:
            longest_row_length = length

    longest_in_column = [1] * longest_row_length
    
    # Insert title row as first row, but only for column calculations
    if title_row: tmp_data = [title_row] + list_of_rows
    else:         tmp_data = list_of_rows

    # Calculate column max lengths
    for row in tmp_data:
        for j, entry in enumerate(row):
            if not isinstance(entry, str) and isinstance(entry, Iterable):
                row[j] = stringification(entry)
                entry = row[j]  # Redefine to str version
            if (length := len(entry)) > longest_in_column[j]:
                longest_in_column[j] = length
    
    
    # Add every entry to list with spacing and delimiters included
    formatted = []
    
    if title_row:
        for j, entry in enumerate(title_row):
            formatted.append((' ' * (longest_in_column[j - 1] - len(title_row[j - 1]) + spaces_bef_delim) + title_delim + (' ' * spaces_aft_delim) if j > 0 else "") + entry)
    
    for row in list_of_rows:
        first_col = True
        for j, entry in enumerate(row):
            formatted.append(f'{(" " * (longest_in_column[j - 1] - len(row[j - 1]) + spaces_bef_delim) + delim + (" " * spaces_aft_delim)) if not first_col else NL}{entry}')
            first_col = False
    return ''.join(formatted)


# Turns a string into a SHA512 hash
def _hash_string(jump_name: str) -> str:
    return hashlib.sha512(jump_name.encode("utf-32")).hexdigest()


def _diff_to_tier(diff: str) -> str:
    diff = diff.title()
    
    # If elite or higher
    if diff in DIFF_ORDER[21:]:
        return diff
    
    if diff == DIFF_ORDER[0]:
        return TIER_ORDER[0]
    
    if diff in DIFF_ORDER[1:7]:
        return TIER_ORDER[1]
    
    if diff in DIFF_ORDER[7:11]:
        return TIER_ORDER[2]
    
    if diff in DIFF_ORDER[11:14]:
        return TIER_ORDER[3]
    
    if diff in DIFF_ORDER[14:17]:
        return TIER_ORDER[4]
    
    if diff in DIFF_ORDER[17:21]:
        return TIER_ORDER[5]


TIMEOUT: dict[int, dict[str, float]] = {}
def _get_remaining_timeout_sec(command: str, timeout_sec: float, id: str | int) -> float:
    """
    Returns the amount of time remaining for the timeout of the command for the user to be over.
    If the timeout is over or was never set for that user, it will set set the timeout to the current time and return 0.0
    """
    
    now = time.time()
    
    TIMEOUT.setdefault(id, {})
    
    if command not in TIMEOUT[id].keys():
        TIMEOUT[id][command] = now
        return 0.0
    
    difference = now - TIMEOUT[id][command]
    
    if difference > timeout_sec:
        TIMEOUT[id][command] = now
        return 0.0
    
    return timeout_sec - difference


LAST_UPDATE = {}
def _is_time_for_daily_update(to_update) -> bool:
    date = datetime.date.today()

    if to_update not in LAST_UPDATE.keys():
        LAST_UPDATE[to_update] = date
        return True
    
    if LAST_UPDATE[to_update] == date:
        return False

    LAST_UPDATE[to_update] = date
    return True
    


# HELP COMMAND
def help() -> str:
    return "**To the help page:**\nhttps://pastebin.com/4CPm8PH2"


def _ftp_to_line(ftp: tuple[Iterable[str], Iterable[str], Iterable[str]]):
    # sub-func by ChatGPT
    def join_special(lst):
        if len(lst) <= 1:
            return "".join(map(str, lst))
        else:
            return ", ".join(map(str, lst[:-1])) + " & " + str(lst[-1])
        
    ACTIONS_ORDERED = "Found", "TASed", "Proven"

    ftp_no_empty = [person_type for person_type in ftp if person_type]

    if not all(not entry for entry in ftp) and all(person_type == ftp_no_empty[0] for person_type in ftp_no_empty):
        return f"{join_special([person_type for i, person_type in enumerate(ACTIONS_ORDERED) if ftp[i]])} by {join_special(ftp_no_empty[0])}"

    parts = []
    
    for i, action in enumerate(ACTIONS_ORDERED):
        if ftp[i]:
            parts.append(f"{action} by {join_special(ftp[i])}")
 
    return ", ".join(parts)


# Jump info to string formatter (functionality over readability)
def _jump_to_dcmsg(jump_data: ElementStat) -> str:
    info_lines = [
        # Name - Kingdom, Location, ...
        f"{jump_data['name']} - {', '.join(jump_data['location'])}",
        
        # Difficulty & Tier (if 0/10 - 10/10)
        f"Difficulty: {jump_data['diff']}" + (f" ({jump_data['tier']})" if jump_data['diff'].partition("/")[0].replace(".", "").isnumeric() else ""),
        
        # Type (list of types) (only if given)
        f"Type: {', '.join(type_)}" if (type_ := jump_data.get('type', "")) else None,
        
        # Founder, TASer, Prover (only if given)
        ftp_line if (ftp_line := _ftp_to_line(tuple([jump_data.get(executor, []) for executor in ('finder', 'taser', 'prover')]))) else None,

        # From the Server
        f"From the {jump_data['server']}",
        
        # Lines of descriptions (only if given)
        "\n".join(jump_data.get('extra', "")),
        
        # Lines of links
        "\n".join(jump_data['links'])
    ]

    return "\n".join([line for line in info_lines if line])


# INFO COMMAND
def info(jump_name: str) -> str:
    jump = database.get_jump(jump_name)
    if not jump:
        return "No jump found!"

    return _jump_to_dcmsg(jump)


# Turns a user input like "loc" instead of "location" into the one in the jump dict
# Strings are expected to be .lower()
def _user_attr_to_attr(user_attribute: str) -> str:
    for attrs in USER_ATTRIBUTES:
        if user_attribute in attrs:
            return attrs[0]
    raise ValueError(f"The attribute `{user_attribute}` doesn't exist!")

# Valid when given user_attr is a valid user_attr 
def _in_user_attributes(user_attr: str) -> bool:
    try: _user_attr_to_attr(user_attr)
    except ValueError: return False
    
    return True

# Turns a user value like "metro" into "metro kingdom"
def _user_val_to_val(attr: str, user_val: str) -> str:
    lower_user_val = user_val.lower()
    
    match attr:
        # Ex: "metro" -> "Metro Kingdom"
        case "location":
            for loc in LOCATION_ORDER:
                if lower_user_val == loc.lower() or lower_user_val == loc.lower().partition(" ")[0]:
                    return loc
            if lower_user_val in 'bowsers kingdom' or lower_user_val in 'bowser kingdom':
                return "Bowser's Kingdom"
        # Ex: "1" -> "1/10" or "low" -> "Low Elite"
        case "diff":
            # Numbers with /10
            if lower_user_val.endswith("/10"):    
                if lower_user_val in DIFF_ORDER:
                    return user_val
            for diff in DIFF_ORDER:
                lower_user_val = lower_user_val.partition(" ")[0]
                if lower_user_val == diff.partition("/10")[0].partition(" ")[0].lower():
                    return diff
            
            
        # Ex: "practice" -> "Practice Tier"
        case "tier":
            for tier in TIER_ORDER:
                if lower_user_val.partition(" ")[0] in tier.lower().partition(" ")[0]:
                    return tier

        # Ex: "main" -> "SMO Trickjumping Server"
        case "server":
            for server in USER_SERVERS:
                for user_server in server:
                    if lower_user_val in user_server.lower():
                        return server[0]
        
        case "links":
            if lower_user_val.startswith("https://"):
                return user_val
        
        case "name":
            if len(user_val) <= MAX_JUMP_NAME_LENGTH:
                return user_val
            
        # Ex: "Metro Impossible" -> "Metro Impossible"
        case _:
            return user_val

    raise ValueError(f"For the attribute `{attr}` the value `{user_val}` doesn't exist!")

# Filters the database by going through each jump and checking if the entry of the attr/key fits the value given
# If the value of the jump's key fits, it stays, otherwise the jump will be thrown out
def _filter_database(db: Database, attr: str, val: str) -> Database:
    if not _in_user_attributes(attr):
        raise ValueError("Key must be a valid ATTRIBUTE")

    val = _user_val_to_val(attr, val).lower()
    
    filtered_db = {}

    for jk, jv in db.items():
        v = jv.get(attr, "")

        if isinstance(v, str) and v.lower() == val:
            filtered_db[jk] = jv
        elif isinstance(v, list):
            for e in v:
                if e.lower() == val:
                    filtered_db[jk] = jv
                    break
                
    return filtered_db

def _get_compare_val(jump: ElementStat, key: str) -> str | int:
    get_index = lambda tup: tup.index(jump.get(key))
    
    match key:
        case "location":
            # Fix later to sort by more specific location better
            # Currently only sorts by kingdom (index[0] of value)
            return LOCATION_ORDER.index(jump.get(key)[0])
        case "tier":
            return get_index(TIER_ORDER)
        case "diff":
            return get_index(DIFF_ORDER)
        case _:
            val = jump.get(key, chr(sys.maxunicode))
            if isinstance(val, (list, tuple)):
                return ", ".join(val)
            return val

# Function & sub-functions reworked and finally fixed by NoWayJay#3800, HUGE thanks to him :)
def _sort_database_by_keys(db: Database, keys: list[str]) -> Database:
    def get_compare_tuple(kv_pair: tuple[str, ElementStat]) -> tuple[str | int]:
        return tuple(_get_compare_val(kv_pair[1], key) for key in keys)
    
    return {
        k: v
        for k, v in sorted(
            db.items(),
            key=get_compare_tuple
        )
    }



def list_(args: tuple[str, ...], author: Member, base_selected: Database = None) -> str:
    attrs_shown = {'name'}
    show_further_attrs = True
    
    # Get the base of jumps being selected so either all jumps or a specific user's jumps
    if base_selected is None:
        if len(args) == 1 or args[1] == 'all':
            base_selected = database.DATABASE
            
        elif args[1] == 'mine' or args[1].isdigit():
            base_selected: Database = {}
            attrs_shown.update(PERSONAL_ATTRIBUTES) 
            
            if args[1].isdigit():
                user = args[1]
            else:
                user = author.id
            
            user_data_path = _get_user_jump_data_path(user)
            
            if not os.path.isfile(user_data_path):
                return "User doesn't have any jumps!"
            
            user_jumps: Database = _read_from_json_safely(user_data_path)
            
            # Combines user data with other jump data and adds it to base_selected
            for name, user_jump_data in user_jumps.items():
                if db_jump_data := database._get_jump_fast(name):
                    base_selected[name] = user_jump_data | db_jump_data
                else:
                    base_selected[name] = f'DELETED: {name.title()}'

        else:
            return f"For the target please enter `all`, `mine` or a valid user-ID instead of `{args[1]}`"

    # Syntax ex: !list all only kingdom metro and server main or diff 10 and server main by server +
    # Ordering must_be:
    # - only_splitter (0)
    # - attr (1)
    # - val (2)
    
    DATA_VISUALIZERS = ("+", "-")
    ONLY_SPLITTERS = ("and", "or")
    
    # Handle the "+" or "-" at the end (if it exists)
    if args[-1] in DATA_VISUALIZERS:
        if args[-1] == "+":
            attrs_shown.update(ATTRIBUTES)
        else:
            show_further_attrs = False

        args = args[:-1]
    
    # Define the start of the only_area and the by_area in the command
    only_start = 2 if len(args) > 2 and args[2] == 'only' else 0
    
    for i in range(2, len(args), 3):
        if args[i] == 'by':
            by_start = i
            break
    else:
        by_start = 0

    # Define the two areas
    if by_start:
        by_area = list(args[by_start + 1:])

        if not by_area:
            return "Please enter sorting options after `by`!"
    else:
        by_area = []

    must_be = 0
    if only_start:
        only_area = list(args[3:by_start] if by_start else args[3:])
        selected_jumps = {}
        must_be = 1

        if not only_area:
            return "Please enter filtering options after `only`!"
    else:
        only_area = []
        selected_jumps = base_selected

    def expected_instead_of(expected) -> str: 
        return f"**Expected {expected} instead of** `{elem}`**!**"
    
    # Filter by iterating over only_area to check if it is validly formatted and to get jumps to be listed
    last_or = -1
    for i, elem in enumerate(only_area):
        match must_be:
            case 0:
                if elem not in ONLY_SPLITTERS:
                    return expected_instead_of(f"a valid splitter ({_join_embed(ONLY_SPLITTERS)})")
            case 1:
                try:
                    only_area[i] = _user_attr_to_attr(elem)
                    if show_further_attrs:
                        attrs_shown.add(only_area[i])
                except ValueError:
                    return f"{expected_instead_of('a valid user attribute')}\n\n__The following attributes exist:__\n" + "\n".join(f"`{attr[0]}`  **or**  `{'`  `'.join(attr[1:])}`" for attr in USER_ATTRIBUTES) 
            case 2:
                try:
                    only_area[i] = _user_val_to_val(only_area[i - 1], elem)
                except ValueError:
                    return expected_instead_of(f"a valid user value for the attribute {only_area[i - 1]}")
                
                # If the next element doesn't exist or is "or"
                if len(only_area) < i + 2 or only_area[i + 1] == 'or':
                    tmp_selected = {**base_selected}
                    for j in range(last_or + 1, i, 3):
                        tmp_selected = _filter_database(tmp_selected, only_area[j], only_area[j + 1])
                    
                    selected_jumps |= tmp_selected
                    last_or = i + 1
                
        must_be = (must_be + 1) % 3

    match must_be:
        case 1: return f"A final user attribute & user value is missing at the end of the `only` section!\nEither add them or remove the final `{only_area[-1]}`!"
        case 2: return "A final user value is missing at the end of the `only` section!"

    # Rate limit if the amount of jumps is more than 500
    if (amt_jumps := len(selected_jumps)) == 0:
        return "No jumps with that criteria were found!"
    
    elif amt_jumps > 500:
        rem_timeout = _get_remaining_timeout_sec("list", 10, author)
        
        if rem_timeout:
            return f"Please wait another {rem_timeout:.1f} seconds to use this command again! [Timeout for lists with > 500 jumps]"
    
    # Sort by iterating over the by_area
    try:
        for i, elem in enumerate(by_area):
            by_area[i] = _user_attr_to_attr(elem)

            if show_further_attrs:
                attrs_shown.add(by_area[i])
    except ValueError:
        return expected_instead_of("a valid user attribute")

    # Sort selected jumps
    selected_jumps = _sort_database_by_keys(selected_jumps, by_area)

    # Create the list of rows of jump info for the _format_table function
    attrs_shown_sorted = list(attr for attr in ('name', *PERSONAL_ATTRIBUTES, *ATTRIBUTES[1:]) if attr in attrs_shown)
    jump_data_list = []
    for jump in selected_jumps.values():
        jump_data_list.append([jump.get(attr, "") for attr in attrs_shown_sorted])
    
    return pastee.create(_format_table(jump_data_list, title_row=list(attr.upper().replace("_", " ") for attr in attrs_shown_sorted)), 
                         beforeLink=f"Found {amt_jumps} matching jump{'s' if amt_jumps > 1 else ''}!")
    

def missing(args: tuple[str, ...], author: Member) -> str:
    if len(args) == 1 or args[1] == 'mine':
        path = _get_user_jump_data_path(str(author.id))
    elif args[1].isdigit():
        path = _get_user_jump_data_path(args[1])
    else:
        return "Please either enter `mine` to list your missing jumps or an ID of a user to list their missing jumps!"

    selected_jumps: Database

    if not os.path.isfile(path):
        selected_jumps = {}
    else:
        selected_jumps = _read_from_json_safely(path)

    selected_jumps = {jump_name: jump_data for jump_name, jump_data in database.DATABASE.items() if jump_name not in selected_jumps.keys()}
    
    return list_(args, author, base_selected=selected_jumps)



NO_SUCH_JUMP_EXISTS = "No jump with that name exists!"
JUMP_GIVEN = "Jump successfully given!"
PROOF_SET = "Proof successfully set!"
 
def give(args: tuple[str, ...], author: Member):
    # Remove all empty strings
    args = tuple(filter(lambda x: x != "", ))

    owned_file_path = _get_user_jump_data_path(author.id)

    if args[-1].lower().startswith("https://"):
        proof: str = args[-1]
        jump_name = args[1:-1]
    else:
        jump_name = args[1:]
        proof = ""
    
    print(jump_name)
    print(proof)
    jump = database.get_jump(" ".join(jump_name).lower())

    if not jump:
        return NO_SUCH_JUMP_EXISTS
    
    jump_name = jump.get("name").lower()
    ret_msg = ""

    if not os.path.isfile(owned_file_path):
        owned = {}
        ret_msg += textwrap.dedent(f"""
            **New user verified!**
            Thanks for using Jumpedia, {author.global_name}! :D
            
            """)
    else:
        owned: Database = _read_from_json_safely(owned_file_path)

        if jump_name in owned.keys():
            return "You already have that jump!"
        
    owned[jump_name] = {
        "time_given": _time_to_str(),
        "proof": proof
    }

    _write_to_json_safely(owned_file_path, owned)
        
    return ret_msg + JUMP_GIVEN + "\n" + (PROOF_SET if proof else "")

                   
def del_(jump_name: str, author: Member) -> str:
    
    owned_file_path = _get_user_jump_data_path(author.id)
    if not database.jump_exists(jump_name):
        return NO_SUCH_JUMP_EXISTS
    if not os.path.isfile(owned_file_path):
        return "You don't have any jumps to remove!"
    
    owned: Database = _read_from_json_safely(owned_file_path)
        
    if jump_name not in owned.keys():
        return "You don't have that jump!"
    
    owned.pop(jump_name)

    _write_to_json_safely(owned_file_path, owned)

    return "Jump successfully removed!"


def proof(args: tuple[str, ...], author: Member):
           
    owned_file_path = _get_user_jump_data_path(author.id)
    
    if not os.path.isfile(owned_file_path):
        return "You don't have any jumps!"
    
    with open(owned_file_path, "r") as f:
        owned: Database = _read_from_json_safely(owned_file_path)

    
    if args[1] == 'get':
        jump_name = " ".join(args[2:])
        
        if not database.jump_exists(jump_name):
            return NO_SUCH_JUMP_EXISTS
        
        try:
            proof = owned[jump_name]["proof"]
            
            if not proof:
                return "You don't have any proof set for that jump!"
            return "Here's your proof for that jump:\n" + proof
        except:
            return "You don't have that jump!"

    if args[1] == 'set':
        if len(args) < 4:
            return "Make sure to enter both the jump name & the URL to use as proof!"
        if not args[-1].lower().startswith("https://"):
            return "Please enter a valid `https://...` URL at the end!"
        
        jump_name = " ".join(args[2:-1]).lower()
        
        if not database.jump_exists(jump_name):
            return NO_SUCH_JUMP_EXISTS
        
        proof = args[-1]
        
        if jump_name not in owned.keys():
            return give(("give",) + args[2:], author)
        
        owned[jump_name]["proof"] = proof
        _write_to_json_safely(owned_file_path, owned)
        return PROOF_SET
       
    else:
        return f"Expected `get` or `set` instead of `{args[1]}`!"


def _stars_val_to_internal(val: str) -> str | None:
    vali = int(val.partition("/")[0])
    if vali <= 5 and vali >= 1:
        return str(vali)
    else: 
        return None

def _diff_avg_to_str(avg: float) -> str:
    rounded = round(avg)
    difference = avg - rounded
    
    if difference < -1/3:
        return f"{DIFF_ORDER[rounded - 1]} - {DIFF_ORDER[rounded]}"
    if difference > 1/3:
        return f"{DIFF_ORDER[rounded]} - {DIFF_ORDER[rounded + 1]}"
    
    return str(DIFF_ORDER[rounded])      
    
RATEABLES = {
    "diff": {
        "preview": "Difficulty",
        "avg_to_str": lambda avg: _diff_avg_to_str(avg),
        "val_to_internal": lambda val: str(DIFF_ORDER.index(_user_val_to_val("diff", val).title() if val.lower() != "unproven" else None)),
        "internal_to_printable": lambda intern: DIFF_ORDER[int(intern)]
    }, 
    "stars": {
        "preview": "Stars",
        "avg_to_str": lambda avg: str(int(avg * 100) / 100) + "/5",
        "val_to_internal": lambda val: _stars_val_to_internal(val),
        "internal_to_printable": lambda intern: intern + "/5"
    }
}

def rate(args: tuple[str, ...], author: Member):
    key = args[1]
    
    if key not in RATEABLES.keys():
        return f"You can only rate jump's by their difficulty with `diff` or by how good of a role they would be with `stars` instead of `{key}`!"
    
    jump_name = " ".join(args[2:-1]).lower()
    
    if not database.jump_exists(jump_name):
        return NO_SUCH_JUMP_EXISTS
    
    jump_path = _get_user_rate_data_path(_hash_string(jump_name))
    
    if not os.path.isfile(jump_path):
        with open(jump_path, "w") as f:
            jump_ratings: Database = {}
            json.dump(jump_ratings, f)
    else:
        jump_ratings: Database = _read_from_json_safely(jump_path)
    
    author_str = str(author.id)
    
    previous_rating = None
    if key in jump_ratings.keys():
        previous_rating = jump_ratings[key].get(author_str, None)
        
    NOT_VALID_RATING = f"`{args[-1]}` is not a valid rating for `{key}`!"
        
    try:
        rating: str = RATEABLES[key]["val_to_internal"](args[-1])
    except ValueError: 
        return NOT_VALID_RATING
        
    if not rating:
        return NOT_VALID_RATING
    
    if rating == previous_rating:
        return f"Rating is the same as before!"

    if key not in jump_ratings.keys():
        jump_ratings[key] = {}

    jump_ratings[key][author_str] = rating

    _write_to_json_safely(jump_path, jump_ratings)
    
    return "Jump has been rated!" if not previous_rating else f"Jump has been re-rated from `{RATEABLES[key]['internal_to_printable'](previous_rating)}` to `{RATEABLES[key]['internal_to_printable'](rating)}`!"


def ratings(jump_name: str) -> str:
    if jump_name.isspace():
        # see why no work
        return "Please enter a jump to get the rating of!"
    
    if not database.jump_exists(jump_name):
        return NO_SUCH_JUMP_EXISTS
    
    jump_path = _get_user_rate_data_path(_hash_string(jump_name))
    
    NO_RATINGS = "That jump has no ratings so far!\nBe the first to rate it! :D"

    if not os.path.isfile(jump_path):
        return NO_RATINGS
    
    rates: Database = _read_from_json_safely(jump_path)
    
    if not rates:
        return NO_RATINGS
    
    ret_msg = f"**Average ratings for __{database.get_jump(jump_name)['name']}__**"
    for rate_key, rate_value in rates.items():
        sum = 0
        amount = 0
        
        for player_rating in rate_value.values():
            amount += 1
            sum += float(player_rating)

        ret_msg += f"\n{RATEABLES[rate_key]['preview']}: {RATEABLES[rate_key]['avg_to_str'](sum/amount)} [{amount}]"
        
    return ret_msg

        
def donate() -> str:
    return "**To the donation page:**\nhttps://paypal.me/JumpediaBot"


# TODO: missing command
# TODO: This
def typedyno(args: tuple[str, ...], author: Member) -> str:
    ACTIONS = "complement", "overwrite"
    AGREEMENTS = "i know this change is not reversible and that all jumps i am still missing compared to an old backup of typedyno will be complemented", "i know this change is not reversible and that all my current jumps will be replaced by an old backup of typedyno"
    
    PLEASE_ENTER = f"Please enter a valid action ({_join_embed(ACTIONS)}) and the corressponding agreement!"
    TRANSFERRED_PATH = "data/users/typedyno/transferred_users.json"
    
    if len(args) < 3:
        return PLEASE_ENTER
    
    action = args[1]
    agreement = " ".join(args[2:])

    if action not in ACTIONS or agreement != AGREEMENTS[ACTIONS.index(action)]:
        return PLEASE_ENTER
    
    author_id = str(author.id)

    transferred: list = _read_from_json_safely(TRANSFERRED_PATH)
    if author_id in transferred:
        return "You already got your data from typedyno, no turning back!"

    if timeout := _get_remaining_timeout_sec("typedyno", 15, "global"):
        return f"To not absolutely shred the bot, this command has a slowmode for everybody together!\nAnother user just used this command, so please wait another {timeout:.1f} seconds!"

    with open("data/users/typedyno/data.json") as f:
        try:
            td_jump_data: dict[str, str] = json.load(f)[author_id]
        except KeyError:
            return "You didn't have any jumps in TypeDyno!"

    if action == "overwrite":
        _write_to_json_safely(_get_user_jump_data_path(author_id), {})

    for jump_name, jump_data in td_jump_data.items():
        give(("give", jump_name, jump_data['proof']), author)

    transferred.append(author_id)
    _write_to_json_safely(TRANSFERRED_PATH, transferred)
    
    return "Your data was successfully transferred!"


TOP100_LINK = ""
def top100(client: discord.Client) -> str:
    global TOP100_LINK
    if not _is_time_for_daily_update("top100"):
        return f"**Top 100**:\n{TOP100_LINK}"
    
    users_scoring: list[list[str | int]] = []

    ORDERING = list(TIER_ORDER)
    ORDERING.reverse()

    for file_name in os.listdir(USER_JUMP_DATA_DIR):
        if file_name.endswith(".json") and not file_name.endswith("backup.json"):
            user_id = int(file_name.removesuffix('.json'))
            username = client.get_user(user_id)

            users_scoring.append([username if username else f"UNKNOWN ({str(user_id)})", *(0 for _ in range(len(ORDERING)))])

            user_data: Database = _read_from_json_safely(_get_user_jump_data_path(user_id))
            
            for jump_name, user_jump_data in user_data.items():
                if (jump_data := database._get_jump_fast(jump_name)) and user_jump_data['proof']:
                    users_scoring[-1][1 + ORDERING.index(jump_data['tier'])] += 1
    
    users_scoring.sort(key=lambda x: x[1:], reverse=True)
    users_scoring = list(users_scoring[:100])

    for scoring in users_scoring:
        scoring.pop(1)
        for i in range(len(scoring)):
            scoring[i] = str(scoring[i])

    TOP100_LINK = pastee.create(_format_table(users_scoring, title_row=['NAME', *ORDERING[1:]])).strip()
    return top100(client)

                    

# / MOD & ADMIN COMMANDS \

NO_PERMISSION = "You don't have the permission to use this moderation command!"

# Checks if person is JUMPEDIA mod, not server mod
def _is_mod(author: Member) -> bool:
    for mod_role in secret.load()["BOT_MOD_ROLES"]:
        for user_role in author.roles:
            if user_role.id == mod_role:
                return True
            
    return _is_admin(author)

# Checks if person is JUMPEDIA admin, not server admin
def _is_admin(author: Member) -> bool:
    return author.id in secret.load()["BOT_ADMINS"]



def channeltype(channel_id: int, author: Member, type: str) -> str:
    # User has to either be a verified jumpedia mod/admin or have admin perms on the server
    
    if _is_mod(author): 
        mod_perms = True
    elif author.guild_permissions.administrator:
        mod_perms = False
    else:
        return NO_PERMISSION

    with open(CHANNEL_TYPES_FILE) as f:
        data: dict[str, int] = json.load(f)

    type = type.lower()

    if type in ("n", "none", "normal", "0"): 
        channel_type_id = 0
    elif type in ("c", "cmd", "command", "commands", "1"): 
        channel_type_id = 1
    elif type in ("m", "mod", "moderation", "admin", "2"): 
        if not mod_perms:
            return "You aren't a verified Jumpedia Moderator, so you can only set the channel's type to `Normal` or `Commands`!"
        
        channel_type_id = 2
        
    else: return "That is not a valid type for a channel!"
    
    prev_channel_type = data.get(str(channel_id), None)
    
    data[str(channel_id)] = channel_type_id
    
    _write_to_json_safely(CHANNEL_TYPES_FILE, data)
    

    if not prev_channel_type: operation = "set to"
    elif prev_channel_type == channel_type_id: operation = "kept as"
    else: operation = "changed to"
    
    

    return f"This channel's type was {operation} `{('Normal', 'Commands', 'Moderation')[channel_type_id]}`!"



Batch = dict[str, Database | str | list[str] | list[list[str]]]
MAX_BATCH_NAME = 50
BATCH_HASH_LENGTH = 128
BATCH_STATUS_ORDER = 'unfinished', 'finished', 'implemented', 'nuked'

def _get_batch_data_by_name_or_hash(name_or_hash: str) -> Batch | list[Batch]:
    """
    If a batch name is given, its corresponding non-implemented batch's data will be returned if found.
    If no non-implemented batch is found, a list of all implemented batches with a matching name will be returned.
    
    If a batch hash is given instead of a name, the batch's data will be returned (no matter if implemented or not).
    
    If the hash or name result in no results, an empty list will be returned.
    """
    
    if len(name_or_hash) == BATCH_HASH_LENGTH:
        try:
            path = _get_batch_data_path(name_or_hash)
            return _read_from_json_safely(path)
        except OSError as noSuchFile:
            return []
        
    
    matching_names = []
    
    for file_name in os.listdir(BATCHES_DIR):
        if file_name.endswith(".json") and not file_name.endswith("backup.json"):
            batch_data: Batch = _read_from_json_safely(BATCHES_DIR + file_name)

            if batch_data['name'].lower() == name_or_hash.lower():
                if not _is_locked(batch_data):
                    return batch_data
                
                matching_names.append(batch_data)

    return matching_names


def _append_log(batch_data: Batch, msg: str) -> None:
    batch_data['log'].append([_time_to_str(), msg])


def _str_author(author: Member) -> str:
    return f"'{author.global_name}' ({author.id})"


def _is_editable(batch_data: Batch) -> bool:
    return True if batch_data['status'] == 'unfinished' else False

def _is_locked(batch_data: Batch) -> bool:
    return True if batch_data['status'] == 'implemented' or batch_data['status'] == 'nuked' else False

BatchErrors = dict[str, set[str] | bool]


def _get_batch_errors(batch_data: Batch) -> BatchErrors:
    def list_jump_names(db: dict | list):
        return db.keys() if isinstance(db, dict) else db
    
    def rem_jump(jump_name: str, db: dict | list):
        db.pop(jump_name) if isinstance(db, dict) else db.remove(db.index(jump_name))
    
    errors: BatchErrors = {
        # 'jump_to_':
        'rem_not_exist': set(),
        'edit_not_exist': set(),
        'edit_in_add_too': set(),
        'edit_in_rem_too': set(),
        'add_exist': set()
    }
    
    # Check if there are any changes at all
    empty = True
    for db in BATCH_DATABASES_ORDER:
        if len(batch_data[db]) > 0:
            empty = False
    
    if empty: return {'empty': True}
        
    # Check every jump to remove
    for jump_name in batch_data['rem']:
        # Error if jump doesn't exist
        if not database._get_jump_fast(jump_name):
            errors['rem_not_exist'].add(jump_name)

    # Check every jump to edit
    for jump_name in batch_data['edit']:
        # Error if jump doesn't exist
        if not database._get_jump_fast(jump_name):
            errors["edit_not_exist"].add(jump_name)
        
        # Error if exists in 'add' db
        if jump_name in list_jump_names(batch_data['add']):
            errors['edit_in_add_too'].add(jump_name)
        # Error if exists in 'rem' db
        if jump_name in list_jump_names(batch_data['rem']):
            errors['edit_in_rem_too'].add(jump_name)
    
    # Check every jump to add
    for jump_name in batch_data['add']:
        # Error if jump does exist (to edit a jump use edit, not remove + re-add)
        if database._get_jump_fast(jump_name):
            errors['add_exist'].add(jump_name)
    
    # Return dict with only non-empty sets / True values and if no errors at all, return None
    errors_final = {error_type: val for error_type, val in errors.items() if val}
    return errors_final if errors_final else None
            
            

def _batch_errors_to_str(errors: BatchErrors, batch_name: str) -> str:
    # List that will later be joined into string
    errors_str_list = []
    
    if errors.get('empty', False):
        return "The batch contains no updates at all, therefore it cannot be finished!"

    # "BlaBlaBla description"\nHow to fix: "BlaBlaBla command"\n"- BlaBlaJump1\n- BlaBlaJump2"...
    def append_error(description: str, how_to_fix: str, jumps: Iterable):
        errors_str_list.append('\n- '.join([f"{description}\nHow to fix: {how_to_fix}\nList:", *jumps]))
    
    for error_type, jumps in errors.items():
        match error_type:
            case 'rem_not_exist':
                append_error("The following jumps that don't exist in Jumpedia were tried to be removed!", f'!batch forget "{batch_name}" rem <jump-name>', jumps)
            case 'edit_not_exist':
                append_error("The following jumps that don't exist in Jumpedia were tried to be edited!", f'!batch forget "{batch_name}" edit <jump-name>', jumps)
            case 'edit_in_add_too':
                append_error("The following jumps that were tried to be edited were also tried to be added at the same time!", f'!batch forget "{batch_name}" <"edit" to remove from edits/"add" to remove from adds> <jump-name>', jumps)
            case 'edit_in_rem_too':
                append_error("The following jumps that were tried to be edited were also tried to be removed at the same time!", f'!batch forget "{batch_name}" <"edit" to remove from edits/"rem" to remove from removals> <jump-name>', jumps)
            case 'add_exist':
                append_error("The following jumps that were tried to be added already exist!", f'!batch forget "{batch_name}" add <jump-name>', jumps)
            
    return pastee.create('\n\n'.join(errors_str_list), beforeLink="A few errors that must be fixed first were found:")


def _batch_list() -> str:
    GET_INFOS = "name", "status", "created_at", "created_by", "implemented_at", "hash"

    batches_data: list[list[str | list[str]]] = []
    for file_name in os.listdir(BATCHES_DIR):
        if file_name.endswith(".json") and not file_name.endswith("backup.json"):
            try:
                with open(BATCHES_DIR + file_name) as f:
                    batch_data_dict: dict = json.load(f)
                
                batch_data = [batch_data_dict.get(info, "") for info in GET_INFOS]

            except (json.JSONDecodeError, KeyError):
                batch_data = ["CORRUPTED"]
            
            batches_data.append(batch_data)
    
    def sort_key(batch: list[str | list[str]]):
        # batch[indexes] are referring to "GET_INFOS" indexes
        return (BATCH_STATUS_ORDER.index(batch[1]), batch[4], batch[2], batch[0])
        
    if len(batches_data) > 0:
        batches_data.sort(key=lambda batch: sort_key(batch))
        return pastee.create(_format_table(batches_data, title_row=[info.upper().replace("_", " ") for info in GET_INFOS]), beforeLink="List of batches:")
    else:
        return "There are no batches to list!"


def _batch_create(batch_name: str, batch_hash: str, author: Member) -> str:
    if not isinstance(_get_batch_data_by_name_or_hash(batch_name), list):
        return "An active batch with that name already exists!"
    
    batch_data = {
            "name": batch_name,
            "hash": batch_hash,
            "created_at": _time_to_str(),
            "created_by": _str_author(author),
            "implemented_at": "TBD",
            "status": "unfinished",
            "log": [],

            "add": {},
            "edit": {},
            "rem": []
        }
    
    _append_log(batch_data, f"{_str_author(author)} creates batch")
    _write_to_json_safely(_get_batch_data_path(batch_hash), batch_data)
    
    return "**Batch successfully created!**\n\n- You can now attach jump additions, removals and edits!\n- After everything wanted is added to the batch, its status can be set to being finished!\n- Finally the batch can be approved by a Jumpedia Admin!"


BATCH_DATABASES_ORDER = ("rem", "edit", "add")



def _batch_status(batch_data: Batch, args: tuple[str, ...], author: Member) -> str:
    args = [arg.lower() for arg in args]

    if not args:
        return f"The batch's status is currently set to `{batch_data['status']}`!"
    
    VALID_STATUSES = 'finished', 'unfinished'
    
    status = " ".join(args)

    if status not in VALID_STATUSES:
        return f"`{status}` is not a valid status, only the statuses {_join_embed(VALID_STATUSES)} are allowed!"
    
    if status == batch_data['status']:
        return f"The batch's status already is `{status}`!"
    else:
        if status == 'finished':
            if errors := _get_batch_errors(batch_data):
                _append_log(batch_data, f"{_str_author(author)} tries to set status to '{status}', but fails due to errors")
                return _batch_errors_to_str(errors, batch_data['name'])
    
        batch_data['status'] = status
        _append_log(batch_data, f"{_str_author(author)} sets status to '{status}'")
        _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data) 

        return f"The batch's status was set to `{status}`!"  

            
def _batch_add_or_edit(batch_data: Batch, args: tuple[str, ...], author: Member, add_else_edit: bool = True) -> str:
    
    TO_CHANGE_NAME = "To change a jump's name itself, just remove and add it with a new name in the same batch!"
    TO_EDIT_REQUIRED = "To edit a jump, both the name and at least one attribute to change must be contained!"
    
    last_attr = None
    jump_data: ElementStat = {}
    
    for arg in args:
        # 'name:I5' -> one value
        # or
        # 'finder:JoniKauf MadeForMario' -> multiple values
        attr, specifies_attr, val = arg.partition(':')
        attr = attr.strip()
        val = val.strip()

        if not specifies_attr:
            # If no attr is specified, ".partition" will only return the value but in the attr variable
            val = attr
            
            if not last_attr:
                last_attr = 'name'
                jump_data[last_attr] = val
                continue
                
            if last_attr not in ATTRIBUTES_LISTABLE:
                return f'The attribute `{last_attr}` cannot contain multiple values!\nMaybe you forgot to put "quotation marks" around it?'
            
            try:
                val = _user_val_to_val(last_attr, val.lower()) if last_attr != 'location' else val
            except ValueError as inv_attr_or_val:
                return str(inv_attr_or_val)
            
            jump_data[last_attr].append(val)
            
        else:
            try:
                attr = _user_attr_to_attr(attr.lower())
                
                if attr in jump_data.keys():
                    return f'A value for the attribute `{attr}` was specified more than once!\n{TO_CHANGE_NAME if not add_else_edit and attr == "name" else ""}'
                
                if attr == 'tier':
                    return f"Don't specify the attribute `{attr}`, it will automatically be calculated!"
                    
                val = _user_val_to_val(attr, val)
                last_attr = attr
            except ValueError as inv_attr_or_val:
                return str(inv_attr_or_val)
            
            if attr in ATTRIBUTES_LISTABLE:
                # If value is empty, the list will be empty -> when checking if any val is given, will return False
                jump_data[attr] = [val] if val else []
            else:
                jump_data[attr] = val

    # Remove empty infos
    if add_else_edit:
        jump_data = {attr: val for attr, val in jump_data.items() if val}
    else:
        for attr in ATTRIBUTES_REQUIRED:
            if attr in jump_data.keys() and not jump_data[attr]:
                return f"{TO_EDIT_REQUIRED}\nYou can also not remove required jump information ({_join_embed(ATTRIBUTES_REQUIRED)})!"
            
            
    # If a jump gets added, it needs all ATTRIBUTES_REQUIRED
    # If a jump gets edited, it only needs the name and at least one thing to change
    if add_else_edit:
        missing = []
        
        for attr in ATTRIBUTES_REQUIRED:
            if attr not in jump_data.keys():
                missing.append(attr)
                
        if missing:
            return f'The required attributes `{"`, `".join(missing)}` are missing!'
    else:
        if 'name' not in jump_data.keys() or len(jump_data.keys()) < 2:
            return f"{TO_EDIT_REQUIRED}\n{TO_CHANGE_NAME}"

    if 'tier' in jump_data:
        jump_data['tier'] = _diff_to_tier(jump_data['diff'])
    
    db = batch_data['add' if add_else_edit else 'edit']
    overwrite = False
    jump_name = jump_data['name'].lower()
    
    if jump_name in db.keys():
        overwrite = True
        
    db[jump_name] = jump_data
    
    _append_log(batch_data, f"{_str_author(author)} {'overwrites' if overwrite else 'adds'} jump under batch's {'additions' if add_else_edit else 'edits'} -> {'   '.join(attr.title() + ': ' + str(jump_data.get(attr, '')) for attr in ATTRIBUTES if jump_data.get(attr, ''))}")
    _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data)
    
    return f"The specified jump's info was successfully {'overwritten (because it already existed)' if overwrite else 'stored'} under the batch's {'additions' if add_else_edit else 'edits'}!"
        


def _batch_rem(batch_data: Batch, jump_name: str, author: Member) -> str:
    jump_name = jump_name.lower()
    
    for attr in USER_ATTRIBUTES[0]:
        s = attr + ":"
        if jump_name.startswith(s):
            jump_name = jump_name.removeprefix(s)
            break
            
    removals = batch_data['rem']
    
    if jump_name in removals:
        return "The specified jump's info is already stored under the batch's removals!"
    
    removals.append(jump_name)
    _append_log(batch_data, f"{_str_author(author)} adds jump under batch's removals -> Name: {jump_name}")
    _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data)

    return "The specified jump's info was successfully stored under the batch's removals!"


def _batch_forget(batch_data: Batch, args: tuple[str, ...], author: Member) -> str:
    if len(args) < 2:
        return f"Please enter both a valid operation ({_join_embed(BATCH_DATABASES_ORDER)}) and the jump you want to remove from that operation!"
    
    operation = args[0].lower() if args[0].lower() != 'del' else 'rem'
    jump_name = " ".join(args[1:]).lower()
    
    for attr in USER_ATTRIBUTES[0]:
        s = attr + ":"
        if jump_name.startswith(s):
            jump_name = jump_name.removeprefix(s)
            break
    
    if operation not in BATCH_DATABASES_ORDER:
        return f"Only the operations `{'`, `'.join(BATCH_DATABASES_ORDER)}` are valid!"
    
    NO_SUCH_JUMP = "There is no jump with that name stored in the batch under that operation!"
    
    jump_iter = batch_data[operation]

    if isinstance(jump_iter, dict):
        if jump_name not in jump_iter.keys():
            return NO_SUCH_JUMP
        
        jump_iter.pop(jump_name)
    
    else:
        if jump_name not in jump_iter:
            return NO_SUCH_JUMP

        jump_iter.pop(jump_iter.index(jump_name))
    
    _append_log(batch_data, f"{_str_author(author)} lets batch information be forgotten -> Operation: {operation}   Name: {jump_name}")
    _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data)
    
    return "The specified batch information was successfully forgotten!"


def _batch_log(batch_data: Batch):
    return pastee.create(_format_table(batch_data['log'], ['Time', 'Info']), beforeLink=f"Logs found:")


def _batch_download(batch_data: Batch) -> tuple | str:
    file_path = _get_batch_data_path(batch_data['hash'])
    
    with open(file_path) as f:
        text = f.read()
        
        if len(text) > 14_000_000:
            return pastee.create(text, beforeLink="**File size too big, data sent via pastee:**")
        
    return ("**Requested batch data:**", file_path)
        

def _batch_approve(batch_data: Batch, author: Member) -> str:
    if not _is_admin(author):
        return "You must be a Jumpedia Admin to be able to approve a batch!"
    
    if batch_data['status'] != 'finished':
        _append_log(batch_data, f"{_str_author(author)} tries to approve batch, but fails due to status not being 'finished'")
        return "Only batches that have the status `finished` can be approved!"
    
    if errors := _get_batch_errors(batch_data):
        _append_log(batch_data, f"{_str_author(author)} tries to approve batch, but fails due to errors")
        return _batch_errors_to_str(errors, batch_data['name'])
    
    # Copy database (for safety)
    db = {**database.DATABASE}
    
    DATABASE_DIR = "data/jumps/"
    _write_to_json_safely(DATABASE_DIR + "jump_data_" + time.strftime("%Y-%m-%d_%H-%M-%S_UTC", time.gmtime()) + ".json", db)
    
    # Remove jumps
    for jump_name in batch_data['rem']:
        db.pop(jump_name)
    
    # Edit jumps
    for jump_name, jump_data in batch_data['edit'].items():
        for attr, val in jump_data.items():
            if attr != 'name':
                if not val:
                    db[jump_name].pop(attr, "")
                else:
                    db[jump_name][attr] = val
    
    # Add jumps
    db |= batch_data['add']

    # Save all changes to files and update database the bot is running on
    _write_to_json_safely(DATABASE_DIR + "jump_data.json", db)
    database.DATABASE = db
    
    batch_data['status'] = 'implemented'
    batch_data['implemented_at'] = _time_to_str()
    
    _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data)
    return "**The batch was successfully approved!**\nThe changes are now implemented and no further changes to the batch can be made!"


def _batch_info(batch_data: Batch) -> str:
    
    def database_to_str(title: str, db: list[str | Iterable[str]] | Database) -> str:
        INDENT = "   "
        LISTER1 = "- "
        LISTER2 = "> "
        NONE = f"{title}:\n{INDENT}{LISTER1}None"
        
        if isinstance(db, list):
            return f"\n{INDENT}{LISTER1}".join([f"{title}:", *(item if isinstance(item, str) else ' | '.join(item) for item in db)]) if db else NONE
        
        jump_texts = []
        for name, infos in db.items():
            jump_texts.append(f"\n{INDENT * 2}{LISTER2}".join([off_name['name'] if (off_name := database._get_jump_fast(name)) else f"{name}*" + ":", *(f"{attr.title()}: {str(info)}" for attr, info in infos.items() if attr != 'name')]))
        
        return f"\n{INDENT}{LISTER1}".join([f"{title}:", *jump_texts]) if jump_texts else NONE
            
    SINGLE_LINE_INFOS = "name", "created_at", "created_by", "implemented_at", "status", "hash"
    texts = [
        "\n".join(f"{info.capitalize().replace('_', ' ')}: {batch_data.get(info, 'Not specified')}" for info in SINGLE_LINE_INFOS),
        database_to_str("Additions", batch_data['add']),
        database_to_str("Edits", batch_data['edit']),
        database_to_str("Removals", batch_data['rem']),
        database_to_str("Logs", batch_data['log']),
        "* next to a jump's name means that the jump is currently not Jumpedia's Database.\nThis means that it simply wasn't added yet (the batch has to still be implemented)\nor that the jump was removed."
    ]
    
    return pastee.create("\n\n".join(texts), beforeLink="Info found:")
    

def _batch_nuke(batch_data: Batch, author: Member) -> str:
    if not _is_admin(author):
        return "You must be a Jumpedia Admin to be able to nuke a batch!"
    
    _append_log(batch_data, f"{_str_author(author)} NUKES BATCH!!!")
    batch_data['status'] = 'nuked'

    _write_to_json_safely(_get_batch_data_path(batch_data['hash']), batch_data)
    return "The batch was successfully ***NUKED***! :exploding_head:"


# TODO: Non-changing operations on implemented batches via hash
def batch(channel_id: int, args: tuple[str, ...], message: Message) -> str:
    operation = args[1].lower() if args[1].lower() != 'del' else 'rem'
    author = message.author

    if not _is_mod(author):
        return "You aren't authorized to use this command!"
    elif _get_channel_type(channel_id) < 2:
        return "Channel must be of type `Moderation`!"
    
    # Operations that require no specification of a batch
    match operation:
        case 'list': return _batch_list()
    
    if len(args) < 3:
        return "Not enough arguments given!\nSyntax: `!batch <operation> <batch name> [arguments]`"
    if len(args[2]) > MAX_BATCH_NAME and len(args[2]) != 128:
        return "The maximum length for a batch name is 50 characters!"
    
    batch_name = args[2]
    rest = " ".join(args[3:])
    new_batch_hash = _hash_string(batch_name + str(time.time()))
    args = args[3:]
        
    batch_data = _get_batch_data_by_name_or_hash(batch_name)
    
    # Operations that require no certain batch to exist
    match operation:
        case 'create': return _batch_create(f"{batch_name}{(' ' + rest) if rest else ''}", new_batch_hash, author)
    
    if not batch_data:
        return "No batch with that name/hash exists!"
    
    if isinstance(batch_data, list):
        return textwrap.dedent("""
            Only already implemented batches with that name exist and such batches can only be interacted with via their corresponding hash!
            Use `!batch list` to get their hash!
        """)
    
    # Operations that don't alter the batch's info
    match operation:
        case 'log': return _batch_log(batch_data)
        case 'download': return _batch_download(batch_data)
        case 'info': return _batch_info(batch_data)
    
    if _is_locked(batch_data):
        return "The specified batch is locked, meaning it is not editable anymore but all info can be accessed!"
    
    # Operations that change any batch info (including the status)
    match operation:
        case 'status': return _batch_status(batch_data, args, author)
        case 'approve': return _batch_approve(batch_data, author)
        case 'nuke': return _batch_nuke(batch_data, author)
    
    if not _is_editable(batch_data):
        return f"The batch is currently not editable because its status is `{batch_data['status']}`!"
    
    # Operations that change any batch info besides status
    match operation:
        case 'add': return _batch_add_or_edit(batch_data, args, author, add_else_edit=True)
        case 'edit': return _batch_add_or_edit(batch_data, args, author, add_else_edit=False)
        case 'rem': return _batch_rem(batch_data, rest, author)
        case 'forget': return _batch_forget(batch_data, args, author)
        #case 'json': pass
        #case 'undo': pass
    
    return f"The batch command `{operation}` does not exist!"
        


def genlist(server_user_val: str, author: Member):
    if not _is_admin(author):
        return "You must be a Jumpedia Admin to be able to use this command!"
    
    try:
        server = _user_val_to_val('server', server_user_val)
    except ValueError:
        return "Please enter a valid server user attribute!"
    
    server_jumps = [{attr: jump_data[attr] for attr in('name', 'location', 'diff')} for jump_data in database.DATABASE.values() if jump_data['server'] == server] 
    text_list = []

    for loc in LOCATION_ORDER:
        curr_loc = []
        for jump in server_jumps:
            if jump['location'][0] == loc:
                curr_loc.append(jump)
        
        if curr_loc:
            curr_loc.sort(key=lambda jump: DIFF_ORDER.index(jump['diff']))
            curr_loc = [f"{jump['name']} | {jump['diff']}" for jump in curr_loc]
            curr_loc.insert(0, f"__**{loc}**__:")
            text_list.append("\n".join(curr_loc))
    
    return pastee.create("\n\n".join(text_list), beforeLink=f"**{server} list:**")

    


def run(message: Message, client: discord.Client) -> str:
    # From https://op.europa.eu/en/web/eu-vocabularies/formex/physical-specifications/character-encoding/quotation-marks
    QUOT_MARKS_TO_REPL = "“”«»“”„‟"
    SINGLE_QUOT_MARKS_TO_REPL = "‘’‚‛‹›"

    input = message.content

    for quot_mark in QUOT_MARKS_TO_REPL: input = input.replace(quot_mark, '"')
    for s_quot_mark in SINGLE_QUOT_MARKS_TO_REPL: input = input.replace(s_quot_mark, "'")

    input_l = input.lower()
    # Ignore if just prefix or not even prefix
    if not input_l.startswith(PREFIX) or len(input) == len(PREFIX):
        return None

    try:
        args = tuple(shlex.split(input))  # Split string into arguments (shell-like)
        args_l = tuple(arg.lower() for arg in args)
        
        rest_l = " ".join(args[1:]).lower()
        cmd = args[0][len(PREFIX):].lower()
        
        channel_id = message.channel.id
        author = message.author
    except:
        return "Put arguments with special characters like `\'` or `SPACE` into `\"quotation marks\"` or alternatively put a `\\` behind every special character\nExample: `\"Bowser's Kingdom\"` or `Bowser\\'s\\ Kingdom`"
    
    # !channeltype is usable everywhere
    if cmd == "channeltype":
        return channeltype(channel_id, author, rest_l)
    
    cmd = 'del' if cmd == 'rem' else cmd
    
    # All other commands must have channeltype > 0 (commands or moderation)
    if _get_channel_type(channel_id):
        match cmd:
            case 'help': return help()
            case 'info': return info(rest_l)
            case 'list': return list_(args_l, author)
            case 'missing': return missing(args, author)
            case 'give': return give(args, author)  
            case 'del': return del_(rest_l, author)
            case 'proof': return proof(args, author)
            case 'rate': return rate(args_l, author)
            case 'ratings': return ratings(rest_l)
            case 'donate': return donate() 
            case 'typedyno': return typedyno(args_l, author)
            case 'batch': return batch(channel_id, args, message)
            case 'genlist': return genlist(rest_l, author) 
            #case 'top100': return top100(client)
            case _: return "That command doesn't exist! Enter `!help` if you need assistance!"
            
            
            
"""
def _cut_string_if_too_long(string: str, max_length: int, regex: str) -> str:
    if len(string) > max_length:
        string = string[:max_length]
        match = re.search(regex, string[::-1])

        if match:
            string = string[:len(string) - match.start() - len(match[-1])] + "\n..."

    return string
    
def _batch_json(batch_name: str, message: Message, args: tuple[str, ...]) -> str:
    if args[0] in 'overwrite':
        overwrite_jump_data = True
    elif args[0] in 'append':
        overwrite_jump_data = False
    
    attachments = message.attachments
    batch_updates: list[Batch] = []

    for attachment in attachments:
        if attachment.filename.endswith('.json'):
            try:
                response = requests.get(attachment.url)
                data = response.json()
                batch_updates.append(data)
            except requests.exceptions.JSONDecodeError:
                pass    # Don't add to list

    if not batch_updates:
        return "No valid `.json` files were attached to the message!"
    
    with open(_get_batch_file_path(batch_name)) as f:
        batch: Batch = json.load(f)
    
    not_updated: list[str] = []
    updated: list[ElementStat] = []
    try:
        # jsons -> add, del, edit -> database -> jump
        for file in batch_updates:
            for batch_key, database in file.items():
                if batch_key not in VALID_BATCH_KEYS:
                    not_updated.append(f"`{batch_key}` is not a valid json operation (only {', '.join(VALID_BATCH_KEYS)} allowed)!")
                    continue

                for jump_name, jump_data in database.items():
                    batch_jump_data = batch.setdefault(batch_key, {}).setdefault(jump_name.lower(), {})

                    if overwrite_jump_data: 
                        batch_jump_data = jump_data
                    else: 
                        batch_jump_data.update(jump_data)

                    updated.append(jump_data)
    except NameError | AttributeError | TypeError | KeyError as e:
        return f"The `.json` provided was malformed! The specificed error is:\n```{str(e)}```"

    if len(updated) == 0:
        return "Nothing was updated, probably because the jsons didn't contain any (new) data!"
    
    # List appending, then converting to string is faster than string appending
    updated_str_as_list = []
    
    for jump_data in updated:
        updated_str_as_list.append(f"- {jump_data['name']}")
        
        for attr, val in jump_data.items():
            updated_str_as_list.append(f"\t- {attr}: {val}")

    updated_str = _cut_string_if_too_long("\n".join(updated_str_as_list), 800, r'\n(?!\t)')
    not_updated = _cut_string_if_too_long("\n".join(not_updated), 800, r'\n')

    return f"**The batch was updated with the contents of the json file(s)**!\n \
        For any jumps that already existed in the same operation, the data was {'overwritten' if overwrite_jump_data else 'appended'}!\n\n \
        {f'__Following things were updated:__{NL}{updated_str}{NL * 2}' if updated_str else ''} \
        {f'__Following things could not be updated:__{NL}{not_updated}{NL * 2}' if not_updated else ''}\n\n \
        If anything went wrong, __**IMMEDIATELY**__ use the `!batch undo` command to revert all changes!"
"""     
