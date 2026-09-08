# Additional synthetic Author source

`when-two-rows.sgl` is a distinct synthetic final Author snapshot used to verify homogeneous two-row When projection and pruning. It retains the nested Decision Table facts and original input/result cells from the historical `when-key-a` example, but this fixture's Author has explicitly decided to omit the schema-incompatible Discount assertion and has frozen the same initial Discount=0 setup in both Scenarios. The first Scenario retains DTA_BEFORE; the second uses an ordinary SETUP carrier. Its final trace and counts record that different Author decision.

This is test-source construction, never a Generator repair. Generator must reject the unsupported non-cell ASSERT in the unchanged historical `fixtures/s3/profiled/when-key-a.sgl`; it cannot perform these semantic changes. The seven reviewed DEC-027 sources remain unchanged.
