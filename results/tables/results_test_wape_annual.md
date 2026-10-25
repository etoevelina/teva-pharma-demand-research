| model                                |       A |       B |       C |       D |      D1 |       N |
|:-------------------------------------|--------:|--------:|--------:|--------:|--------:|--------:|
| Zero forecast (reference)            | nan     |   1.000 |   1.000 |   1.000 |   1.000 |   1.000 |
| Naive (last month)                   |   0.256 | nan     | nan     | nan     | nan     | nan     |
| Seasonal naive                       |   0.259 | nan     | nan     | nan     | nan     | nan     |
| Moving average (12)                  |   0.259 | nan     | nan     | nan     | nan     | nan     |
| Global mean                          | nan     |   1.303 |   1.364 |   1.360 |   1.358 |   2.548 |
| Form mean                            | nan     |   1.281 |   1.328 |   1.323 |   1.315 |   2.409 |
| Hierarchical group mean              | nan     |   1.286 |   1.253 |   1.317 |   1.315 |   2.888 |
| Hierarchical group median            | nan     |   0.978 |   0.980 |   0.958 |   0.959 |   1.391 |
| Launch-age mean                      | nan     | nan     | nan     | nan     | nan     |   1.129 |
| CatBoost, no INN/ATC                 |   0.288 |   1.104 |   1.197 |   1.206 |   1.236 |   0.922 |
| CatBoost, INN only                   |   0.257 |   1.052 |   1.183 |   1.184 |   1.257 |   0.886 |
| CatBoost, ATC only                   |   0.290 |   1.019 |   1.075 |   1.196 |   1.249 |   0.889 |
| CatBoost, INN + ATC                  |   0.257 |   1.037 |   1.055 |   1.185 |   1.232 |   0.895 |
| CatBoost, INN + ATC + category codes |   0.286 |   1.116 | nan     | nan     | nan     | nan     |
