| model                                |       A |       B |       C |       D |      D1 |       N |
|:-------------------------------------|--------:|--------:|--------:|--------:|--------:|--------:|
| Zero forecast (reference)            | nan     | nan     | nan     | nan     | nan     | nan     |
| Naive (last month)                   |   0.959 | nan     | nan     | nan     | nan     | nan     |
| Seasonal naive                       |   0.935 | nan     | nan     | nan     | nan     | nan     |
| Moving average (12)                  |   0.935 | nan     | nan     | nan     | nan     | nan     |
| Global mean                          | nan     |  -0.015 |  -0.027 |  -0.054 |  -0.069 |   0.358 |
| Form mean                            | nan     |   0.171 |   0.180 |   0.149 |   0.145 |   0.490 |
| Hierarchical group mean              | nan     |   0.350 |   0.238 |   0.134 |   0.151 |   0.544 |
| Hierarchical group median            | nan     |   0.346 |   0.282 |   0.200 |   0.133 |   0.511 |
| Launch-age mean                      | nan     | nan     | nan     | nan     | nan     |   0.358 |
| CatBoost, no INN/ATC                 |   0.957 |   0.268 |   0.190 |   0.161 |   0.096 |   0.599 |
| CatBoost, INN only                   |   0.961 |   0.385 |   0.226 |   0.185 |   0.124 |   0.655 |
| CatBoost, ATC only                   |   0.961 |   0.384 |   0.311 |   0.205 |   0.070 |   0.682 |
| CatBoost, INN + ATC                  |   0.961 |   0.392 |   0.334 |   0.216 |   0.122 |   0.667 |
| CatBoost, INN + ATC + category codes |   0.960 |   0.367 | nan     | nan     | nan     | nan     |
