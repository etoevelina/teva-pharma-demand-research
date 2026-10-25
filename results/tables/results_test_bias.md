| model                                |       A |       B |       C |       D |      D1 |       N |
|:-------------------------------------|--------:|--------:|--------:|--------:|--------:|--------:|
| Zero forecast (reference)            | nan     |  -1.000 |  -1.000 |  -1.000 |  -1.000 |  -1.000 |
| Naive (last month)                   |   0.066 | nan     | nan     | nan     | nan     | nan     |
| Seasonal naive                       |   0.013 | nan     | nan     | nan     | nan     | nan     |
| Moving average (12)                  |   0.013 | nan     | nan     | nan     | nan     | nan     |
| Global mean                          | nan     |   0.016 |   0.114 |   0.105 |   0.105 |   1.654 |
| Form mean                            | nan     |   0.018 |   0.097 |   0.059 |   0.038 |   1.651 |
| Hierarchical group mean              | nan     |   0.092 |  -0.086 |   0.040 |   0.043 |   2.471 |
| Hierarchical group median            | nan     |  -0.572 |  -0.679 |  -0.787 |  -0.801 |   0.219 |
| Launch-age mean                      | nan     | nan     | nan     | nan     | nan     |  -0.338 |
| CatBoost, no INN/ATC                 |  -0.058 |  -0.270 |  -0.130 |  -0.124 |  -0.116 |  -0.638 |
| CatBoost, INN only                   |   0.021 |  -0.273 |  -0.139 |  -0.152 |  -0.075 |  -0.597 |
| CatBoost, ATC only                   |  -0.042 |  -0.360 |  -0.311 |  -0.138 |  -0.098 |  -0.649 |
| CatBoost, INN + ATC                  |  -0.047 |  -0.299 |  -0.342 |  -0.148 |  -0.111 |  -0.627 |
| CatBoost, INN + ATC + category codes |  -0.087 |  -0.152 | nan     | nan     | nan     | nan     |
