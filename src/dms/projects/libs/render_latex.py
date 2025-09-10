from typing import Any

import pandoc
from langdetect import detect
from pylatex import Command, Document, Itemize, Section, Subsection
from pylatex.package import Package


def get_title_text(title_obj: Any, lang: str = "default") -> str:
    """Extract title text from title object, supporting multiple languages."""
    if isinstance(title_obj, dict):
        return title_obj.get(lang, title_obj.get("default", ""))
    return str(title_obj) if title_obj else ""


def render_element_content(
    doc: Document,
    element: dict[str, Any],
    result_data: dict[str, Any],
    lang: str = "default",
) -> None:
    """Render content for a single form element based on its type and result data."""
    element_name = element.get("name")
    element_type = element.get("type")
    element_title = get_title_text(element.get("title", element_name), lang)

    if element_name not in result_data:
        return

    value = result_data[element_name]

    if element_type == "text":
        with doc.create(Subsection(element_title)):
            doc.append(str(value))

    elif element_type == "comment":
        with doc.create(Subsection(element_title)):
            doc.append(str(value))

    elif element_type == "boolean":
        with doc.create(Subsection(element_title)):
            bool_value = "Yes" if value else "No"
            doc.append(bool_value)

            # Handle comment area for boolean fields
            if (
                element.get("showCommentArea")
                and f"{element_name}-Comment" in result_data
            ):
                comment = result_data[f"{element_name}-Comment"]
                if comment:
                    doc.append(f"\n\nNotes: {comment}")

    elif element_type == "tagbox":
        with doc.create(Subsection(element_title)):
            if isinstance(value, list):
                doc.append(", ".join(str(v) for v in value))
            else:
                doc.append(str(value))

            # Handle comment area for tagbox fields
            if (
                element.get("showCommentArea")
                and f"{element_name}-Comment" in result_data
            ):
                comment = result_data[f"{element_name}-Comment"]
                if comment:
                    doc.append(f"\n\nNotes: {comment}")

    elif element_type == "paneldynamic":
        with doc.create(Subsection(element_title)):
            if isinstance(value, list):
                for i, item in enumerate(value, 1):
                    with doc.create(Subsection(f"{element_title} {i}")):
                        render_panel_dynamic_item(doc, element, item, lang)


def render_panel_dynamic_item(
    doc: Document,
    panel_element: dict[str, Any],
    item_data: dict[str, Any],
    lang: str = "default",
) -> None:
    """Render a single item from a paneldynamic element."""
    template_elements = panel_element.get("templateElements", [])

    with doc.create(Itemize()) as itemize:
        for template_elem in template_elements:
            elem_name = template_elem.get("name")
            elem_title = get_title_text(template_elem.get("title", elem_name), lang)
            elem_type = template_elem.get("type")

            if elem_name not in item_data:
                continue

            value = item_data[elem_name]

            if elem_type == "boolean":
                bool_value = "Yes" if value else "No"
                itemize.add_item(f"{elem_title}: {bool_value}")

                # Handle comment for boolean in panel
                if (
                    template_elem.get("showCommentArea")
                    and f"{elem_name}-Comment" in item_data
                ):
                    comment = item_data[f"{elem_name}-Comment"]
                    if comment:
                        itemize.add_item(f"{elem_title} Notes: {comment}")

            elif elem_type == "tagbox":
                if isinstance(value, list):
                    itemize.add_item(
                        f"{elem_title}: {', '.join(str(v) for v in value)}"
                    )
                else:
                    itemize.add_item(f"{elem_title}: {value}")

            else:
                itemize.add_item(f"{elem_title}: {value}")


def render_page_content(
    doc: Document,
    page: dict[str, Any],
    result_data: dict[str, Any],
    lang: str = "default",
) -> None:
    """Render content for a single page"""
    page_title = get_title_text(page.get("title", page.get("name", "Section")), lang)

    with doc.create(Section(page_title)):
        # Add page description if available
        if page.get("description"):
            page_desc = get_title_text(page["description"], lang)
            doc.append(f"{page_desc}\n\n")

        # Render each element in the page
        for element in page.get("elements", []):
            if element.get("type") == "panel":
                # Handle panel elements (like license warnings)
                continue
            elif element.get("type") == "html":
                # Skip HTML elements in PDF output
                continue
            else:
                render_element_content(doc, element, result_data, lang)


def render_to_tex(
    dmp_template: dict,
    result_data: dict,
) -> None:
    """
    Create a data management plan document using pylatex
    """

    # Detect language from result data
    detected_lang = detect(
        "\n".join([v for k, v in result_data.items() if isinstance(v, str)])
    )

    geometry_options = {"margin": "1in"}
    doc = Document(geometry_options=geometry_options)

    # Set babel language based on detected language
    babel_lang = "norsk" if detected_lang == "no" else "english"
    doc.packages.append(Package("babel", options=[babel_lang]))
    doc.packages.append(Package("inputenc", options=["utf8"]))

    # Set document title from DMS structure using detected language
    doc_title = get_title_text(
        dmp_template.get("title", "Data Management Plan"), detected_lang
    )
    doc.preamble.append(Command("title", doc_title))
    doc.preamble.append(Command("author", "NINA"))
    doc.preamble.append(Command("date", Command("today")))
    doc.append(Command("maketitle"))

    # Render each page from the DMS structure using detected language
    for page in dmp_template.get("pages", []):
        render_page_content(doc, page, result_data, detected_lang)

    return doc.dumps()


def render_to_format(
    dmp_template: dict,
    result_data: dict,
    output_format: str = "html",
):
    latex_content = render_to_tex(dmp_template, result_data)
    if format == "latex":
        return latex_content
    doc = pandoc.read(latex_content, format="latex")
    return pandoc.write(doc, format=output_format)
