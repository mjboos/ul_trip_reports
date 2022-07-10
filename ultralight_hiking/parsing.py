from dataclasses import dataclass, fields, asdict
import pandas as pd
from typing import List, Optional, Callable, Mapping, Generator, Dict
from bs4.element import Tag
from functools import partial


@dataclass(frozen=True)
class Item:
    name: str
    description: str
    price: str
    weight_g: float
    quantity: float


def get_lp_items(
    lp_link: str,
    category_type="ul",
    category_class="lpItems lpDataTable",
    parser: str = "html.parser",
) -> pd.DataFrame:
    import requests
    from bs4 import BeautifulSoup

    page = requests.get(lp_link)
    if page.status_code == 400:  # bad url or list is gone
        return None
    soup = BeautifulSoup(page.content, features=parser)
    categories = [
        parse_category(category)
        for category in soup.find_all(category_type, {"class": category_class})
    ]
    return categories_to_df(categories)


def categories_to_df(categories: List[dict]) -> pd.DataFrame:
    dfs = []
    for category in categories:
        df = pd.DataFrame([asdict(item) for item in category["items"]])
        dfs.append(df.assign(category=category["category"]))
    return pd.concat(dfs, ignore_index=True)


convert_to_gram = {"lb": 453.59, "oz": 28.35, "g": 1, "kg": 1000}


def extract_weight_in_gram(
    item: Tag, weight_class: str = "lpWeight", unit_select_class: str = "lpUnitSelect"
) -> float:
    unit = (
        item.find_next("div", {"class": unit_select_class})
        .find_next("option", selected=True)
        .contents[0]
    )
    weight = generic_extract_item_property(item, weight_class, conversion_func=float)
    return convert_to_gram[unit] * weight


def generic_extract_item_property(
    item: Tag, class_name: str, conversion_func: Callable = str, html_type: str = "span"
):
    try:
        content_list = item.find_next(html_type, {"class": class_name}).contents
        content = next(iterate_nested_content(content_list), None)
        return conversion_func(content) if content else content
    except AttributeError:  # empty item/this element is missing
        return None


generic_extract_spans: Dict[str, Callable] = {
    "name": partial(generic_extract_item_property, class_name="lpName"),
    "description": partial(generic_extract_item_property, class_name="lpDescription"),
    "price": lambda x: float(res.strip("$£€"))
    if (res := generic_extract_item_property(x, class_name="lpPriceCell lpNumber"))
    else res,
    "weight_g": extract_weight_in_gram,
    "quantity": partial(
        generic_extract_item_property,
        class_name="lpQtyCell lpNumber",
        conversion_func=float,
    ),
}


def parse_item(
    item: Tag,
    extract_spans: Optional[Mapping[str, Callable]] = None,
) -> Item:
    if extract_spans is None:  # out of function
        extract_spans = generic_extract_spans

    return Item(
        **{
            var_name: extract_spans[var_name](item)
            for var_name, span_name in extract_spans.items()
        }
    )


def parse_category(category_bs: Tag, item_css_sel: str = "li[class^=lpItem]"):
    try:
        category_name = (
            category_bs.find_next("h2", {"class": "lpCategoryName"}).contents[0].strip()
        )
    except IndexError:  # there was no category name
        category_name = ""
    return {
        "category": category_name,
        "items": [parse_item(item) for item in category_bs.select(item_css_sel)],
    }


def iterate_nested_content(contents: list) -> Generator[str, None, None]:
    for content in contents:
        # necessary because we else have nested exceptions
        if isinstance(content, str):
            stripped_content = content.strip()
            if stripped_content:  # only yield if it contains more than a newline/space
                yield stripped_content
        else:  # we found a nested structure
            for sub_content in iterate_nested_content(content.contents):
                yield sub_content
