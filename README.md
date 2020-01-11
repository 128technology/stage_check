# Stage_check

Welcome to the 128 Technology  stage_check public repository.  

Stage check is a tool used to diagnose and / or check the health of  128 Technology routers (the tool was initially used to determine if router and its environment were properly configured to transition from a pre-deployment to the deployment stage, hence the name).

Ideally stage check should be built on a recent Linux distribution with the fiollowing packages installed:
- git
- python36
- tox

This tool is distributed as a python pex file, a self extracting binary which when executed, creates a dedicated python virtual environment and installs the required modules.  

To create this file, from the top level directory run ./make_pex, which will run some unit tests and the construct the pex file.  The result, stage_check.pex, can be found at:

**build_stage_check/stage_check/stage_check.pex**

The repo directory structure is listed below.  See **stage_check/README.md** for more information.

## Directory Structure:

```
repo-root
  |-make_pex
  +-stage_check { currently the only project }
    |-setup.py
    |-requirements.py
    |-tox.ini
    +-stage_check
      |-{ source files }
    +-tests
      |-{unit tests }
  +-build_stage_check 
      +-stage_check
        |-stage_check.pex { ** stage_check self-extracting binary ** }
        +-stage_check
          |- { copy of sources }
        +-{ build artifacts }
  +- future_project { some future project }
      :
  +- build_future_project { build artifacts
```