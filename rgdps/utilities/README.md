# RealistikGDPS Utilities
These utilities are programs that are separate from the main RealistikGDPS instance but share code and logic
with it.


## GMDPrivateServer Migrator
`gmdps_converter.py` is a tool that aims to convert a GMDPrivateServer styled database for use in the current
RealistikGDPS instance.

### Usage
#### Using the Docker setup
```sh
make converter
```

#### Standalone
```sh
python3.10 gmdps_converter.py
```

### Note
To avoid increasing the complexity of the rest of the codebase, the converter makes the following assumptions regarding your configuration:
- The root user is available and has the same password as the main MySQL (already the case if using the docker setup)
- Your old database is named `old_gdps`.

Additionally, the converter will skip converting any table that is not empty. This means that if you have any users registered, no users
will be converted from the old database. This is a deliberate choice to prevent the difficulties that come with merging users.
