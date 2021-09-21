from bidict import bidict
import pandas as pd
import us

states = bidict({k.fips: k.abbr for k in us.states.STATES})
