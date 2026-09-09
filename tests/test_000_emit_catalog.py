import unittest

from tools.build_catalog import build_catalog, render_catalog


class CatalogBootstrapEmission(unittest.TestCase):
    def test_emit_generated_catalog_for_pr_bootstrap(self) -> None:
        print("CATALOG_BOOTSTRAP_BEGIN")
        print(render_catalog(build_catalog()), end="")
        print("CATALOG_BOOTSTRAP_END")


if __name__ == "__main__":
    unittest.main()
