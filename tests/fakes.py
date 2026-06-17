from shared import CATEGORY_CATALOG, CATEGORY_SEARCH, DETAILS, PRODUCTS


class FakeImgGenerator:
    async def generate_product_variants(self, img: bytes) -> dict[str, bytes]:
        return {PRODUCTS: b"fake_small_bytes", DETAILS: b"fake_medium_bytes"}

    async def generate_category_variants(self, img: bytes) -> dict[str, bytes]:
        return {
            CATEGORY_CATALOG: b"fake_small_bytes",
            CATEGORY_SEARCH: b"fake_medium_bytes",
        }
