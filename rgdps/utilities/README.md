# RealistikGDPS Utilities
These utilities are programs that are separate from the main RealistikGDPS instance but share code and logic
with it.


## GMDPrivateServer Migrator
`gmdps_converter.py` is a tool that aims to convert a GMDPrivateServer styled database for use in the current
RealistikGDPS instance.

### Usage

```sh
python3.10 gmdps_converter.py <old_db>
```
Where:
- old_db is the name of the old database in MySQL (make sure the current user can access it)
