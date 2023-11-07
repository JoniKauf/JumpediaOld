# Jumpedia
Jumpedia is a discord bot developed for the Super Mario Odyssey Trickjumping Community. It allows you, the user, to get any information about any trickjumps in its database, select jumps you have completed and set proof for them, rate jumps based on their quality & difficulty and much more. 


## How Jumpedia works
Jumpedia is a static/universal bot, meaning that all the data in the bot is the same (synced) across servers and the data is only changeable by Jumpedia staff, not by staff of servers the bot is on. If a jump is not stored in Jumpedia yet, it can be submitted to the Trickjump Database and it will be added by the team as soon as possible!
- The SMO Trickjumping Server: https://discord.gg/CxqUN9E
- The Trickjump Database: https://discord.gg/cJnFmM6bjD


## How to setup the bot on your server
**There are 2 simple steps to setup the bot on your server:**
1. Invite the bot to your server by clicking [**here**](https://discord.com/api/oauth2/authorize?client_id=1063173353352986645&permissions=8&scope=bot)
2. Activate commands in the desired channel by typing `!channelconf commands normal` ([More channelconf info](#channelconf-command))                        

And that's it! :)


# Commands
Here you can find the list of all commands! If a term needs more explanation, it will be hyperlinked (clickable like a link) to the term explanation.
- The current prefix is `!`
- Commands use [shell-like syntax](#shell-like-syntax)

### Table formatting
- Enclosed in `<>` means the argument is required
- Enclosed in `[]` means the argument is optional
- Lead by `*` means this argument can be made up of multiple sub-arguments, which is explained in the command's `[More details]` tab


## User Commands
| User Command   | Arguments                                           | Description                                                                                                                                                           |
|----------------|-----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `help`         |                                                     | Returns a link to this page                                                                                                                                           |
| `info`         | `<jump-name>`                                       | Returns all information about the specified jump                                                                                                                      |
| `random`       |                                                     | Returns a random jump's info (more customisation planned in the future)                                                                                               |
| `give`         | `<jump-name> [proof-link]`                          | Adds the specified jump to the user's list and (if included) sets the proof                                                                                           |
| `proof`        | `get <jump-name>`<br>`set <jump-name> <proof-link>` | Returns the user's proof link set for the specified jump<br>Sets the link given as proof for the specified jump                                                       |
| `rem`<br>`del` | `<jump-name>`                                       | Removes the specified jump from the user's list                                                                                                                       |
| `list`         | `<target> [*filters] [*sorts] [yield]`              | Returns a link to a list with all jumps from the target with the filters, sorts and yield applied<br>[\[More details\]](#list-command)                                |
| `missing`      | `<target> [*filters] [*sorts] [yield]`              | Returns a link to a list with all jumps the target is missing with the filters, sorts and yield applied<br>[\[More details\]](#missing-command)                       |
| `rate`         | `<key> <jump-name> <value>`                         | Rates the specified jump with the given value for the key specified<br>[\[More details\]](#rate-command)                                                              |
| `ratings`      | `<jump-name>`                                       | Returns the average of all ratings for all keys from the specified jump and the amount of ratings per key                                                             |
| `top100`       |                                                     | Returns the list of the top 100 players, based off [this](https://docs.google.com/spreadsheets/d/1WLThhxpPawMfB-YhjRhuLi8GXLJvCxEqr9Own-77nyI/edit?usp=sharing) table |                                                                                                  |
| `donate`       |                                                     | Returns a link to Jumpedia's PayPal account, where people can donate, of which 100% flows directly into the bot's running costs                                       |


## Privileged Commands
Privileged commands cannot be executed by just anybody, but rather only by server admins, Jumpedia moderators or Jumpedia admins.<br>
Jumpedia moderators and especially Jumpedia admins are selected community members who are well trusted.<br>
At any time given, there are roughly 10-50 Jumpedia moderators and less than 10 Jumpedia admins.<br>

The following list shows who can execute which privileged commands:
- Server admins can only use `channelconf` to most of its full extent
- Jumpedia moderators can use every command besides `batch approve`, `batch nuke`, `genlists` and `backup`
- Jumpedia admins can use any command on ANY SERVER, as long as they have permission to type and Jumpedia is on that server, obviously<br><br>

| Privileged Command      | Arguments                               | Description                                                                                                                                                    |
|-------------------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `channelconf`           | `<configuration> [value]`               | Changes the channel's configuration to the specified value<br>[\[More details\]](#channelconf-command)                                                         |
| `batch list`            |                                         | Returns a link to a list of all existing batches and some of their metadata                                                                                    |
| `batch create`          | `<batch-name>`                          | Creates a new & empty batch with the specified name                                                                                                            |
| `batch add`             | `<batch-name> <jump-name> <*jump-data>` | Adds the specified jump and its data to the batch's add tab<br>[\[More details\]](#batch-add-command)                                                          |
| `batch edit`            | `<batch-name> <jump-name> <*jump-data>` | Adds the specified jump and its data to the batch's edit tab<br>[\[More details\]](#batch-edit-command)                                                        |
| `batch rem`             | `<batch-name> <jump-name>`              | Adds the specified jump to the batch's removals tab                                                                                                            |
| `batch forget`          | `<batch-name> <batch-tab> <jump-name>`  | Forgets the specified jump and its data from the batch's tab                                                                                                   |
| `batch info`            | `<batch-name>`                          | Returns all the information of the specified batch                                                                                                             |
| `batch log`             | `<batch-name>`                          | Returns all the logs of the specified batch                                                                                                                    |
| `batch download`        | `<batch-name>`                          | Returns a downloadable json-file of the batch's data                                                                                                           |
| `batch status`          | `<batch-name> [status]`                 | Changes the batch's status to the one specified<br>[\[More details\]](#batch-status-command)                                                                   |
| `batch approve`         | `<batch-name>`                          | Approves the batch specified and therefore implements all its changes into Jumpedia<br>[\[More details\]](#batch-approve-command)                              |
| `batch nuke`            | `<batch-name>`                          | Makes a batch completely immutable from that point onwards                                                                                                     |
| `genlists`<br>`genlist` |                                         | Generates updated lists in the pre-defined list channels in the Trickjump Database                                                                             |
| `backup`                |                                         | Creates a backup in the pre-defined backup channel in the SMO Trickjumping Server                                                                              |

## Detailed Command Information

### <a name="list-command">The `list` command</a>
The list command is a powerful tool that lets the user generate any kind of list of jumps they would desire with filters & sorts.<br>
The arguments need to be in the order `[*filters]` -> `[*sorts]` -> `[yield]`, but any of those arguments can be included or left out, depending on the needs.
If the target is not `all`, it will show information about when the user gave themselves the jump and the link to the proof.
For any [listable-attribute](#listable-attributes) it will check if at least one of the values matches the filter.

| Argument     | Explanation                                                                                                                                                                                                                                                                                                                                                                          | Example                                                                                                                                                               |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[target]`   | The target selects the base-list selected and can be one of 3 things:<br>- `all` to select all jumps in Jumpedia's database<br>- `mine` to select all jumps in the user's list<br>- A user's Discord ID to select all jumps in that user's list                                                                                                                                      | `!list all`<br>`!list mine`<br>`!list 679564566769827841`                                                                                                             |
| `[*filters]` | - To use any filters, start off with the keyword `only`<br>- Each filter is an argument pair of [user-attribute](#user-attributes) & [user-value](#user-values)<br>- Connect filters with the keyword `and` and jumps will need to fulfill all filters connected<br>- Connect and-groups with the keyword `or` and jumps will need to fulfill at least one and-group's requirements  | `!list all only kingdom metro`<br>`!list all only k metro`<br><br>`!list all only k metro and s main`<br>`!list all only k metro and s main or k snow and s database` |
| `[*sorts]`   | - To use any sorts, start off with the keyword `by`<br>- Each sort is a single argument with an [user-attribute](#user-attributes)<br>- List the sorts wanted from highest priority to lowest priority<br>- If multiple jumps have the same value for the first sort, that subset gets sorted by the second sort...                                                                  | `!list all by server`<br>`!list all by s`<br>`!list all by server kingdom finder`                                                                                     |
| `[yield]`    | The yield can be one of 3 things:<br>- `+` to show all attribute-values of jumps<br>- `-` to only show the most basic attribute-values of jumps<br>- Empty to only show the most basic attribute-values and the attribute-values used in filters & sorts                                                                                                                             | `!list all +`<br>`!list all -`<br>`!list all`                                                                                                                         |

| Special Case Examples                                                                                                                                                                        | Explanation                                                                                                                                                                                                                                      |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `!list all only tier main`<br>`!list all only diff elite`                                                                                                                                    | By using `main` as a value for the attribute `tier`/`diff` it will include all jumps from `diff` `0/10` to `10/10`<br>By using `elite` as a value for the attribute `tier`/`diff` it will allow all jumps from `diff` `Low Elite` to `Hell Tier` |
| `!list all only name vault`<br>`!list all only finder Joni`<br>`!list all only taser Mario`<br>`!list all only prover j`<br>`!list all only extra "how to"`<br>`!list all only link twitter` | For the attributes `name`, `finder`, `taser`, `prover`, `extra` & `link`<br>the value has to only be **contained** in the attribute's value                                                                                                      |
| `!list`                                                                                                                                                                                      | This is the short equivalent of `!list all`                                                                                                                                                                                                      |


### <a name="missing-command">The `missing` command</a>
The missing command is based off the [list command](#list-command) with a few minor differences:
- The target can only be `mine` or a user's Discord ID
- The base-list selected is all jumps in Jumpedia's database, reduced by all jumps the target has done and excluding unproven jumps

### <a name="rate-command">The `rate` command</a>
The rate command allows the user to rate jumps. There are multiple keys jumps can be rated by and those keys have different valid values. 

| Key     | Possible Values                                           | Examples                                                  |
|---------|-----------------------------------------------------------|-----------------------------------------------------------|
| `stars` | Any whole number from `1` to `5`                          | `1`<br>`2`<br>`5`                                         |
| `diff`  | Any user-value for the attribute `diff` except `Unproven` | `0`<br>`0/10`<br>`7/10`<br>`Insanity`<br>`Insanity Elite` |

### <a name="channelconf-command">The `channelconf` command</a>
The channelconf command lets the user change certain configurations (settings) of a channel.<br>
Listed below are all the possible values for each configuration:

| Values for `commands` | Alternatives     | Description                                                     |
|-----------------------|------------------|-----------------------------------------------------------------|
| `none`                | `0`              | No commands but `channeltype` are allowed                       |
| `normal`              | `1`              | All [user commands](#user-commands) & `channeltype` are allowed |
| `moderation`          | `mods` `mod` `2` | All commands are allowed                                        |

| Values for `info` | Alternatives | Description                                                                                                                                                                                                   |
|-------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `short`           | `fast` `0`   | Enables the shorthand use of the `info` command by just entering the jump-name, without having to specify the command<br>In the shorthand form, the jump-name must be a perfect match                         |
| `long`            | `slow` `1`   | Requires to use the `info` command directly<br>The long command version finds the closest matching jump with a maximum [Levenshtein search distance](https://en.wikipedia.org/wiki/Levenshtein_distance) of 3 |



### <a name="batch-add-command">The `batch add` command</a>
The batch add command lets the user add jumps with their corresponding data to a batch. Therefore, when the batch gets approved, the specified jump will be added to Jumpedia's database.

To define one value for an attribute in `<*jump-data>` one must follow the following syntax:
1. [User-attribute](#user-attributes)
2. Colon (`:`) with no spaces before or after
3. [User-value](#user-values)
4. Optionally more [user-values](#user-values) if the [attribute is listable](#listable-attributes) by delimiting them with spaces<br>
Disclaimer: There is currently a bug with listable attributes that there cannot be more than one value if the values themselves contain colons (`:`). This makes things like adding multiple links (where colons are always included) impossible and will be fixed in a future update!

**Example:** `!batch add "DB Batch" "Toad's Path" location:Mushroom diff:Insanity server:DB links:"https://youtu.be/zd3WSKzVNVY" "https://youtu.be/3_ZgKgijX9M" finder:Wezly prover:Marci`

There are 5 attributes required to have a value assigned for any jump, which are `name`, `location`, `diff`, `server` & `links`, so these have to be defined.<br>
The value for the attribute `name` gets specified by `<jump-name>`, so it doesn't have to be entered.<br>
The value for the attribute `tier` cannot be specified, because it gets calculated automatically by the value of `diff`.<br>
If a value is left empty it will be ignored.


### <a name="batch-edit-command">The `batch edit` command</a>
The batch edit command lets the user add jump edits to a batch. Therefore, when the batch gets approved, the specified jump will be edited in Jumpedia's database. It uses the same syntax and basic rules as the [batch add command](#batch-add-command), with the following differences:
- Values that are left empty signify that the jump's value should be deleted entirely
- As long as the jump keeps values for the required attributes, as many or as few edits to the jump can be made (ex: `!batch edit "DB Batch" "Metro Impossible" extra:"This is a cool jump description"`)
- The value of the attribute `name` can be re-specified in the `<*jump-data>` section to signify that the jump's name should be changed to that new info


### <a name="batch-status-command">The `batch status` command</a>
The batch status command allows the user to change the batch's status, such that some rules about the batch itself change.<br>
If the batch itself contains illegal statements, setting the status to `finished` will not work and result in the errors and how to fix them being returned as a list. These "illegal" statements are simply jump additions, edits or removals that don't make any logical sense, such as e.g. removing a jump that doesn't even exist.

| Status       | Rule Changes                                                                                                                                                                                                                                        |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `finished`   | - Makes the batch immutable to any jump information changes, which includes the commands `batch add`, `batch edit`, `batch rem` & `batch forget`<br>- Allows the batch to be approved with the [batch approve command](#batch-approve-command) |
| `unfinished` | - Makes the batch mutable again<br>- Forbids the batch to be approved with the [batch approve command](#batch-approve-command)                                                                                                                          |


### <a name="batch-approve-command">The `batch approve` command</a>
The batch approve command is the final step of a successful batch.
**Once a batch is approved, it becomes completely immutable and all changes will instantly be implemented into Jumpedia's database!** The `genlists` command will also be executed automatically.

There are two conditions though:
1. The batch's status must be set to `finished`
2. No illegal jump data additions are contained in the batch (further explained in the info of the [batch status command](#batch-status-command))

Condition 2 is already checked when the jump's status gets set to `finished`, but is re-checked here for the case that in-between setting the status to `finished` and approving the batch, a different batch has interfered with the current batch's data




# Term explanation

### <a name="shell-like-syntax">Shell-Like Syntax</a>
When talking about shell-like syntax, we talk about how commands need to be input. The following rules apply:
| Rule                                                                                                                            | Example                                                                                                                                                              |
|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Arguments are delimited by spaces                                                                                               | `!list all only server main`<br> Between all words are spaces, so all words are individual arguments                                                                 |
| Quotation marks can be used to enclose an argument and don't get counted towards the argument itself                            | `!list all only kingdom "Metro Kingdom"`<br> `!list all only kingdom 'Metro Kingdom'`<br> "Metro Kingdom" is one argument, because it is enclosed in quotation marks |
| Special characters (spaces, quotation marks) can also be escaped, so counted as normal characters, by placing a `\` before them | `!list all only kingdom Metro\ Kingdom`<br> "Metro\ Kingdom" is one argument, because the space got escaped                                                          |

The recommended way to input arguments is to...
- ... use double quotation marks (`"`) around any argument with multiple words or around words with single quotation marks (`'`) in them
- ... escape double quotation marks (`"`) with a backslash (`\`) if they appear in the argument themselves


### <a name="user-attributes">User-Attributes</a>
Each jump has multiple attributes, which are simply `name`, `location`, `server`, `link`, ...<br>
When dealing with jump data (for example on the `list` command), to reference certain attributes of a jump, you can use alternative ways to reference attributes:
| Attribute  | User-Attributes                                             |
|------------|-------------------------------------------------------------|
| `name`     | `n`                                                         |
| `location` | `kingdom` `loc` `k`                                         |
| `diff`     | `difficulty` `d`                                            |
| `tier`     | `t`                                                         |
| `type`     | `ty`                                                        |
| `finder`   | `find` `founder` `found` `f`                                |
| `taser`    | `tased` `tas`                                               |
| `prover`   | `proved` `p`                                                |
| `server`   | `s`                                                         |
| `extra`    | `desc` `description` `ex` `e` `info` `i` `rules` `rule` `r` |
| `links`    | `link` `l`                                                  |

See also: [User-Values](#user-values)

### <a name="user-values">User-Values</a>
Like mentioned in the term explanation of [user-attributes](#user-attributes), each jump has attributes.<br>
For those attributes, each jump has their own values, so for example the jump `Metro Impossible` has the value `0.5/10` for the attribute `diff`.
**No user-values are case-sensitive**, so all valid examples below could be capitalized in any way and they **would still be valid**!
Make sure to read about [listable-attributes](#listable-attributes) to understand some parts of the table better!

| Attribute                       | User-Value Rules                                                                                                                                                                                                                             | Valid examples                                                                                    |
|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `name`                          | Anything below or equal to 100 characters in length is valid                                                                                                                                                                                 | `Cool Name indeed`                                                                                |
| `location`                      | - The first location must be a valid kingdom or the first word of a valid kingdom<br>- `Bowsers Kingdom` is seen like `Bowser's Kingdom`<br>- `Odyssey` is a valid kingdom (for any jumps that work in most kingdoms or are Odyssey related) | `Metro Kingdom`<br>`Metro`<br>`Bowser's`<br>`Bowsers`<br>`Dark Side`<br>`Dark`<br>`Odyssey`       |
| `diff`                          | - Any difficulty in the format of `x/10` or just `x` where `x` is any number from `0` to `10` in `0.5` steps<br>- Any elite difficulty with the word `Elite` or `Tier` removed<br>- `Unproven` is a valid difficulty                         | `0/10`<br>`5.5/10`<br>`5.5`<br>`7`<br>`Low Elite`<br>`Low`<br>`Hell Tier`<br>`Hell`<br>`Unproven` |
| `tier`                          | - Any tier with the word `Elite` or `Tier` removed<br>- `Unproven` is a valid tier                                                                                                                                                           | `Beginner`<br>`Expert`<br>`Practice Tier`<br>`Practice`<br>`High Elite`<br>`High`<br>`Unproven`   |
| `type`                          | No rules (planned for the future)                                                                                                                                                                                                            | `Anything`                                                                                        |
| `finder`<br>`taser`<br>`prover` | No rules                                                                                                                                                                                                                                     | `Anything`                                                                                        |
| `server`                        | Must be **contained** in any of the server user-values, which are:<br>- `SMO Trickjumping Server` `Main Trickjumping Server` `Main Trickjump Server` `Main Server`<br>- `Database` `The Trickjump Database` `Database Server` `DB`           | `Main Server`<br>`Main`<br>`D`<br>`SMO`                                                           |
| `extra`                         | No rules                                                                                                                                                                                                                                     | `Anything`                                                                                        |
| `links`                         | - Must start with `https://` if the link has to be valid (for example for the proof of a jump)<br>- No rules if the link doesn't have to be valid (for example when using the `list` command to search if a keyword is contained)            | `https://x.com/JoniKauf/status/1651344903790796800?s=20`<br>`twitter` (only if case 2)            |

### <a name="listable-attributes">Listable Attributes</a>
Listable attributes are all attributes that can have more than a single value. For example, a jump can only have one specific & unique name but could have multiple links to show off different ways to do the jump.
All listable attributes are:
- `location`, `type`, `finder`, `taser`, `prover`, `extra` & `links`

Therefore, all non-listable attributes are:
- `name`, `diff`, `tier` & `server`


# Credit
Here is a list of all people who actively supported me or this project and therefore made it possible!<br>
I am grateful for every single one of them, so please contact me via discord (@jonikauf) if you think somebody is missing from this list!

*A big THANK YOU to:*
- **The Main Server & Database team** for actively updating, improving and cleaning Jumpedia's Database with their batches and for helping me debug & fix the development version, before it releases
- **Gummy & TheAmazingRaptor** for putting an enormous amount of time & effort into the Database & Main Server and managing them
- **Xeter** for helping me host the bot on a server and generally being supportive of the project
- **Ninjapugs** for the Jumpedia profile picture
- **The countless suggesters** who gave me many awesome ideas to improve the bot even further
- **Every single Jumpedia user**, because without their interest this project would be meaningless and their use of the bot also helps me find further bugs
