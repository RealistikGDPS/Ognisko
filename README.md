# Ognisko 🔥
![Geometry Dash Version - 2.201](https://img.shields.io/badge/Geometry_Dash_Version-2.201-red)

The Geometry Dash-facing backend for RealistikGDPS.

**Note that this branch does not work at this moment. Please use the `stable` branch for deployments.**

## What is this?
This is essentially the service with which the Geometry Dash client communicates directly. It is responsible for
handling requests directly from the Geometry Dash client and returning responses in the format the client expects.

This is **just** the backend. For more functionality, consult the full [deployment](https://github.com/RealistikGDPS/deployment).


## Requirements
While Docker should handle all of this, in cases where you are running this standalone, here are the requirements:
### Software and Hardware
- Python 3.12 (we are leveraging new language features).
