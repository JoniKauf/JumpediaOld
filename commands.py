# / IMPORTS \
import shlex, json, time, sys, os       # External
import pastee, database                 # Internal

# "From" imports
from discord import Member      
from database import Database, ElementStat

# true rivals, rune factory frontier - autumn theme

# / GLOBALS & CONSTANTS \

# Load all jumps
with open("data/jump_data.json") as f:
    JUMP_DATA = json.load(f)

JUMPEDIA_ADMINS = ("679564566769827841",)

# Newline for some f-strings
NL = "\n"

# Discord input
PREFIX = '!'

# Attributes users can enter that mean the same thing (e.g. input "n" means "name")
USER_ATTRIBUTES = (("name",     "n"),
                   ("location", "kingdom", "loc", "k"),
                   ("diff",     "difficulty", "d"),
                   ("tier",     "t"), ("type", "ty"),
                   ("founder",  "found", "f"),
                   ("taser",    "tased", "tas"),
                   ("prover",   "proved", "p"),
                   ("server",   "s"),
                   ("extra",    "desc", "description", "ex", "e","info", "i"),
                   ("links",    "link", "l"))

# > First element of every USER_ATTRIBUTES tuple
# > USER_ATTRIBUTES get converted to these
# > Actual ATTRIBUTES used in the code and the jump_data
ATTRIBUTES = tuple(tpl[0] if tpl else None for tpl in USER_ATTRIBUTES)

PERSONAL_ATTRIBUTES = ("proof", "time_given")

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



# / FUNCTIONS \
# > Functions with no leading "_" are the discord command's functions
# > Each leading "_" in the function name indicates a level of sub-functionality
# > E.g. "__get_compare_val" is a sub-sub-function of a discord command's function

# Global way to turn a list to str
def _list_to_str(list: list[str]) -> str:
    return ", ".join(list)

# Creates a backup. Make sure if the main json is not readable, this will not be called!!
# > If backup file corrupts, main file isn't touched
# > If main file corrupts, backup is saved

BACKUP_NAME_EXTENSION = "_backup"
def _write_to_json_safely(main_file_path: str, data: Database) -> None:
    with open(main_file_path[:-len(".json")] + BACKUP_NAME_EXTENSION + ".json", "w") as bf:
        json.dump(data, bf)
    with open(main_file_path, "w") as of:
        json.dump(data, of)
        

def _fix_corrupted_json(path_json_to_fix: str) -> str:
    # To avoid as many further issues as possible, files get opened and closed individually instead of at once
    
    with open(path_json_to_fix[:-len(".json")] + BACKUP_NAME_EXTENSION + ".json", "r") as bf:
        backup = json.load(bf)
    with open(path_json_to_fix, "w") as cf:
        json.dump(backup, cf)
        

_get_user_jump_data_path = lambda id: f"data/user_data/jump_data/{id}.json"
_get_user_rate_data_path = lambda jump_name: f"data/user_data/rate_data/{jump_name}.json"


# HELP COMMAND
def help() -> str:
    return "**To the help page:**\nhttps://pastebin.com/4CPm8PH2"


# Jump info to string formatter (functionality over readability)
def _jump_to_dcmsg(jump: ElementStat) -> str:
    # Name - Kingdom
    # Difficulty / Jump Type
    # [Founder/Taser/Prover]
    # From the Server
    # [Extra Infos]
    # Links
    return (
        f"{jump['name']} - {jump['location']}{NL}" +
        f"{'Jump Type: ' + jump['type'] if 'type' in jump else 'Difficulty: ' + jump['diff']}{NL}" +
        (f"{jump['line']}{NL}" if 'line' in jump else '') +
        f"From the {jump['server']}{NL}" +
        (f"{NL.join(jump['extra'])}{NL}" if 'extra' in jump else '') +
        f"{NL.join(jump['links'])}")

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

# Valid when given user_attr is a valid user_attr 
def _in_user_attributes(user_attr: str) -> bool:
    if _user_attr_to_attr(user_attr):
        return True
    return False

# Turns a user value like "metro" into "metro kingdom"
# Strings are expected to be .lower()
def __user_val_to_val(attr: str, user_val: str) -> str:
    match attr:
        # Ex: "metro" -> "metro kingdom"
        case "location":
            for loc in LOCATION_ORDER:
                if user_val == loc.lower().partition(" ")[0]:
                    return loc.lower()
        # Ex: "1" -> "1/10" or "low" -> "low elite"
        case "diff":
            # Numbers with /10
            if user_val.endswith("/10"):    
                if user_val in DIFF_ORDER:
                    return user_val
            for diff in DIFF_ORDER:
                user_val = user_val.lower().partition(" ")[0]
                if user_val == diff.partition("/10")[0].partition(" ")[0].lower():
                    return diff.lower()
            
            
        # Ex: "practice" -> "practice tier"
        case "tier":
            for tier in TIER_ORDER:
                if user_val in tier.lower().partition(" ")[0]:
                    return tier.lower()

        # Ex: "main" -> "SMO Trickjumping Server"
        case "server":
            for server in USER_SERVERS:
                for user_server in server:
                    if user_val in user_server.lower():
                        return server[0].lower()
        
        # Ex: "Metro Impossible" -> "metro impossible"
        case _:
            return user_val.lower()

    raise ValueError(f"For the attribute `{attr}` the value `{user_val}` doesn't exist!")

# Filters the database by going through each jump and checking if the entry of the attr/key fits the value given
# If the value of the jump's key fits, it stays, otherwise the jump will be thrown out
def _filter_database(db: Database, attr: str, val: str) -> Database:
    if not _in_user_attributes(attr):
        raise ValueError("Key must be a valid ATTRIBUTE")

    val = __user_val_to_val(attr, val)
    
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

def __get_compare_val(
    jump: ElementStat,
    key: str
) -> str | tuple[str] | int:
    get_index = lambda tup: tup.index(jump.get(key, chr(127)))

    match key:
        case "location":
            return get_index(LOCATION_ORDER)
        case "tier":
            return get_index(TIER_ORDER)
        case "diff":
            return get_index(DIFF_ORDER)
        case _:
            val = jump.get(key, chr(sys.maxunicode))
            if isinstance(val, list):
                return tuple(val)
            return val

# Function & sub-functions reworked by NoWayJay#3800, HUGE thanks to him :)

def _sort_database_by_keys(db: Database, keys: list[str]) -> Database:
    def get_compare_tuple(
        kv_pair: tuple[str, ElementStat]
    ) -> tuple[str | tuple[str] | int, ...]:
        return tuple(__get_compare_val(kv_pair[1], key) for key in keys)
    return {
        k: v
        for k, v in sorted(
            db.items(),
            key=get_compare_tuple
        )
    }


def _database_to_str(jumps: Database, attrs: tuple) -> str:
    if len(jumps) < 1:
        return None
    
    # Remove any clones
    lst_attrs = list(set(attrs))
    lst_attrs.sort(key=lambda attr: (PERSONAL_ATTRIBUTES + ATTRIBUTES).index(attr))
    try: lst_attrs.remove("name") 
    except: pass
    lst_attrs.insert(0, "name")
    
            
    # Attributes that will be shown
    attrs = tuple(lst_attrs)
    
    # Get length of longest value to later align attribute values in file
    longest = [1] * len(attrs)  # Longest value of each attribute of all jumps
    
    for jump in jumps.values():
        for k, v in jump.items():
            if isinstance(v, list):
                v = _list_to_str(v)

            length = len(v)
        
            if k in attrs and longest[attrs.index(k)] < length:
                longest[attrs.index(k)] = length

    BONUS_SPACE_AMT = 2
    
    # Using lists is almost 20x faster than concatenating strings
    # 3.5s -> 0.2s !!!
    textAsList = []
    lastLen = 0

    # Add titles on top + change column width if needed
    for i, attr in enumerate(attr.upper().replace("_", " ") + ": " for attr in attrs):
        if longest[i] < len(attr):
            longest[i] = len(attr)

        if i > 0:
            textAsList += ' ' * (longest[i - 1] - lastLen + BONUS_SPACE_AMT) + "> "
        
        textAsList.append(attr)
        lastLen = len(attr)
    
    lastLen = 0

    # Print every value in columns by putting enough spaces in between
    for jump in jumps.values():
        textAsList += "\n"

        for i, k in enumerate(attrs):
            if i > 0:
                textAsList += ' ' * (longest[i - 1] - lastLen + BONUS_SPACE_AMT) + '| '

            v = jump.get(k, '')

            if isinstance(v, list):
                v = _list_to_str(v)

            textAsList += v
            lastLen = len(v)

    return "".join(textAsList)

# A list of jumps can be changed like (only -> filtering, by -> sorting):
OPERATORS = "only", "by"

def list_(args: tuple[str], author: Member) -> str:
    attrs_shown: list[str] = list()
    show_any_attrs = True
    
    if len(args) == 1 or args[1] == 'all':
        selected_jumps = database.DATABASE
        
    elif args[1] == 'mine' or args[1].isdigit():
        attrs_shown += PERSONAL_ATTRIBUTES
        
        if args[1].isdigit():
            user = args[1]
        else:
            user = author.id
        
        user_data_path = _get_user_jump_data_path(user)
        
        if not os.path.isfile(user_data_path):
            return "User doesn't have any jumps!"
        
        with open(user_data_path, "r") as f:
            try:
                selected_jumps: Database = json.load(f)
                
                for name, data in selected_jumps.items():
                    try:
                        data |= database._get_jump_fast(name).items()
                    except AttributeError:
                        data |= {"name": f"REMOVED: {name.title()}"}
            except json.decoder.JSONDecodeError:
                _fix_corrupted_json(user_data_path)
                return list_(args, author)
    else:
        return f"For the target please enter `all`, `mine` or a valid user-ID instead of `{args[1]}`"
    
    if args[-1] in ("+", "-"):
        if args[-1] == "+":
            attrs_shown += list(ATTRIBUTES)
        else:
            show_any_attrs = False
            
        args = args[:-1]
    
    sorts = list()
    chunk = list()

    nextArgType = "key"

    try:
        for i, arg in enumerate(args[2:]):
            if nextArgType == "attr":
                arg = _user_attr_to_attr(arg)
                
                if show_any_attrs:
                    attrs_shown.append(arg)
                
                if not arg:
                    msg = f"**Expected a valid attribute!**\n\n__The following attributes exist:__"
                    for attr in USER_ATTRIBUTES:
                        msg += f"\n`{attr[0]}`  **or**  `{'`  `'.join(attr[1:])}`"

                    raise ValueError(msg)

            chunk.append(arg)

            if nextArgType == "key":
                if arg not in OPERATORS:
                    raise ValueError(f"Expected `only` or `by` instead of `{arg}`")

                nextArgType = "attr"

            elif nextArgType == "attr":
                if not _in_user_attributes(arg):
                    raise ValueError(f"Expected an attribute instead of `{arg}`")

                if chunk[0] == "only":
                    nextArgType = "val"
                elif chunk[0] == "by":
                    sorts.append(arg)
                    nextArgType = "key"

            elif nextArgType == "val":
                selected_jumps = _filter_database(selected_jumps, chunk[1], chunk[2])
                nextArgType = "key"

            if nextArgType == "key":
                chunk.clear()
        # for-loop end ------------------------

        if nextArgType != "key":
            raise ValueError("Final key does not have enough arguments!")

    except ValueError as e:
        return str(e)

    if len(sorts) > 0:
        selected_jumps = _sort_database_by_keys(selected_jumps, sorts)
    
    content = _database_to_str(selected_jumps, attrs_shown)

    amt_jumps = len(selected_jumps)
    if amt_jumps <= 0:
        return "No jumps with that criteria were found!"
    return pastee.create(
        content, f"Found {amt_jumps} matching jump{'s' if amt_jumps > 1 else ''}!")


NO_SUCH_JUMP_EXISTS: str = "No jump with that name exists!"
JUMP_GIVEN: str = "Jump successfully given!"
PROOF_SET: str = "Proof successfully set!"
 
def give(args: tuple[str], author: Member):
    owned_file_path = _get_user_jump_data_path(author.id)

    if args[-1].startswith("https://"):
        proof: str = args[-1]
        jump_name = args[1:-1]
    else:
        jump_name = args[1:]
        proof = ""
    
    jump = database.get_jump(" ".join(jump_name))

    if not jump:
        return NO_SUCH_JUMP_EXISTS
    
    jump_name = jump.get("name").lower()
    ret_msg = ""

    if not os.path.isfile(owned_file_path):
        owned = {}
        ret_msg += f"**New user verified!**\nThanks for using Jumpedia, {author.name}!\n\n"
    else:
        with open(owned_file_path, "r") as f:
            try:
                owned: Database = json.load(f)
            except:
                _fix_corrupted_json(owned_file_path)
                return give(args, author)

        if jump_name in owned.keys():
            return "You already have that jump!"
        
    owned[jump_name] = {
        "time_given": time.strftime("%Y-%m-%d %H:%M:%S (UTC)", time.gmtime()),
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
    
    with open(owned_file_path, "r") as f:
        try:
            owned: Database = json.load(f)
        except:
            _fix_corrupted_json(owned_file_path)
            return del_(jump_name, author)

    if jump_name not in owned.keys():
        return "You don't have that jump!"
    
    owned.pop(jump_name)

    _write_to_json_safely(owned_file_path, owned)

    return "Jump successfully removed!"


def proof(args: tuple[str], author: Member):
           
    owned_file_path = _get_user_jump_data_path(author.id)
    
    if not os.path.isfile(owned_file_path):
        return "You don't have any jumps!"
    
    with open(owned_file_path, "r") as f:
            try:
                owned: Database = json.load(f)
            except:
                _fix_corrupted_json(owned_file_path)
                return proof(args, author)

    
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
        if not args[-1].startswith("https://"):
            return "Please enter a valid `https://...` URL at the end!"
        
        jump_name = " ".join(args[2:-1])
        
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


def ___stars_val_to_internal(val: str) -> str | None:
    vali = int(val.partition("/")[0])
    if vali <= 5 and vali >= 1:
        return str(vali)
    else: 
        return None

def ___diff_avg_to_str(avg: float) -> str:
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
        "avg_to_str": lambda avg: ___diff_avg_to_str(avg),
        "val_to_internal": lambda val: str(DIFF_ORDER.index(__user_val_to_val("diff", val).title() if val.lower() != "unproven" else None)),
        "internal_to_printable": lambda intern: DIFF_ORDER[int(intern)]
    }, 
    "stars": {
        "preview": "Stars",
        "avg_to_str": lambda avg: str(int(avg * 100) / 100) + "/5",
        "val_to_internal": lambda val: ___stars_val_to_internal(val),
        "internal_to_printable": lambda intern: intern + "/5"
    }
}

def rate(args: tuple[str], author: Member):
    key = args[1]
    
    if key not in RATEABLES.keys():
        return f"You can only rate jump's by their difficulty with `diff` or by how good of a role they would be with `stars` instead of `{key}`!"
    
    jump_name = " ".join(args[2:-1]).lower()
    
    if not database.jump_exists(jump_name):
        return NO_SUCH_JUMP_EXISTS
    
    jump_path = _get_user_rate_data_path(jump_name)
    
    if not os.path.isfile(jump_path):
        with open(jump_path, "w") as f:
            jump_ratings: Database = {}
            json.dump(jump_ratings, f)
    else:
        with open(jump_path, "r") as f:
            try:
                jump_ratings: Database = json.load(f)
            except:
                _fix_corrupted_json(jump_path)
                return rate(args, author)
    
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
    
    jump_path = _get_user_rate_data_path(jump_name.lower())
    
    NO_RATINGS = "That jump has no ratings so far!\nBe the first to rate it! :D"

    if not os.path.isfile(jump_path):
        return NO_RATINGS
    
    with open(jump_path, "r") as f:
        try:
            rates: Database = json.load(f)
        except:
            _fix_corrupted_json(jump_path)
            return ratings(jump_name)
    
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



def run(input: str, author: Member) -> str:

    # Ignore if just prefix or not even prefix
    if not input.startswith(PREFIX) or len(input) == len(PREFIX):
        return None

    input = input.lower()[len(PREFIX):] # Remove prefix

    try:
        args = tuple(shlex.split(input))  # Split string into arguments (shell-like)
        cmd = args[0]
        rest = " ".join(args[1:])
    except:
        return "Put arguments with special characters like `\'` or `SPACE` into `\"quotation marks\"` or alternatively put a `\\` behind every special character\nExample: `\"Bowser's Kingdom\"` or `Bowser\\'s\\ Kingdom`"

    cmd = 'del' if cmd == 'rem' else cmd
    
    match cmd:
        case 'help': return help()
        case 'info': return info(rest)
        case 'list': return list_(args, author)
        case 'give': return give(args, author)  
        case 'del': return del_(rest, author)
        case 'proof': return proof(args, author)
        case 'rate': return rate(args, author)
        case 'ratings': return ratings(rest)
        case 'donate': return donate()
        case _: return "That command doesn't exist! Enter `!help` if you need assistance!"
    
    