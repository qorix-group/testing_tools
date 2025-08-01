load("@rules_rust//rust:defs.bzl", "rust_library", "rust_test")
load("@test_scenarios_rust_crates//:defs.bzl", "all_crate_deps")

rust_library(
    name = "test_scenarios_rust",
    srcs = glob(["src/**/*.rs"]),
    visibility = ["//visibility:public"],
    deps = all_crate_deps(normal = True),
)

rust_test(
    name = "tests",
    crate = ":test_scenarios_rust",
    visibility = ["//visibility:private"],
    deps = all_crate_deps(normal = True),
)
