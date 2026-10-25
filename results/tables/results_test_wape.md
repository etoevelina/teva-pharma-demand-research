| model                                |       A |       B |       C |       D |      D1 |       N |
|:-------------------------------------|--------:|--------:|--------:|--------:|--------:|--------:|
| Zero forecast (reference)            | nan     |   1.000 |   1.000 |   1.000 |   1.000 |   1.000 |
| Naive (last month)                   |   0.298 | nan     | nan     | nan     | nan     | nan     |
| Seasonal naive                       |   0.397 | nan     | nan     | nan     | nan     | nan     |
| Moving average (12)                  |   0.324 | nan     | nan     | nan     | nan     | nan     |
| Global mean                          | nan     |   1.325 |   1.387 |   1.383 |   1.380 |   2.620 |
| Form mean                            | nan     |   1.303 |   1.351 |   1.346 |   1.337 |   2.501 |
| Hierarchical group mean              | nan     |   1.313 |   1.277 |   1.340 |   1.336 |   2.999 |
| Hierarchical group median            | nan     |   1.001 |   0.994 |   0.967 |   0.967 |   1.474 |
| Launch-age mean                      | nan     | nan     | nan     | nan     | nan     |   1.169 |
| CatBoost, no INN/ATC                 |   0.339 |   1.119 |   1.211 |   1.220 |   1.251 |   0.960 |
| CatBoost, INN only                   |   0.314 |   1.068 |   1.198 |   1.198 |   1.272 |   0.927 |
| CatBoost, ATC only                   |   0.333 |   1.033 |   1.089 |   1.211 |   1.264 |   0.927 |
| CatBoost, INN + ATC                  |   0.302 |   1.053 |   1.069 |   1.200 |   1.246 |   0.933 |
| CatBoost, INN + ATC + category codes |   0.330 |   1.132 | nan     | nan     | nan     | nan     |
