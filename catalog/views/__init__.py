from .hub import catalog_hub

from .pools import (
    pool_list,
    pool_create,
    pool_detail,
    pool_update,
    pool_delete,
)

from .heating import (
    heating_list,
    heating_create,
    heating_delete,
    heating_detail,
    heating_update,
)

from .waterfall import (
    waterfall_list,
    waterfall_create,
    waterfall_detail,
    waterfall_update,
    waterfall_delete,
)

from .lighting import(
    lighting_detail,
    lighting_update,
)

from .water_treatment import(
    treatment_detail,
    treatment_update,
)