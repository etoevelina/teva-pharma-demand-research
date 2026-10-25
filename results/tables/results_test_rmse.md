| model                                |         A |         B |         C |         D |        D1 |         N |
|:-------------------------------------|----------:|----------:|----------:|----------:|----------:|----------:|
| Zero forecast (reference)            |   nan     | 33338.313 | 30095.713 | 30095.713 | 30095.713 |  8818.950 |
| Naive (last month)                   |  9742.236 |   nan     |   nan     |   nan     |   nan     |   nan     |
| Seasonal naive                       | 11827.865 |   nan     |   nan     |   nan     |   nan     |   nan     |
| Moving average (12)                  |  9351.441 |   nan     |   nan     |   nan     |   nan     |   nan     |
| Global mean                          |   nan     | 32563.009 | 29413.839 | 29420.707 | 29401.662 |  9560.586 |
| Form mean                            |   nan     | 32427.494 | 29304.638 | 29381.001 | 29375.017 |  9459.025 |
| Hierarchical group mean              |   nan     | 33190.218 | 29656.772 | 29457.510 | 29358.042 | 18076.798 |
| Hierarchical group median            |   nan     | 32522.879 | 29626.879 | 29804.437 | 29799.064 | 10062.715 |
| Launch-age mean                      |   nan     |   nan     |   nan     |   nan     |   nan     |  8438.530 |
| CatBoost, no INN/ATC                 | 13019.852 | 32524.556 | 29202.897 | 29276.238 | 29455.253 |  8351.088 |
| CatBoost, INN only                   | 13542.434 | 31857.288 | 29122.310 | 29240.812 | 29524.288 |  8104.200 |
| CatBoost, ATC only                   | 17968.883 | 32043.874 | 29130.464 | 29283.963 | 29449.640 |  8222.240 |
| CatBoost, INN + ATC                  | 12358.853 | 31827.365 | 29125.315 | 29254.800 | 29422.790 |  8170.577 |
| CatBoost, INN + ATC + category codes | 15397.833 | 31766.799 |   nan     |   nan     |   nan     |   nan     |
